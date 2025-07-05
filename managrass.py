import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("Bird_Monitoring_Data_GRASSLAND.XLSX - MANA.csv")

# Clean and preprocess
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.time
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce').dt.time
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
df.dropna(subset=['common_name', 'date'], inplace=True)

# Display summary
print("Shape:", df.shape)
print("\nMissing values:\n", df.isnull().sum())
print("\nTop 10 most observed birds:\n", df['common_name'].value_counts().head(10))

# Plot: Top 10 bird species
top_species = df['common_name'].value_counts().head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top_species.values, y=top_species.index, palette='crest')
plt.title("Top 10 Most Observed Bird Species - MANA")
plt.xlabel("Number of Observations")
plt.tight_layout()
plt.show()
