import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv("Bird_Monitoring_Data_FOREST.XLSX - CATO.csv")

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert data types
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.time
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce').dt.time
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')

# Drop missing critical fields
df.dropna(subset=['common_name', 'date'], inplace=True)

# Add year and month columns
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# Fill missing count with 0
df['initial_three_min_cnt'].fillna(0, inplace=True)

# -------------------------------
# 1. Top 10 most counted species
top_species = df.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_species.values, y=top_species.index, palette='crest')
plt.title("Top 10 Most Counted Bird Species")
plt.xlabel("Total Bird Count")
plt.tight_layout()
plt.show()

# -------------------------------
# 2. Species richness per site
if 'site_name' in df.columns:
    richness = df.groupby('site_name')['common_name'].nunique().sort_values(ascending=False)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=richness.index, y=richness.values, palette='viridis')
    plt.title("Species Richness by Site")
    plt.ylabel("Number of Unique Species")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# -------------------------------
# 3. Top 10 observers
if 'observer' in df.columns:
    top_observers = df.groupby('observer')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=top_observers.values, y=top_observers.index, palette='mako')
    plt.title("Top 10 Observers by Bird Count")
    plt.xlabel("Total Bird Count")
    plt.tight_layout()
    plt.show()

# -------------------------------
# 4. Monthly trend (heatmap)
monthly_trend = df.groupby(['year', 'month'])['initial_three_min_cnt'].sum().unstack().fillna(0)

plt.figure(figsize=(10, 6))
sns.heatmap(monthly_trend, cmap='YlGnBu', annot=True, fmt=".0f")
plt.title("Monthly Bird Observation Trend")
plt.xlabel("Month")
plt.ylabel("Year")
plt.tight_layout()
plt.show()

# -------------------------------
# 5. Weather correlation heatmap
if 'temperature' in df.columns and 'humidity' in df.columns:
    corr = df[['temperature', 'humidity', 'initial_three_min_cnt']].dropna().corr()
    plt.figure(figsize=(6, 4))
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title("Correlation: Bird Count vs Weather")
    plt.tight_layout()
    plt.show()
