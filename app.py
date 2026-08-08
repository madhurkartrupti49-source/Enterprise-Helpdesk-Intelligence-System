import streamlit as st
import joblib
import re
import pandas as pd
import os
import plotly.express as px



def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.strip()
    return text



st.set_page_config(
    page_title="Enterprise Helpdesk Intelligence System"
)
# Professional AI Dashboard Styling
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #f5f8fc, #eaf2fb);
}

/* Main container */
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Main Title */
h1 {
    color: #17324d;
    font-weight: 800;
    text-align: center;
    letter-spacing: 0.5px;
}

/* Headings */
h2, h3 {
    color: #17324d;
    font-weight: 700;
}

/* Normal text */
p, label {
    color: #40566b;
}

/* Ticket input */
.stTextArea textarea {
    background-color: #ffffff !important;
    border: 1px solid #d5e1ed !important;
    border-radius: 12px !important;
    color: #17324d !important;
    box-shadow: 0 3px 12px rgba(40, 70, 100, 0.08);
}

/* Search box */
.stTextInput input {
    background-color: #ffffff !important;
    border: 1px solid #d5e1ed !important;
    border-radius: 10px !important;
    color: #17324d !important;
}

/* Buttons */
.stButton button {
    background: #2878d0;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.45rem 1.2rem;
    font-weight: 600;
    transition: 0.2s;
}

.stButton button:hover {
    background: #1f63ad;
    transform: translateY(-1px);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid #dbe6f0;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 5px 18px rgba(45, 75, 105, 0.09);
}

/* Metric value */
[data-testid="stMetricValue"] {
    color: #1769aa;
    font-weight: 750;
}

/* History table */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(40, 70, 100, 0.08);
}

/* Chart containers */
.stPlotlyChart {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid #dce7f1;
    border-radius: 16px;
    padding: 8px;
    box-shadow: 0 5px 18px rgba(45, 75, 105, 0.07);
}

/* Success message */
.stAlert {
    border-radius: 12px;
}

/* Download button */
.stDownloadButton button {
    border-radius: 10px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)




category_model = joblib.load("Models/category_model.pkl")
team_model = joblib.load("Models/team_model.pkl")
priority_model = joblib.load("Models/priority_model.pkl")
vectorizer = joblib.load("Models/tfidf_vectorizer.pkl")



st.title("Enterprise Helpdesk Intelligence System")
st.write("AI Powered Ticket Classification System")



# Initialize ticket
if "ticket_box" not in st.session_state:
    st.session_state.ticket_box = ""


# Function to update ticket description
def update_ticket():
    st.session_state.ticket_box = st.session_state.recommended_description


# Enter Ticket Description
ticket = st.text_area(
    "Enter Ticket Description",
    key="ticket_box"
)


st.write("💡 Recommended Ticket Descriptions")


recommendations = {

    "📧 Email Issue": [
        "Email is not working",
        "Outlook is not opening",
        "Emails are not sending",
        "Emails are not receiving",
        "Email client is not syncing"
    ],

    "🌐 VPN Issue": [
        "VPN is not connecting",
        "VPN connection keeps dropping",
        "Unable to access VPN",
        "VPN authentication failed",
        "VPN is very slow"
    ],

    "💻 Laptop Issue": [
        "Laptop is not turning on",
        "Laptop is running very slow",
        "Laptop screen is not working",
        "Laptop is overheating",
        "Laptop keeps restarting"
    ],

    "🔐 Security Issue": [
        "Antivirus detected a threat",
        "Suspicious activity detected",
        "Malware detected on system",
        "Phishing email received",
        "Security alert appeared"
    ],

    "🔑 Password Issue": [
        "Password reset required",
        "Unable to login",
        "Account is locked",
        "Password has expired",
        "Forgot my password"
    ]
}


selected_issue = st.selectbox(
    "Select Issue Type",
    ["-- Select an Issue --"] + list(recommendations.keys())
)


if selected_issue != "-- Select an Issue --":

    st.selectbox(
        "Select Recommended Description",
        recommendations[selected_issue],
        key="recommended_description",
        on_change=update_ticket
    )




if st.button("Predict"):

    if ticket.strip() == "":
        st.warning("Please enter a ticket description.")

    else:

        clean_ticket = clean_text(ticket)

        ticket_vector = vectorizer.transform([clean_ticket])

        # Smart Category Rules

        ticket_lower = ticket.lower()

        if any(word in ticket_lower for word in [
            "email",
            "outlook",
            "mailbox",
            "mail",
            "gmail"
        ]):
            category = "Software"

        elif any(word in ticket_lower for word in [
            "vpn",
            "wifi",
            "network",
            "internet",
            "router",
            "connection"
        ]):
            category = "Network"

        elif any(word in ticket_lower for word in [
            "password",
            "login",
            "account",
            "access",
            "permission"
        ]):
            category = "Access"

        elif any(word in ticket_lower for word in [
            "virus",
            "antivirus",
            "malware",
            "phishing",
            "security",
            "threat"
        ]):
            category = "Security"

        else:
            category = category_model.predict(ticket_vector)[0]
                     # Smart Team Rules

        if any(word in ticket_lower for word in [
            "email",
            "outlook",
            "mailbox",
            "mail",
            "gmail"
        ]):
            team = "Application Support"

        elif any(word in ticket_lower for word in [
            "vpn",
            "wifi",
            "network",
            "internet",
            "router",
            "connection"
        ]):
            team = "Network Team"

        elif any(word in ticket_lower for word in [
            "virus",
            "antivirus",
            "malware",
            "phishing",
            "security",
            "threat"
        ]):
            team = "Security Team"

        else:
            team = team_model.predict(ticket_vector)[0]

        priority = priority_model.predict(ticket_vector)[0]
        
    priority = priority_model.predict(ticket_vector)[0]


    probability = category_model.predict_proba(ticket_vector)
    confidence = max(probability[0]) * 100


    st.success("Prediction Completed Successfully!")


    st.subheader("Prediction Results")

    st.write(
            "Confidence :",
            round(confidence,2),
            "%"
        )

    st.write("📂 Category:", category)
    st.write("👨‍💻 Assigned Team:", team)
    st.write("⚡ Priority:", priority)


        # Save Prediction

    new_history = pd.DataFrame({

            "Ticket":[ticket],
            "Category":[category],
            "Assigned Team":[team],
            "Priority":[priority]

        })


    os.makedirs("Database", exist_ok=True)


    file_path = "Database/prediction.csv"


    if not os.path.exists(file_path):

            new_history.to_csv(
                file_path,
                index=False
            )

    else:

            new_history.to_csv(
                file_path,
                mode="a",
                header=False,
                index=False
            )


    st.success("Prediction Saved Successfully!")




st.subheader("Prediction History")


if os.path.exists("Database/prediction.csv"):

    history = pd.read_csv(
        "Database/prediction.csv"
    )


    search = st.text_input(
        " Search Ticket"
    )


    if search:

        filtered_history = history[
            history["Ticket"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]


        if len(filtered_history)>0:
            st.dataframe(filtered_history)

        else:
            st.warning(
                "No matching ticket found"
            )

    else:

        st.dataframe(history)
    st.subheader("Dashboard Summary")

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Predictions",
    len(history)
)


critical_count = len(
    history[history["Priority"] == "Critical"]
)

col2.metric(
    "Critical Tickets",
    critical_count
)


# Safe Top Category & Team

if len(history) > 0:

    top_category = history["Category"].mode().iloc[0]
    top_team = history["Assigned Team"].mode().iloc[0]

else:

    top_category = "No Data"
    top_team = "No Data"


col3.metric(
    "Top Category",
    top_category
)


col4.metric(
    "Top Team",
    top_team
)



st.subheader("Category Distribution")


if len(history) > 0:

    category_count = (
        history["Category"]
        .value_counts()
        .reset_index()
    )


    category_count.columns=[
        "Category",
        "Count"
    ]


    fig_cat = px.bar(
        category_count,
        x="Category",
        y="Count",
        color="Category",
        title="Category Distribution",
        template="plotly_white"
    )
    fig_cat.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)


    st.plotly_chart(
        fig_cat,
        use_container_width=True
    )


else:

    st.info("No data available for Category Distribution")



st.subheader("Priority Distribution")


if len(history) > 0:

    priority_count = (
        history["Priority"]
        .value_counts()
        .reset_index()
    )


    priority_count.columns=[
        "Priority",
        "Count"
    ]


    fig_pie = px.pie(
        priority_count,
        names="Priority",
        values="Count",
        title="Priority Distribution",
        template="plotly_white"
    )
    fig_pie.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)



    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )


else:

    st.info("No data available for Priority Distribution")



st.subheader("Assigned Team Distribution")


if len(history) > 0:

    team_count = (
        history["Assigned Team"]
        .value_counts()
        .reset_index()
    )


    team_count.columns=[
        "Assigned Team",
        "Count"
    ]


    fig_team = px.bar(
        team_count,
        x="Assigned Team",
        y="Count",
        color="Assigned Team",
        title="Assigned Team Distribution",
        template="plotly_white"
    )
    fig_team.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)


    st.plotly_chart(
        fig_team,
        use_container_width=True
    )


else:

    st.info("No data available for Team Distribution")



st.subheader("Download Prediction History")


with open(
    "Database/prediction.csv",
    "rb"
) as file:

    st.download_button(

        label="📥 Download Prediction History",

        data=file,

        file_name="prediction_history.csv",

        mime="text/csv"

    )


if st.button("🗑️ Clear Prediction History"):

    empty_history = pd.DataFrame(
        columns=[
            "Ticket",
            "Category",
            "Assigned Team",
            "Priority"
        ]
    )

    empty_history.to_csv(
        "Database/prediction.csv",
        index=False
    )

    st.success("Prediction History Cleared Successfully!")


st.subheader("📈 Model Performance")


performance = pd.DataFrame({

    "Model": [
        "Category Model",
        "Team Model",
        "Priority Model"
    ],

    "Accuracy": [
        "100%",
        "100%",
        "25.10%"
    ]

})


st.dataframe(
    performance,
    use_container_width=True
) 

