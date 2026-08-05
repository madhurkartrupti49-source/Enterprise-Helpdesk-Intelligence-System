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

st.markdown(
"""
<style>

/* Full Background */

.stApp {

    background:
    linear-gradient(
        135deg,
        #0f172a,
        #1e3a5f,
        #0b1120
    );

}



/* Main Container */

.block-container {

    padding-top:2rem;

}



/* Main Title */

h1 {

    color:#00eaff !important;

    text-align:center;

    font-size:42px;

    font-weight:900;

    text-shadow:

    0 0 10px #00eaff,

    0 0 25px #00eaff;

}



/* Headings */

h2,h3 {

    color:white !important;

    font-weight:800;

    letter-spacing:1px;

    text-shadow:

    0 0 8px rgba(255,255,255,0.5);

}



/* Normal Text */

p,label {

    color:#f8fafc !important;

    font-weight:500;

}



/* Text Area */
/* Ticket Description Box */

.stTextArea textarea {

    background-color: #ffffff !important;

    color: #111827 !important;

    font-size:16px;

    font-weight:600;

    border-radius:15px;

    border:2px solid #00eaff;

}


/* Placeholder Text */

.stTextArea textarea::placeholder {

    color:#64748b !important;

    font-weight:500;

}



/* Search Box */

.stTextInput input {

    background-color:#ffffff !important;

    color:#111827 !important;

    font-size:16px;

    font-weight:600;

    border-radius:12px;

    border:2px solid #00eaff;

}


.stTextInput input::placeholder {

    color:#64748b !important;

}




/* Search Box */

.stTextInput input {

    background:

    rgba(255,255,255,0.12);

    color:white;

    border-radius:12px;

}



/* Metric Cards */

div[data-testid="stMetric"] {

    background:

    linear-gradient(

    135deg,

    rgba(255,255,255,0.18),

    rgba(255,255,255,0.05)

    );


    border-radius:20px;


    padding:20px;


    border:1px solid rgba(0,234,255,0.5);


    box-shadow:

    0 0 20px rgba(0,234,255,0.25);

}



/* Metric Numbers */

div[data-testid="stMetricValue"] {

    color:#00ffcc !important;

    font-size:35px;

    font-weight:900;

}



/* Buttons */

.stButton button {


    background:

    linear-gradient(

    90deg,

    #00c6ff,

    #0072ff

    );


    color:white;

    font-weight:800;

    border-radius:12px;


    box-shadow:

    0 0 15px rgba(0,198,255,0.6);

}



/* Download Button */

.stDownloadButton button {


    background:

    linear-gradient(

    90deg,

    #22c55e,

    #16a34a

    );


    color:white;

    font-weight:700;

    border-radius:12px;

}



/* Data Table */

[data-testid="stDataFrame"] {

    border-radius:15px;

    overflow:hidden;

}



/* Alert */

.stAlert {

    border-radius:15px;

}
/* Chart Containers */

div[data-testid="stPlotlyChart"] {

    background:
    rgba(255,255,255,0.08);

    border-radius:25px;

    padding:15px;

    border:1px solid rgba(0,234,255,0.3);

    box-shadow:
    0 0 20px rgba(0,234,255,0.15);

}


/* Prediction History Table */

div[data-testid="stDataFrame"] {

    background:
    rgba(255,255,255,0.08);

    border-radius:20px;

    padding:10px;

}


/* Info Boxes */

.stAlert {

    background:
    rgba(255,255,255,0.12);

    border-radius:20px;

}



/* Space between sections */

h2,h3 {

    margin-top:25px;

}


</style>
""",
unsafe_allow_html=True
)



category_model = joblib.load("Models/category_model.pkl")
team_model = joblib.load("Models/team_model.pkl")
priority_model = joblib.load("Models/priority_model.pkl")
vectorizer = joblib.load("Models/tfidf_vectorizer.pkl")



st.title("Enterprise Helpdesk Intelligence System")
st.write("AI Powered Ticket Classification System")



ticket = st.text_area("Enter Ticket Description")



if st.button("Predict"):

    if ticket.strip() == "":
        st.warning("Please enter a ticket description.")

    else:

        clean_ticket = clean_text(ticket)

        ticket_vector = vectorizer.transform([clean_ticket])


        category = category_model.predict(ticket_vector)[0]
        team = team_model.predict(ticket_vector)[0]
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
        template="plotly_dark"
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
        template="plotly_dark"
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
        template="plotly_dark"
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

