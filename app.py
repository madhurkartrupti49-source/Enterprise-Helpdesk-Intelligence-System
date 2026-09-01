# ============================================================
# AI ENTERPRISE HELPDESK
# COMPLETE END-TO-END STREAMLIT APPLICATION
# ============================================================

import streamlit as st
import pandas as pd
import sqlite3
import smtplib
import uuid
import os
import re
import joblib

from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from company_config import COMPANY_NAME, TEAM_EMAILS


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=f"{COMPANY_NAME} - AI Enterprise Helpdesk",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CONSTANTS
# ============================================================

DB_PATH = "helpdesk.db"

DEFAULT_TEAMS = {
    "Network Team": "network-team@company.com",
    "Application Support": "application-team@company.com",
    "Desktop Support": "desktop-team@company.com",
    "Security Team": "security-team@company.com",
    "Email/Collab Team": "email-team@company.com",
}

CATEGORIES = [
    "VPN",
    "Email",
    "Laptop",
    "Outlook",
    "Wi-Fi",
    "Internet",
    "Printer",
    "Password/Login",
    "Microsoft Teams",
    "Browser",
    "Software",
]


# ============================================================
# CATEGORY INFORMATION
# ============================================================

CATEGORY_INFO = {

    "VPN": {
        "team": "Network Team",
        "troubleshooting": [
            "Check whether your internet connection is working properly.",
            "Disconnect VPN and reconnect using your corporate VPN credentials.",
            "Restart the VPN application and try connecting again.",
            "Restart the laptop and reconnect to the VPN.",
        ],
    },

    "Email": {
        "team": "Email/Collab Team",
        "troubleshooting": [
            "Check your internet connection and try sending the email again.",
            "Verify that the recipient email address is correct.",
            "Refresh the mailbox and check whether new messages are loading.",
            "Sign out of your email account and sign in again.",
        ],
    },

    "Outlook": {
        "team": "Email/Collab Team",
        "troubleshooting": [
            "Close Outlook completely and open it again.",
            "Check your internet connection and verify Outlook connectivity.",
            "Restart the laptop and launch Outlook again.",
            "Sign out and sign in again using your corporate account.",
        ],
    },

    "Laptop": {
        "team": "Desktop Support",
        "troubleshooting": [
            "Restart the laptop and check whether the issue is resolved.",
            "Disconnect unnecessary external devices and try again.",
            "Check whether the laptop has sufficient battery/power.",
            "Restart the system and verify the issue again.",
        ],
    },

    "Wi-Fi": {
        "team": "Network Team",
        "troubleshooting": [
            "Turn Wi-Fi off and turn it on again.",
            "Forget the corporate Wi-Fi network and reconnect.",
            "Restart the laptop and reconnect to Wi-Fi.",
            "Check whether other devices can connect to the same network.",
        ],
    },

    "Internet": {
        "team": "Network Team",
        "troubleshooting": [
            "Check whether the network cable or Wi-Fi connection is active.",
            "Restart the router/network connection if applicable.",
            "Disconnect and reconnect to the network.",
            "Restart the laptop and test internet connectivity again.",
        ],
    },

    "Printer": {
        "team": "Desktop Support",
        "troubleshooting": [
            "Check whether the printer is powered on.",
            "Verify that the printer is connected to the correct network.",
            "Remove stuck documents from the print queue.",
            "Restart the printer and try printing again.",
        ],
    },

    "Password/Login": {
        "team": "Security Team",
        "troubleshooting": [
            "Verify that Caps Lock is not enabled.",
            "Check whether the username is correct.",
            "Try signing in again after carefully entering your credentials.",
            "Use the official password reset process if your password is expired.",
        ],
    },

    "Microsoft Teams": {
        "team": "Application Support",
        "troubleshooting": [
            "Close Microsoft Teams and open it again.",
            "Check your internet connection.",
            "Sign out of Teams and sign in again.",
            "Restart the laptop and test Teams again.",
        ],
    },

    "Browser": {
        "team": "Application Support",
        "troubleshooting": [
            "Refresh the webpage.",
            "Clear browser cache and cookies.",
            "Try opening the website in another supported browser.",
            "Restart the browser and test the website again.",
        ],
    },

    "Software": {
        "team": "Application Support",
        "troubleshooting": [
            "Close the application and open it again.",
            "Restart the laptop and launch the application.",
            "Check whether the application has pending updates.",
            "Try running the application again after restarting the system.",
        ],
    },
}


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION = {
    "page": "Dashboard",

    "chatbot_active": False,
    "chatbot_category": "",
    "chatbot_issue": "",
    "chatbot_step": 0,
    "chatbot_history": [],
    "chatbot_escalated": False,
    "chatbot_escalation_message": "",
    "active_ticket": None,

    "admin_logged_in": False,
}

for key, value in DEFAULT_SESSION.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def initialize_database():

    conn = get_connection()
    cur = conn.cursor()

    # --------------------------------------------------------
    # Teams
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            team_email TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # Tickets
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            created_at TEXT,
            resolved_at TEXT,
            category TEXT,
            issue TEXT,
            priority TEXT,
            status TEXT,
            team TEXT,
            resolution_time_hrs REAL DEFAULT 0,
            stage TEXT,
            escalated INTEGER DEFAULT 0
        )
    """)

    # --------------------------------------------------------
    # Troubleshooting History
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS troubleshooting_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT,
            speaker TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # Seed Teams
    # --------------------------------------------------------

    merged_teams = dict(DEFAULT_TEAMS)

    try:
        merged_teams.update(TEAM_EMAILS)
    except Exception:
        pass

    for team, email in merged_teams.items():

        cur.execute("""
            INSERT OR IGNORE INTO teams
            (team_name, team_email, created_at)
            VALUES (?, ?, ?)
        """, (
            team,
            email,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()
    conn.close()


initialize_database()


# ============================================================
# TEAM FUNCTIONS
# ============================================================

def get_all_teams():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM teams
        ORDER BY team_name
    """, conn)

    conn.close()

    return df


def get_team_email(team):

    conn = get_connection()

    row = conn.execute("""
        SELECT team_email
        FROM teams
        WHERE team_name = ?
    """, (team,)).fetchone()

    conn.close()

    if row:
        return row[0]

    return "Not configured"


def update_team_email(team, email):

    conn = get_connection()

    conn.execute("""
        UPDATE teams
        SET team_email = ?
        WHERE team_name = ?
    """, (email, team))

    conn.commit()
    conn.close()


# ============================================================
# TICKET FUNCTIONS
# ============================================================

def create_ticket(category, issue, priority=None):

    ticket_id = "HD-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(uuid.uuid4())[:6].upper()

    team = CATEGORY_INFO.get(
        category,
        {}
    ).get(
        "team",
        "Application Support"
    )

    if priority is None:
        priority = classify_priority(issue)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()

    conn.execute("""
        INSERT INTO tickets (
            ticket_id,
            created_at,
            resolved_at,
            category,
            issue,
            priority,
            status,
            team,
            resolution_time_hrs,
            stage,
            escalated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        now,
        None,
        category,
        issue,
        priority,
        "Open",
        team,
        0,
        "Ticket Created",
        0
    ))

    conn.commit()
    conn.close()

    return ticket_id


def get_ticket(ticket_id):

    conn = get_connection()

    row = conn.execute("""
        SELECT *
        FROM tickets
        WHERE ticket_id = ?
    """, (ticket_id,)).fetchone()

    columns = [
        "ticket_id",
        "created_at",
        "resolved_at",
        "category",
        "issue",
        "priority",
        "status",
        "team",
        "resolution_time_hrs",
        "stage",
        "escalated"
    ]

    conn.close()

    if row is None:
        return None

    return dict(zip(columns, row))


def get_all_tickets():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM tickets
        ORDER BY created_at DESC
    """, conn)

    conn.close()

    return df


def update_ticket(ticket_id, **kwargs):

    allowed = {
        "category",
        "issue",
        "priority",
        "status",
        "team",
        "stage",
        "resolved_at",
        "resolution_time_hrs",
        "escalated"
    }

    updates = []
    values = []

    for key, value in kwargs.items():

        if key in allowed:
            updates.append(f"{key} = ?")
            values.append(value)

    if not updates:
        return

    values.append(ticket_id)

    conn = get_connection()

    conn.execute(
        f"""
        UPDATE tickets
        SET {", ".join(updates)}
        WHERE ticket_id = ?
        """,
        values
    )

    conn.commit()
    conn.close()


def mark_resolved(ticket_id):

    ticket = get_ticket(ticket_id)

    if ticket is None:
        return

    created = datetime.strptime(
        ticket["created_at"],
        "%Y-%m-%d %H:%M:%S"
    )

    resolved = datetime.now()

    hours = round(
        (resolved - created).total_seconds() / 3600,
        2
    )

    update_ticket(
        ticket_id,
        status="Resolved",
        stage="Resolved by AI Helpdesk",
        resolved_at=resolved.strftime("%Y-%m-%d %H:%M:%S"),
        resolution_time_hrs=hours,
        escalated=0
    )


# ============================================================
# TROUBLESHOOTING HISTORY
# ============================================================

def save_history(ticket_id, speaker, message):

    if not ticket_id:
        return

    conn = get_connection()

    conn.execute("""
        INSERT INTO troubleshooting_history
        (ticket_id, speaker, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        ticket_id,
        speaker,
        message,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_history(ticket_id):

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT speaker, message, created_at
        FROM troubleshooting_history
        WHERE ticket_id = ?
        ORDER BY id
    """, conn, params=(ticket_id,))

    conn.close()

    return df


# ============================================================
# CLASSIFICATION
# ============================================================

def clean_text(text):

    text = str(text).lower()

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    return text.strip()


def detect_category(issue, selected_category="VPN"):

    text = clean_text(issue)

    keyword_map = {

        "Outlook": [
            "outlook",
            "outlook not opening",
            "outlook not working",
            "outlook mail"
        ],

        "Email": [
            "email",
            "e-mail",
            "mail",
            "send mail",
            "receive mail",
            "mailbox"
        ],

        "VPN": [
            "vpn",
            "virtual private network"
        ],

        "Wi-Fi": [
            "wifi",
            "wi-fi",
            "wireless"
        ],

        "Internet": [
            "internet",
            "network connection",
            "no internet"
        ],

        "Printer": [
            "printer",
            "printing",
            "print"
        ],

        "Laptop": [
            "laptop",
            "computer",
            "system",
            "pc"
        ],

        "Password/Login": [
            "password",
            "login",
            "log in",
            "signin",
            "sign in",
            "account locked"
        ],

        "Microsoft Teams": [
            "teams",
            "microsoft teams"
        ],

        "Browser": [
            "browser",
            "chrome",
            "edge",
            "firefox",
            "website"
        ],

        "Software": [
            "software",
            "application",
            "app",
            "program"
        ],
    }

    for category, keywords in keyword_map.items():

        for keyword in keywords:

            if keyword in text:
                return category

    return selected_category if selected_category in CATEGORIES else "Software"


def classify_priority(issue):

    text = clean_text(issue)

    critical_words = [
        "server down",
        "security breach",
        "data loss",
        "ransomware",
        "production down",
        "critical"
    ]

    high_words = [
        "urgent",
        "cannot work",
        "business stopped",
        "system down",
        "unable to login",
        "major issue"
    ]

    medium_words = [
        "slow",
        "error",
        "problem",
        "not working"
    ]

    if any(word in text for word in critical_words):
        return "Critical"

    if any(word in text for word in high_words):
        return "High"

    if any(word in text for word in medium_words):
        return "Medium"

    return "Low"


# ============================================================
# MODEL LOADING
# ============================================================

@st.cache_resource
def load_models():

    models = {}

    paths = {
        "category": "Models/category_model.pkl",
        "team": "Models/team_model.pkl",
        "priority": "Models/priority_model.pkl",
        "vectorizer": "Models/tfidf_vectorizer.pkl",
    }

    for name, path in paths.items():

        if os.path.exists(path):

            try:
                models[name] = joblib.load(path)

            except Exception:
                models[name] = None

        else:
            models[name] = None

    return models


MODELS = load_models()


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

def get_smtp_config():

    try:

        return {
            "server": st.secrets.get(
                "SMTP_SERVER",
                "smtp.gmail.com"
            ),

            "port": int(
                st.secrets.get(
                    "SMTP_PORT",
                    587
                )
            ),

            "username": st.secrets.get(
                "SMTP_USERNAME",
                ""
            ),

            "password": st.secrets.get(
                "SMTP_PASSWORD",
                ""
            ),
        }

    except Exception:

        return {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": "",
            "password": "",
        }


def email_configured():

    config = get_smtp_config()

    return bool(
        config["username"]
        and config["password"]
    )


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(
    receiver,
    subject,
    body
):

    config = get_smtp_config()

    if not config["username"]:
        return False, "SMTP username is not configured."

    if not config["password"]:
        return False, "SMTP password/app-password is not configured."

    if not receiver or receiver == "Not configured":
        return False, "Team email is not configured."

    try:

        msg = MIMEMultipart()

        msg["From"] = config["username"]
        msg["To"] = receiver
        msg["Subject"] = subject

        msg.attach(
            MIMEText(
                body,
                "plain"
            )
        )

        server = smtplib.SMTP(
            config["server"],
            config["port"]
        )

        server.starttls()

        server.login(
            config["username"],
            config["password"]
        )

        server.sendmail(
            config["username"],
            receiver,
            msg.as_string()
        )

        server.quit()

        return True, "Email sent successfully."

    except Exception as e:

        return False, f"Email sending failed: {e}"


# ============================================================
# TICKET EMAIL
# ============================================================

def build_ticket_email(ticket):

    team_email = get_team_email(
        ticket["team"]
    )

    body = f"""
AI ENTERPRISE HELPDESK
======================

Company:
{COMPANY_NAME}

Ticket ID:
{ticket["ticket_id"]}

Category:
{ticket["category"]}

Issue:
{ticket["issue"]}

Priority:
{ticket["priority"]}

Status:
{ticket["status"]}

Assigned Team:
{ticket["team"]}

Team Email:
{team_email}

Stage:
{ticket["stage"]}

Created At:
{ticket["created_at"]}

Resolved At:
{ticket["resolved_at"] or "Not resolved"}

Resolution Time:
{ticket["resolution_time_hrs"]} hours


This ticket has been assigned to your working team.

Please review the ticket and take the necessary action.
"""

    return body


def notify_team(ticket_id):

    ticket = get_ticket(ticket_id)

    if not ticket:
        return False, "Ticket not found."

    receiver = get_team_email(
        ticket["team"]
    )

    subject = (
        f"[Helpdesk Ticket {ticket_id}] "
        f"{ticket['category']} - {ticket['priority']}"
    )

    body = build_ticket_email(ticket)

    return send_email(
        receiver,
        subject,
        body
    )


# ============================================================
# ESCALATION EMAIL WITH COMPLETE HISTORY
# ============================================================

def notify_team_with_history(
    ticket_id,
    chatbot_history
):

    ticket = get_ticket(ticket_id)

    if not ticket:
        return False, "Ticket not found."

    receiver = get_team_email(
        ticket["team"]
    )

    subject = (
        f"[ESCALATED] Helpdesk Ticket {ticket_id}"
    )

    body = f"""
AI ENTERPRISE HELPDESK
======================

ESCALATED TICKET

Company:
{COMPANY_NAME}

Ticket ID:
{ticket["ticket_id"]}

Category:
{ticket["category"]}

Issue:
{ticket["issue"]}

Priority:
{ticket["priority"]}

Status:
{ticket["status"]}

Assigned Team:
{ticket["team"]}

Team Email:
{receiver}

Stage:
{ticket["stage"]}

Created At:
{ticket["created_at"]}


============================================================
AI TROUBLESHOOTING HISTORY
============================================================

"""

    for speaker, message in chatbot_history:

        if speaker == "bot":
            speaker_name = "AI Helpdesk"
        else:
            speaker_name = "User"

        body += (
            f"\n{speaker_name}: "
            f"{message}\n"
        )

    body += """

============================================================

The AI self-service troubleshooting process has been
completed without resolving the issue.

Please investigate and resolve this ticket.

This email contains the complete troubleshooting history.
"""

    return send_email(
        receiver,
        subject,
        body
    )


# ============================================================
# NAVIGATION
# ============================================================

def go_to(page):

    st.session_state.page = page


def reset_chatbot():

    st.session_state.chatbot_active = False
    st.session_state.chatbot_category = ""
    st.session_state.chatbot_issue = ""
    st.session_state.chatbot_step = 0
    st.session_state.chatbot_history = []
    st.session_state.chatbot_escalated = False
    st.session_state.chatbot_escalation_message = ""
    st.session_state.active_ticket = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        f"""
        ## 🤖 {COMPANY_NAME}
        ### AI Enterprise Helpdesk
        """
    )

    st.divider()

    st.subheader("📊 Main Menu")

    if st.button(
        "📊 Dashboard",
        use_container_width=True
    ):
        go_to("Dashboard")
        st.rerun()

    if st.button(
        "🏷️ Ticket Classification",
        use_container_width=True
    ):
        go_to("Ticket Classification")
        st.rerun()

    if st.button(
        "🤖 AI Helpdesk Chatbot",
        use_container_width=True
    ):
        go_to("AI Helpdesk Chatbot")
        st.rerun()

    if st.button(
        "⚙️ Admin Settings",
        use_container_width=True
    ):
        go_to("Admin Settings")
        st.rerun()

    st.divider()

    st.subheader("🛠️ IT Support Categories")

    for category in CATEGORIES:

        if st.button(
            category,
            use_container_width=True,
            key=f"side_{category}"
        ):

            st.session_state.selected_category = category
            go_to("Ticket Classification")
            st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():

    st.title("📊 Enterprise Helpdesk Dashboard")

    st.caption(
        "Centralized monitoring of IT support tickets and AI helpdesk operations."
    )

    tickets = get_all_tickets()

    if tickets.empty:

        st.info(
            "No tickets have been created yet."
        )

    else:

        total = len(tickets)

        open_count = len(
            tickets[
                tickets["status"] == "Open"
            ]
        )

        progress_count = len(
            tickets[
                tickets["status"] == "In Progress"
            ]
        )

        resolved_count = len(
            tickets[
                tickets["status"] == "Resolved"
            ]
        )

        escalated_count = len(
            tickets[
                tickets["status"] == "Escalated"
            ]
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Total Tickets",
            total
        )

        c2.metric(
            "Open",
            open_count
        )

        c3.metric(
            "In Progress",
            progress_count
        )

        c4.metric(
            "Resolved",
            resolved_count
        )

        c5.metric(
            "Escalated",
            escalated_count
        )

        st.divider()

        st.subheader("🎫 Ticket Overview")

        display = tickets.copy()

        display.columns = [
            "Ticket ID",
            "Created",
            "Resolved",
            "Category",
            "Issue",
            "Priority",
            "Status",
            "Team",
            "Resolution Hours",
            "Stage",
            
        ]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("👥 Team Workload")

    teams = get_all_teams()

    if not teams.empty:

        team_data = []

        for _, team in teams.iterrows():

            team_name = team["team_name"]

            if tickets.empty:
                count = 0
                resolved = 0
                escalated = 0
            else:

                team_tickets = tickets[
                    tickets["team"] == team_name
                ]

                count = len(team_tickets)

                resolved = len(
                    team_tickets[
                        team_tickets["status"] == "Resolved"
                    ]
                )

                escalated = len(
                    team_tickets[
                        team_tickets["status"] == "Escalated"
                    ]
                )

            team_data.append({
                "Working Team": team_name,
                "Team Email": team["team_email"],
                "Assigned Tickets": count,
                "Resolved": resolved,
                "Escalated": escalated,
            })

        st.dataframe(
            pd.DataFrame(team_data),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# TICKET CLASSIFICATION
# ============================================================

def render_ticket_classification():

    st.title("🏷️ AI Ticket Classification")

    st.write(
        "Describe your IT issue. The system automatically detects "
        "the category and assigns the appropriate support team."
    )

    issue = st.text_area(
        "Describe Your Issue",
        placeholder=(
            "Example: My Outlook is not opening "
            "and I cannot access my emails."
        ),
        height=150
    )

    selected = st.session_state.get(
        "selected_category",
        "VPN"
    )

    detected_category = detect_category(
        issue,
        selected
    ) if issue.strip() else selected

    category = st.selectbox(
        "Issue Category",
        CATEGORIES,
        index=CATEGORIES.index(
            detected_category
        )
    )

    if issue.strip():

        st.success(
            f"🤖 Detected Category: **{detected_category}**"
        )

    priority = classify_priority(
        issue
    ) if issue.strip() else "Low"

    team = CATEGORY_INFO[
        category
    ]["team"]

    st.info(
        f"""
        **Assigned Team:** {team}

        **Team Email:** {get_team_email(team)}

        **Priority:** {priority}
        """
    )

    if st.button(
        "🎫 Create Helpdesk Ticket",
        type="primary",
        use_container_width=True
    ):

        if not issue.strip():

            st.error(
                "Please describe your issue."
            )

            return

        final_category = detect_category(
            issue,
            category
        )

        final_priority = classify_priority(
            issue
        )

        ticket_id = create_ticket(
            final_category,
            issue.strip(),
            final_priority
        )

        st.session_state.active_ticket = ticket_id

        # ----------------------------------------------------
        # Save initial chatbot history
        # ----------------------------------------------------

        st.session_state.chatbot_category = final_category
        st.session_state.chatbot_issue = issue.strip()
        st.session_state.chatbot_step = 0

        st.session_state.chatbot_history = [
            (
                "bot",
                f"Let's troubleshoot your "
                f"**{final_category}** issue step by step."
            )
        ]

        st.session_state.chatbot_active = True
        st.session_state.chatbot_escalated = False
        st.session_state.chatbot_escalation_message = ""

        save_history(
            ticket_id,
            "bot",
            f"Let's troubleshoot your {final_category} issue step by step."
        )

        # ----------------------------------------------------
        # Send assignment email
        # ----------------------------------------------------

        ok, message = notify_team(
            ticket_id
        )

        st.success(
            f"🎫 Ticket **{ticket_id}** created successfully."
        )

        st.info(
            f"""
            **Category:** {final_category}

            **Priority:** {final_priority}

            **Assigned Team:** {CATEGORY_INFO[final_category]["team"]}

            **Team Email:** {
                get_team_email(
                    CATEGORY_INFO[final_category]["team"]
                )
            }
            """
        )

        if ok:

            st.success(
                "📧 Ticket assignment email sent successfully."
            )

        else:

            st.warning(
                f"📧 Email notification: {message}"
            )

        st.session_state.page = "AI Helpdesk Chatbot"

        st.rerun()


# ============================================================
# AI CHATBOT
# ============================================================

def render_chatbot():

    st.title("🤖 AI Helpdesk Chatbot")

    st.write(
        "The AI Helpdesk continues troubleshooting "
        "after self-service steps fail."
    )

    # ========================================================
    # START NEW CHAT
    # ========================================================

    if not st.session_state.chatbot_active:

        issue = st.text_area(
            "Describe the issue",
            placeholder=(
                "Example: My Outlook is not working..."
            ),
            height=120
        )

        selected_category = st.session_state.get(
            "selected_category",
            "VPN"
        )

        if issue.strip():

            detected_category = detect_category(
                issue,
                selected_category
            )

        else:

            detected_category = selected_category

        category = st.selectbox(
            "Select Issue Category",
            CATEGORIES,
            index=CATEGORIES.index(
                detected_category
            )
        )

        if issue.strip():

            st.success(
                f"🤖 Category automatically detected as "
                f"**{detected_category}**"
            )

        if st.button(
            "🚀 Start AI Troubleshooting",
            use_container_width=True
        ):

            if not issue.strip():

                st.error(
                    "Please describe your issue."
                )

                return

            final_category = detect_category(
                issue,
                category
            )

            # ------------------------------------------------
            # Create ticket if no active ticket exists
            # ------------------------------------------------

            if not st.session_state.active_ticket:

                ticket_id = create_ticket(
                    final_category,
                    issue.strip(),
                    classify_priority(issue)
                )

                st.session_state.active_ticket = ticket_id

                # Email assigned team

                notify_team(ticket_id)

            else:

                ticket_id = (
                    st.session_state.active_ticket
                )

            st.session_state.chatbot_category = final_category
            st.session_state.chatbot_issue = issue.strip()
            st.session_state.chatbot_step = 0

            st.session_state.chatbot_history = [
                (
                    "bot",
                    f"Let's troubleshoot your "
                    f"**{final_category}** issue step by step."
                )
            ]

            st.session_state.chatbot_active = True
            st.session_state.chatbot_escalated = False
            st.session_state.chatbot_escalation_message = ""

            save_history(
                ticket_id,
                "bot",
                f"Let's troubleshoot your {final_category} issue step by step."
            )

            st.session_state.selected_category = final_category

            st.rerun()

        return

    # ========================================================
    # ACTIVE CHAT
    # ========================================================

    category = st.session_state.chatbot_category

    issue = st.session_state.chatbot_issue

    steps = CATEGORY_INFO[
        category
    ]["troubleshooting"]

    ticket_id = st.session_state.active_ticket

    # ========================================================
    # TICKET INFORMATION
    # ========================================================

    if ticket_id:

        ticket = get_ticket(
            ticket_id
        )

        if ticket:

            st.info(
                f"""
🎫 **Ticket:** {ticket_id}

**Category:** {ticket["category"]}

**Issue:** {ticket["issue"]}

**Priority:** {ticket["priority"]}

**Team:** {ticket["team"]}

**Team Email:** {get_team_email(ticket["team"])}

**Stage:** AI Troubleshooting
"""
            )

            if ticket["status"] not in [
                "Resolved",
                "Escalated"
            ]:

                update_ticket(
                    ticket_id,
                    status="In Progress",
                    stage="AI Troubleshooting"
                )

    # ========================================================
    # CHAT HISTORY
    # ========================================================

    for speaker, message in st.session_state.chatbot_history:

        if speaker == "bot":

            st.markdown(
                f"🤖 **AI Helpdesk:** {message}"
            )

        else:

            st.markdown(
                f"🧑 **You:** {message}"
            )

    # ========================================================
    # CURRENT STEP
    # ========================================================

    step = st.session_state.chatbot_step

    # ========================================================
    # TROUBLESHOOTING
    # ========================================================

    if step < len(steps):

        st.markdown("---")

        st.subheader(
            f"🔧 AI Troubleshooting Step "
            f"{step + 1} of {len(steps)}"
        )

        st.info(
            steps[step]
        )

        col1, col2 = st.columns(2)

        # ====================================================
        # YES
        # ====================================================

        with col1:

            if st.button(
                "✅ Yes, It Worked",
                key=f"worked_{step}",
                use_container_width=True
            ):

                st.session_state.chatbot_history.append(
                    (
                        "user",
                        "Yes, the issue is resolved."
                    )
                )

                st.session_state.chatbot_history.append(
                    (
                        "bot",
                        "🎉 Excellent! The issue has been successfully resolved."
                    )
                )

                save_history(
                    ticket_id,
                    "user",
                    "Yes, the issue is resolved."
                )

                save_history(
                    ticket_id,
                    "bot",
                    "Excellent! The issue has been successfully resolved."
                )

                if ticket_id:

                    mark_resolved(
                        ticket_id
                    )

                st.success(
                    "✅ Ticket marked as RESOLVED."
                )

                st.balloons()

                st.session_state.chatbot_active = False
                st.session_state.chatbot_step = 0

                st.session_state.page = "Dashboard"

                st.rerun()

        # ====================================================
        # NO
        # ====================================================

        with col2:

            if st.button(
                "❌ No, Still Not Working",
                key=f"failed_{step}",
                use_container_width=True
            ):

                st.session_state.chatbot_history.append(
                    (
                        "user",
                        "Still not working."
                    )
                )

                save_history(
                    ticket_id,
                    "user",
                    "Still not working."
                )

                next_step = step + 1

                st.session_state.chatbot_step = next_step

                if next_step < len(steps):

                    message = (
                        "Understood. Let's try the next "
                        "troubleshooting step."
                    )

                    st.session_state.chatbot_history.append(
                        (
                            "bot",
                            message
                        )
                    )

                    save_history(
                        ticket_id,
                        "bot",
                        message
                    )

                else:

                    message = (
                        "All AI troubleshooting steps "
                        "have now been completed."
                    )

                    st.session_state.chatbot_history.append(
                        (
                            "bot",
                            message
                        )
                    )

                    save_history(
                        ticket_id,
                        "bot",
                        message
                    )

                st.rerun()

    # ========================================================
    # ESCALATION
    # ========================================================

    else:

        st.markdown("---")

        st.error(
            "🚨 AI troubleshooting could not resolve the issue."
        )

        st.warning(
            "The ticket is ready to be escalated to the appropriate working team."
        )

        ticket = get_ticket(
            ticket_id
        )

        if ticket:

            escalation_team = ticket["team"]

        else:

            escalation_team = CATEGORY_INFO[
                category
            ]["team"]

        escalation_email = get_team_email(
            escalation_team
        )

        st.info(
            f"""
📩 **Escalation Team:** {escalation_team}

📧 **Team Email:** {escalation_email}

The working team will receive the complete ticket
information and AI troubleshooting history.
"""
        )

        # ====================================================
        # ESCALATE
        # ====================================================

        if not st.session_state.chatbot_escalated:

            if st.button(
                "📩 Escalate Ticket to Working Team",
                type="primary",
                use_container_width=True
            ):

                # ------------------------------------------------
                # Make sure ticket exists
                # ------------------------------------------------

                if not ticket_id:

                    ticket_id = create_ticket(
                        category,
                        issue
                    )

                    st.session_state.active_ticket = ticket_id

                # ------------------------------------------------
                # Update ticket
                # ------------------------------------------------

                update_ticket(
                    ticket_id,
                    status="Escalated",
                    stage="Escalated to Working Team",
                    escalated=1
                )

                # ------------------------------------------------
                # Send complete history
                # ------------------------------------------------

                ok, message = notify_team_with_history(
                    ticket_id,
                    st.session_state.chatbot_history
                )

                final_ticket = get_ticket(
                    ticket_id
                )

                st.session_state.chatbot_escalated = True

                st.session_state.chatbot_escalation_message = ticket_id

                st.success(
                    f"🎫 Ticket **{ticket_id}** has been escalated successfully."
                )

                st.info(
                    f"""
📩 **Working Team:** {final_ticket["team"]}

📧 **Team Email:** {get_team_email(final_ticket["team"])}

📊 **Status:** Escalated

🔄 **Stage:** Escalated to Working Team
"""
                )

                if ok:

                    st.success(
                        f"📧 Escalation email successfully sent to "
                        f"{get_team_email(final_ticket['team'])}"
                    )

                else:

                    st.warning(
                        message
                    )

                st.markdown("---")

                st.subheader(
                    "📊 Current Working Status"
                )

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Ticket ID",
                    ticket_id
                )

                c2.metric(
                    "Status",
                    "Escalated"
                )

                c3.metric(
                    "Working Team",
                    final_ticket["team"]
                )

                st.success(
                    "✅ The working team has been notified. "
                    "The ticket can now be monitored from Dashboard."
                )

                st.rerun()

        # ====================================================
        # ALREADY ESCALATED
        # ====================================================

        else:

            final_ticket_id = (
                st.session_state.chatbot_escalation_message
            )

            st.success(
                f"✅ Ticket **{final_ticket_id}** "
                f"is already escalated to the working team."
            )

            st.info(
                "📊 You can monitor the ticket status from Dashboard."
            )

        # ====================================================
        # DASHBOARD BUTTON
        # ====================================================

        if st.button(
            "🏠 Return to Dashboard",
            use_container_width=True,
            key="dashboard_after_escalation"
        ):

            reset_chatbot()

            st.session_state.page = "Dashboard"

            st.rerun()


# ============================================================
# ADMIN SETTINGS
# ============================================================

def render_admin_settings():

    st.title("⚙️ Admin Settings")

    st.write(
        "Manage working teams, team emails and existing helpdesk tickets."
    )

    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.admin_logged_in:

        st.subheader(
            "🔐 Administrator Login"
        )

        password = st.text_input(
            "Admin Password",
            type="password"
        )

        if st.button(
            "🔓 Login",
            use_container_width=True
        ):

            try:

                correct_password = st.secrets.get(
                    "ADMIN_PASSWORD",
                    "admin123"
                )

            except Exception:

                correct_password = "admin123"

            if password == correct_password:

                st.session_state.admin_logged_in = True

                st.success(
                    "✅ Admin login successful."
                )

                st.rerun()

            else:

                st.error(
                    "❌ Invalid admin password."
                )

        return

    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button(
        "🔒 Logout Admin",
        use_container_width=False
    ):

        st.session_state.admin_logged_in = False
        st.rerun()

    st.divider()

    # ========================================================
    # TEAM MANAGEMENT
    # ========================================================

    st.subheader(
        "👥 Team & Email Management"
    )

    teams = get_all_teams()

    if not teams.empty:

        for _, team in teams.iterrows():

            team_name = team["team_name"]

            tickets = get_all_tickets()

            if tickets.empty:

                assigned = 0
                resolved = 0
                escalated = 0
                pending = 0

            else:

                team_tickets = tickets[
                    tickets["team"] == team_name
                ]

                assigned = len(
                    team_tickets
                )

                resolved = len(
                    team_tickets[
                        team_tickets["status"] == "Resolved"
                    ]
                )

                escalated = len(
                    team_tickets[
                        team_tickets["status"] == "Escalated"
                    ]
                )

                pending = len(
                    team_tickets[
                        team_tickets["status"].isin(
                            ["Open", "In Progress"]
                        )
                    ]
                )

            with st.expander(
                f"👥 {team_name}"
            ):

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Assigned",
                    assigned
                )

                c2.metric(
                    "Resolved",
                    resolved
                )

                c3.metric(
                    "Pending",
                    pending
                )

                c4.metric(
                    "Escalated",
                    escalated
                )

                new_email = st.text_input(
                    "Team Email",
                    value=team["team_email"],
                    key=f"email_{team_name}"
                )

                if st.button(
                    "💾 Update Team Email",
                    key=f"save_email_{team_name}"
                ):

                    if not new_email.strip():

                        st.error(
                            "Email cannot be empty."
                        )

                    else:

                        update_team_email(
                            team_name,
                            new_email.strip()
                        )

                        st.success(
                            f"✅ {team_name} email updated."
                        )

                        st.rerun()

    st.divider()
# ========================================================
# ALL TICKETS
# ========================================================

st.subheader(
    "🎫 Ticket Management"
)

tickets = get_all_tickets()

if tickets is None or tickets.empty:

    st.info(
        "No tickets available."
    )

else:

    st.dataframe(
        tickets,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ====================================================
    # SELECT TICKET
    # ====================================================

    ticket_ids = (
        tickets["ticket_id"]
        .dropna()
        .astype(str)
        .tolist()
    )

    if not ticket_ids:

        st.info(
            "No ticket IDs available."
        )

    else:

        selected_ticket_id = st.selectbox(
            "🎫 Select Ticket to Edit",
            ticket_ids,
            key="admin_selected_ticket"
        )

        # =================================================
        # GET LATEST TICKET
        # =================================================

        ticket = get_ticket(
            selected_ticket_id
        )

        if ticket is None:

            st.error(
                f"❌ Ticket {selected_ticket_id} not found."
            )

        else:

            # =================================================
            # EDIT TICKET
            # =================================================

            st.subheader(
                f"✏️ Edit Ticket - {selected_ticket_id}"
            )

            col1, col2 = st.columns(2)

            # =================================================
            # LEFT COLUMN
            # =================================================

            with col1:

                # ---------------------------------------------
                # CATEGORY
                # ---------------------------------------------

                category_options = list(CATEGORIES)

                current_category = (
                    ticket["category"]
                    if ticket["category"]
                    else category_options[0]
                )

                if current_category not in category_options:

                    category_options.append(
                        current_category
                    )

                edit_category = st.selectbox(
                    "Category",
                    category_options,
                    index=category_options.index(
                        current_category
                    ),
                    key=f"edit_category_{selected_ticket_id}"
                )

                # ---------------------------------------------
                # PRIORITY
                # ---------------------------------------------

                priority_options = [
                    "Low",
                    "Medium",
                    "High",
                    "Critical"
                ]

                current_priority = (
                    ticket["priority"]
                    if ticket["priority"]
                    else "Low"
                )

                if current_priority not in priority_options:

                    current_priority = "Low"

                edit_priority = st.selectbox(
                    "Priority",
                    priority_options,
                    index=priority_options.index(
                        current_priority
                    ),
                    key=f"edit_priority_{selected_ticket_id}"
                )

                # ---------------------------------------------
                # STATUS
                # ---------------------------------------------

                status_options = [
                    "Open",
                    "In Progress",
                    "Resolved",
                    "Escalated"
                ]

                current_status = (
                    ticket["status"]
                    if ticket["status"]
                    else "Open"
                )

                if current_status not in status_options:

                    current_status = "Open"

                edit_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(
                        current_status
                    ),
                    key=f"edit_status_{selected_ticket_id}"
                )

            # =================================================
            # RIGHT COLUMN
            # =================================================

            with col2:

                # ---------------------------------------------
                # TEAM LIST
                # ---------------------------------------------

                current_teams = get_all_teams()

                if (
                    current_teams is not None
                    and not current_teams.empty
                    and "team_name"
                    in current_teams.columns
                ):

                    teams_list = (
                        current_teams["team_name"]
                        .dropna()
                        .astype(str)
                        .tolist()
                    )

                else:

                    teams_list = [
                        "Application Support",
                        "Desktop Support",
                        "Email/Collab Team",
                        "Network Team",
                        "Security Team",
                        "Hardware Team"
                    ]

                # ---------------------------------------------
                # CURRENT TEAM
                # ---------------------------------------------

                current_team = (
                    ticket["team"]
                    if ticket["team"]
                    else teams_list[0]
                )

                if current_team not in teams_list:

                    teams_list.append(
                        current_team
                    )

                edit_team = st.selectbox(
                    "Assigned Team",
                    teams_list,
                    index=teams_list.index(
                        current_team
                    ),
                    key=f"edit_team_{selected_ticket_id}"
                )

                # ---------------------------------------------
                # STAGE
                # ---------------------------------------------

                current_stage = (
                    ticket["stage"]
                    if ticket["stage"]
                    else ""
                )

                edit_stage = st.text_input(
                    "Stage",
                    value=current_stage,
                    key=f"edit_stage_{selected_ticket_id}"
                )

            # =================================================
            # ISSUE
            # =================================================

            current_issue = (
                ticket["issue"]
                if ticket["issue"]
                else ""
            )

            edit_issue = st.text_area(
                "Issue Description",
                value=current_issue,
                height=130,
                key=f"edit_issue_{selected_ticket_id}"
            )

            # =================================================
            # SAVE CHANGES
            # =================================================

            if st.button(
                "💾 Save Ticket Changes",
                type="primary",
                use_container_width=True,
                key=f"save_ticket_{selected_ticket_id}"
            ):

                try:

                    # -----------------------------------------
                    # RESOLVED DATE
                    # -----------------------------------------

                    old_resolved_at = ticket["resolved_at"]

                    if edit_status == "Resolved":

                        if old_resolved_at:

                            resolved_at = old_resolved_at

                        else:

                            resolved_at = (
                                datetime.now()
                                .strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            )

                    else:

                        resolved_at = None

                    # -----------------------------------------
                    # ESCALATED
                    # -----------------------------------------

                    escalated_value = (
                        1
                        if edit_status == "Escalated"
                        else 0
                    )

                    # -----------------------------------------
                    # UPDATE DATABASE
                    # -----------------------------------------

                    update_ticket(
                        selected_ticket_id,
                        category=edit_category,
                        issue=edit_issue.strip(),
                        priority=edit_priority,
                        status=edit_status,
                        team=edit_team,
                        stage=edit_stage.strip(),
                        resolved_at=resolved_at,
                        escalated=escalated_value
                    )

                    st.success(
                        f"✅ Ticket {selected_ticket_id} "
                        "updated successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Ticket update failed: {e}"
                    )

            # =================================================
            # EMAIL ACTIONS
            # =================================================

            st.divider()

            st.subheader(
                "📧 Email Actions"
            )

            # ---------------------------------------------
            # CURRENT TEAM EMAIL
            # ---------------------------------------------

            try:

                current_team_email = get_team_email(
                    edit_team
                )

            except Exception:

                current_team_email = None

            if current_team_email:

                st.info(
                    f"📧 Current Team Email: "
                    f"**{current_team_email}**"
                )

            else:

                st.warning(
                    f"⚠️ No email configured for "
                    f"**{edit_team}**"
                )

            # =================================================
            # SEND / RESEND EMAIL
            # =================================================

            if st.button(
                "📧 Send / Resend Ticket Email",
                use_container_width=True,
                key=f"send_email_{selected_ticket_id}"
            ):

                try:

                    ok, message = notify_team(
                        selected_ticket_id
                    )

                    if ok:

                        st.success(
                            "✅ Ticket email sent successfully."
                        )

                    else:

                        st.error(
                            f"❌ {message}"
                        )

                except Exception as e:

                    st.error(
                        f"❌ Email sending failed: {e}"
                    )

            # =================================================
            # TROUBLESHOOTING HISTORY EMAIL
            # =================================================

            if st.button(
                "📧 Send Complete Troubleshooting History",
                use_container_width=True,
                key=f"send_history_{selected_ticket_id}"
            ):

                try:

                    history_df = get_history(
                        selected_ticket_id
                    )

                    history = []

                    if (
                        history_df is not None
                        and not history_df.empty
                    ):

                        for _, row in history_df.iterrows():

                            history.append(
                                (
                                    row["speaker"],
                                    row["message"]
                                )
                            )

                    ok, message = (
                        notify_team_with_history(
                            selected_ticket_id,
                            history
                        )
                    )

                    if ok:

                        st.success(
                            "✅ Complete troubleshooting "
                            "history email sent successfully."
                        )

                    else:

                        st.error(
                            f"❌ {message}"
                        )

                except Exception as e:

                    st.error(
                        f"❌ History email failed: {e}"
                    )

            # =================================================
            # CURRENT TICKET INFORMATION
            # =================================================

            st.divider()

            st.subheader(
                "📋 Current Ticket Information"
            )

            info1, info2, info3 = st.columns(3)

            info1.metric(
                "Ticket ID",
                selected_ticket_id
            )

            info2.metric(
                "Status",
                edit_status
            )

            info3.metric(
                "Assigned Team",
                edit_team
            )

            st.write(
                f"**📧 Team Email:** "
                f"{current_team_email or 'Not Configured'}"
            )