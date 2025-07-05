import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv("Bird_Monitoring_Data_FOREST.XLSX - HAFE.csv")

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert date and time columns
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.time
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce').dt.time

# Convert bird count to numeric
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')

# Drop rows with missing common_name or date
df.dropna(subset=['common_name', 'date'], inplace=True)

# Print dataset summary
print("Shape:", df.shape)
print("Missing values:\n", df.isnull().sum())
print("Top 10 most observed birds:\n", df['common_name'].value_counts().head(10))

# Plot top 10 most observed bird species
top_species = df['common_name'].value_counts().head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top_species.values, y=top_species.index, palette='crest')
plt.title("Top 10 Most Observed Bird Species (HAFE)")
plt.xlabel("Number of Observations")
plt.tight_layout()
plt.show()
