import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
df =pd.read_csv("Bird_Monitoring_Data_FOREST.XLSX - ANTI.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.time
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce').dt.time
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
df.dropna(subset=['common_name', 'date'], inplace=True)
print("Shape:", df.shape)
print("Missing values:\n", df.isnull().sum())
print("Top 10 most observed birds:\n", df['common_name'].value_counts().head(10))
top_species = df['common_name'].value_counts().head(10)
sns.barplot(x=top_species.values, y=top_species.index, palette='crest')
plt.title("Top 10 Most Observed Bird Species")
plt.xlabel("Number of Observations")
plt.tight_layout()
plt.show()