import streamlit as st
import joblib
import re
import pandas as pd
import os

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

        st.dataframe(history)

        st.subheader("Dashboard Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Predictions", len(history))

        col2.metric("Unique Categories", history["Category"].nunique())

        col3.metric("Unique Teams", history["Assigned Team"].nunique())
