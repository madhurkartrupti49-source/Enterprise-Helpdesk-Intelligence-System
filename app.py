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

st.set_page_config(page_title="Enterprise Helpdesk Intelligence System")
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
        category_probability = category_model.predict_proba(ticket_vector)
        #st.write(category_probability)


        confidence = max(category_probability[0]) * 100
        

        st.success("Prediction Completed Successfully!")

        st.subheader("Prediction Results")
        st.write("Confidence :", round(confidence, 2), "%")

        st.write("📂 Category:", category)
        st.write("👨‍💻 Assigned Team:", team)
        st.write("⚡ Priority:", priority)

        history = pd.DataFrame({
            "Ticket": [ticket],
            "Category": [category],
            "Assigned Team": [team],
            "Priority": [priority]
        })

        history.to_csv(
            "Database/prediction.csv",
            mode="a",
            header=False,
            index=False
        )

        st.success("Prediction Saved Successfully!")
        st.subheader("Prediction History")

        history = pd.read_csv("Database/prediction.csv")

        search = st.text_input("🔍 Search Ticket")

        if search:
            filtered_history = history[
        history["Ticket"].str.contains(search, case=False, na=False)
    ]
    st.dataframe(filtered_history)
else:
    st.dataframe(history)

    st.subheader("Dashboard Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Predictions", len(history))

    col2.metric("Unique Categories", history["Category"].nunique())

    col3.metric("Unique Teams", history["Assigned Team"].nunique())

    st.subheader("Category Distribution")

    category_count = history["Category"].value_counts().reset_index()
    category_count.columns = ["Category", "Count"]

    fig_Cat = px.bar(
                    category_count,
                    x="Category",
                    y="Count",
                    color="Category",
                    title="Category Distribution"
                )

    st.plotly_chart(fig_Cat, use_container_width=True)
    st.subheader("Priority Distribution")

    priority_count = history["Priority"].value_counts().reset_index()
    priority_count.columns = ["Priority", "Count"]

    fig_pie = px.pie(
    priority_count,
    names="Priority",
    values="Count",
    title="Priority Distribution"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Assigned Team Distribution")

    team_count = history["Assigned Team"].value_counts().reset_index()
    team_count.columns = ["Assigned Team", "Count"]

    fig_team = px.bar(
        team_count,
        x="Assigned Team",
        y="Count",
        color="Assigned Team",
        title="Assigned Team Distribution"
    )

    st.plotly_chart(fig_team, use_container_width=True)

    st.subheader("Download Prediction History")

    with open("Database/prediction.csv", "rb") as file:
        st.download_button(
        label="📥 Download Prediction History",
        data=file,
        file_name="prediction_history.csv",
        mime="text/csv"
    )