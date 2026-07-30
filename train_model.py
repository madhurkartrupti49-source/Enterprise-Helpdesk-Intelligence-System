import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
df = pd.read_csv("Data/helpdesk_tickets.csv")

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.strip()
    return text

df["Description"] = df["Description"].apply(clean_text)
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(df["Description"])
y = df["Category"]
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)
print("Training Data:", X_train.shape)
print("Testing Data:", X_test.shape)
