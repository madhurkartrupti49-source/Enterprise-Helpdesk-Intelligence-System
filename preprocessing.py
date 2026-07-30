import pandas as pd
import re

df = pd.read_csv("Data/helpdesk_tickets.csv")
df_copy = df.copy()
print("Duplicate Rows:", df_copy.duplicated().sum())

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.strip()
    return text
df_copy["Description"] = df_copy["Description"].apply(clean_text)
print(df_copy["Description"].head())