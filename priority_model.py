import pandas as pd
import re
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report


df = pd.read_csv("Data/helpdesk_tickets.csv")

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.strip()
    return text

df["Description"] = df["Description"].apply(clean_text)
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(df["Description"])
y = df["Priority"]
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)
print("Training Data:", X_train.shape)
print("Testing Data:", X_test.shape)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Model Accuracy:", accuracy)
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("Model Training Completed Successfully!")
joblib.dump(model, "Models/priority_model.pkl")
joblib.dump(vectorizer, "Models/tfidf_vectorizer.pkl")
print("Model Saved Successfully!")
new_ticket = ["User cannot connect to office VPN"]
new_ticket = [clean_text(text) for text in new_ticket]
new_ticket_vector = vectorizer.transform(new_ticket)
prediction = model.predict(new_ticket_vector)
print("Predicted priority:", prediction[0])
new_ticket = ["User cannot connect to office VPN"]

new_ticket = [clean_text(text) for text in new_ticket]

new_ticket_vector = vectorizer.transform(new_ticket)

prediction = model.predict(new_ticket_vector)

print("Predicted Priority:", prediction[0])