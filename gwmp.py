import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("Bird_Monitoring_Data_FOREST.XLSX - GWMP.csv")

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert date and time fields
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.time
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce').dt.time

# Convert bird count to numeric
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')

# Drop rows missing critical values
df.dropna(subset=['common_name', 'date'], inplace=True)

# Combine common and scientific names
df['full_name'] = df['common_name']
if 'scientific_name' in df.columns:
    df['scientific_name'] = df['scientific_name'].fillna("").str.strip()
    df['full_name'] = df.apply(
        lambda row: f"{row['common_name']} ({row['scientific_name']})" if row['scientific_name'] else row['common_name'],
        axis=1
    )

# Summary
print("Shape:", df.shape)
print("Missing values:\n", df.isnull().sum())
print("Top 10 most observed birds:\n", df['full_name'].value_counts().head(10))

# Plot top 10 species
top_species = df['full_name'].value_counts().head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top_species.values, y=top_species.index, palette='crest')
plt.title("Top 10 Most Observed Bird Species (with Scientific Names)")
plt.xlabel("Number of Observations")
plt.tight_layout()
plt.show()
