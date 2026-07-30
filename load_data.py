import pandas as pd

df = pd.read_csv("Data/helpdesk_tickets.csv")

print(df.head())

print("\nDataset Information:")
print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nCategory Count:")
print(df["Category"].value_counts())

print("\nPriority Count:")
print(df["Priority"].value_counts())

print("\nStatus Count:")
print(df["Status"].value_counts())

df_copy = df.copy()
print(df.duplicated().sum())