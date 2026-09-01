import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# LOAD PRE-BUILT KNOWLEDGE BASE MODEL
# =========================================================

vectorizer = joblib.load(
    "Models/chatbot_vectorizer.pkl"
)

knowledge_vectors = joblib.load(
    "Models/chatbot_vectors.pkl"
)

df = joblib.load(
    "Models/chatbot_knowledge.pkl"
)

print(
    "\n📚 Knowledge Base Articles:",
    len(df)
)

print(
    "✅ Chatbot Knowledge Base Loaded Successfully!"
)


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    return str(text).lower().strip()


# =========================================================
# MAIN CHATBOT RESPONSE
# =========================================================

def chatbot_response(user_question):

    question = clean_text(user_question)


    # =====================================================
    # SECURITY PRIORITY
    # =====================================================

    security_keywords = [

        "hacked",
        "hack",
        "hacker",
        "compromised",
        "account compromised",
        "someone hacked",
        "someone accessed",
        "someone access",
        "unauthorized access",
        "suspicious activity",
        "suspicious login",
        "unknown login",
        "unknown device",
        "security issue",
        "security problem",
        "account breach",
        "account breached",
        "cyber attack",
        "cyberattack"

    ]


    if any(
        keyword in question
        for keyword in security_keywords
    ):

        security_matches = df[
            (
                df["Question"]
                .astype(str)
                .str.lower()
                .str.contains(
                    "compromised|hacked|security|breach",
                    regex=True,
                    na=False
                )
            )
            |
            (
                df["Category"]
                .astype(str)
                .str.lower()
                .str.contains(
                    "security",
                    regex=False,
                    na=False
                )
            )
        ]


        if len(security_matches) > 0:

            result = security_matches.iloc[0]

            return {

                "found": True,

                "question": result["Question"],

                "category": result["Category"],

                "steps": result["Steps"],

                "resolution": result["Resolution"],

                "support_team": result["Support_Team"]

            }


    # =====================================================
    # PASSWORD PRIORITY
    # =====================================================

    password_keywords = [

        "forgot password",
        "forgot my password",
        "forgot login password",
        "can't remember password",
        "cannot remember password",
        "dont remember password",
        "don't remember password",
        "password forgotten",
        "lost password",
        "reset password",
        "password reset"

    ]


    if any(
        keyword in question
        for keyword in password_keywords
    ):

        password_matches = df[

            df["Question"]
            .astype(str)
            .str.lower()
            .str.contains(
                "password",
                regex=False,
                na=False
            )

        ]


        if len(password_matches) > 0:

            result = password_matches.iloc[0]

            return {

                "found": True,

                "question": result["Question"],

                "category": result["Category"],

                "steps": result["Steps"],

                "resolution": result["Resolution"],

                "support_team": result["Support_Team"]

            }


    # =====================================================
    # OUTLOOK PRIORITY
    # =====================================================

    if "outlook" in question:

        outlook_matches = df[

            df["Question"]
            .astype(str)
            .str.lower()
            .str.contains(
                "outlook",
                regex=False,
                na=False
            )

        ]


        if len(outlook_matches) > 0:

            result = outlook_matches.iloc[0]

            return {

                "found": True,

                "question": result["Question"],

                "category": result["Category"],

                "steps": result["Steps"],

                "resolution": result["Resolution"],

                "support_team": result["Support_Team"]

            }


    # =====================================================
    # VPN PRIORITY
    # =====================================================

    if "vpn" in question:

        vpn_matches = df[

            df["Question"]
            .astype(str)
            .str.lower()
            .str.contains(
                "vpn",
                regex=False,
                na=False
            )

        ]


        if len(vpn_matches) > 0:

            result = vpn_matches.iloc[0]

            return {

                "found": True,

                "question": result["Question"],

                "category": result["Category"],

                "steps": result["Steps"],

                "resolution": result["Resolution"],

                "support_team": result["Support_Team"]

            }


    # =====================================================
    # EMAIL RECEIVING
    # =====================================================

    email_receive_keywords = [

        "email not coming",
        "emails not coming",
        "mail not coming",
        "mails not coming",

        "email not receiving",
        "emails not receiving",
        "mail not receiving",
        "mails not receiving",

        "not getting emails",
        "not getting email",
        "not getting mails",
        "not getting mail",

        "email is not coming",
        "emails are not coming",

        "emails are not arriving",
        "email is not arriving",
        "email not arriving",
        "emails not arriving",

        "not receiving emails",
        "not receiving email"

    ]


    if any(
        keyword in question
        for keyword in email_receive_keywords
    ):

        email_matches = df[

            df["Question"]
            .astype(str)
            .str.lower()
            .str.contains(
                "receiving|receiv|coming|arriving",
                regex=True,
                na=False
            )

        ]


        if len(email_matches) > 0:

            result = email_matches.iloc[0]

            return {

                "found": True,

                "question": result["Question"],

                "category": result["Category"],

                "steps": result["Steps"],

                "resolution": result["Resolution"],

                "support_team": result["Support_Team"]

            }


    # =====================================================
    # LAPTOP SLOW
    # =====================================================

    laptop_keywords = [

        "laptop is slow",
        "laptop running slow",
        "laptop running very slow",
        "computer is slow",
        "computer running slow",
        "pc is slow",
        "system is slow",
        "laptop very slow",
        "my laptop is running slow"

    ]


    if any(
        keyword in question
        for keyword in laptop_keywords
    ):

        hardware_matches = df[

            df["Category"]
            .astype(str)
            .str.lower()
            .str.contains(
                "hardware",
                regex=False,
                na=False
            )

        ]


        if len(hardware_matches) > 0:

            result = hardware_matches.iloc[0]

            return {

                "found": True,

                "question": result["Question"],

                "category": result["Category"],

                "steps": result["Steps"],

                "resolution": result["Resolution"],

                "support_team": result["Support_Team"]

            }


    # =====================================================
    # TF-IDF SEMANTIC FALLBACK
    # =====================================================

    user_vector = vectorizer.transform(
        [question]
    )


    similarity = cosine_similarity(
        user_vector,
        knowledge_vectors
    )


    best_match = similarity.argmax()

    best_score = similarity[0][best_match]


    if best_score < 0.15:

        return {

            "found": False,

            "message": (
                "Sorry, I could not understand the issue clearly. "
                "Please provide more details about the IT issue."
            )

        }


    result = df.iloc[best_match]


    return {

        "found": True,

        "question": result["Question"],

        "category": result["Category"],

        "steps": result["Steps"],

        "resolution": result["Resolution"],

        "support_team": result["Support_Team"]

    }


# =========================================================
# LOAD TROUBLESHOOTING DATA
# =========================================================

troubleshooting_df = pd.read_csv(
    "Knowledge_Base/troubleshooting_steps.csv"
)


troubleshooting_df["Issue"] = (
    troubleshooting_df["Issue"]
    .fillna("")
)


troubleshooting_df["Step"] = (
    troubleshooting_df["Step"]
    .fillna("")
)


troubleshooting_df["If_Not_Working"] = (
    troubleshooting_df["If_Not_Working"]
    .fillna("")
)


troubleshooting_df["If_Dont_Understand"] = (
    troubleshooting_df["If_Dont_Understand"]
    .fillna("")
)


print(
    "🧠 Troubleshooting Knowledge Loaded."
)
# =========================================================
# TROUBLESHOOTING RESPONSE
# =========================================================

# =========================================================
# TROUBLESHOOTING RESPONSE
# =========================================================

def get_troubleshooting_steps(user_issue):

    question = clean_text(user_issue)

    # =====================================================
    # OUTLOOK
    # =====================================================

    if "outlook" in question:

        return {
            "found": True,
            "question": user_issue,
            "category": "Software",

            "steps": [
                "Check your internet connection.",
                "Restart Outlook and try again.",
                "Refresh your Outlook mailbox.",
                "Check your Outlook account settings.",
                "Restart the computer and try again."
            ],

            "resolution": (
                "If the Outlook issue continues after these steps, "
                "the issue should be escalated to Application Support."
            ),

            "support_team": "Application Support"
        }


    # =====================================================
    # VPN
    # =====================================================

    if "vpn" in question:

        return {
            "found": True,
            "question": user_issue,
            "category": "Network",

            "steps": [
                "Check your internet connection.",
                "Disconnect and reconnect the VPN.",
                "Restart the VPN application.",
                "Check your VPN credentials.",
                "Restart the computer and try again."
            ],

            "resolution": (
                "If the VPN issue continues, "
                "the ticket should be escalated to Network Team."
            ),

            "support_team": "Network Team"
        }


    # =====================================================
    # EMAIL
    # =====================================================

    if any(
        word in question
        for word in [
            "email",
            "mail",
            "mailbox",
            "gmail"
        ]
    ):

        return {
            "found": True,
            "question": user_issue,
            "category": "Software",

            "steps": [
                "Check your internet connection.",
                "Refresh your email inbox and try again.",
                "Check whether your email account is connected properly.",
                "Try opening your email account again.",
                "Restart the computer and try again."
            ],

            "resolution": (
                "If the email issue continues after these steps, "
                "the issue should be escalated to Application Support."
            ),

            "support_team": "Application Support"
        }


    # =====================================================
    # PASSWORD
    # =====================================================

    if any(
        word in question
        for word in [
            "password",
            "forgot password",
            "login password",
            "reset password"
        ]
    ):

        return {
            "found": True,
            "question": user_issue,
            "category": "Access",

            "steps": [
                "Check that you are entering the correct username.",
                "Try entering the password again carefully.",
                "Use the password reset option.",
                "Check whether your account is locked.",
                "Try logging in again."
            ],

            "resolution": (
                "If the login issue continues, "
                "the ticket should be escalated to IT Helpdesk."
            ),

            "support_team": "Helpdesk Support Team"
        }


    # =====================================================
    # SECURITY
    # =====================================================

    if any(
        word in question
        for word in [
            "hacked",
            "hack",
            "compromised",
            "suspicious",
            "security",
            "breach",
            "unauthorized",
            "malware",
            "phishing"
        ]
    ):

        return {
            "found": True,
            "question": user_issue,
            "category": "Security",

            "steps": [
                "Disconnect the affected device from the network.",
                "Do not open suspicious links or attachments.",
                "Change your account password if possible.",
                "Run the approved antivirus/security scan.",
                "Report the incident to the Security Team."
            ],

            "resolution": (
                "The issue should be escalated to the Security Team "
                "for further investigation."
            ),

            "support_team": "Security Team"
        }


    # =====================================================
    # LAPTOP / COMPUTER SLOW
    # =====================================================

    if any(
        phrase in question
        for phrase in [
            "laptop is slow",
            "laptop running slow",
            "laptop running very slow",
            "computer is slow",
            "computer running slow",
            "pc is slow",
            "system is slow",
            "laptop very slow",
            "my laptop is running slow"
        ]
    ):

        return {
            "found": True,
            "question": user_issue,
            "category": "Hardware",

            "steps": [
                "Close unnecessary applications.",
                "Check available storage space.",
                "Restart the computer.",
                "Check whether background applications are consuming resources.",
                "Try using the computer again."
            ],

            "resolution": (
                "If the performance issue continues, "
                "the ticket should be escalated to Desktop Support."
            ),

            "support_team": "Desktop Support"
        }


    # =====================================================
    # UNKNOWN ISSUE
    # =====================================================

    return {
        "found": False,
        "question": user_issue,
        "category": "Unknown",

        "steps": [
            "Please describe your IT issue in more detail."
        ],

        "resolution": (
            "IT Helpdesk will investigate the issue."
        ),

        "support_team": "IT Helpdesk"
    }