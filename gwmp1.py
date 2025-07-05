import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(layout="wide")
st.title("🌿 Bird Observation Dashboard - GWMP (with Scientific Names, Weather & ID Method)")

# Load dataset
FILE = "Bird_Monitoring_Data_FOREST.XLSX - GWMP.csv"
try:
    df = pd.read_csv(FILE)
except FileNotFoundError:
    st.error(f"❌ File '{FILE}' not found.")
    st.stop()

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert date/time/count fields
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
for time_col in ['start_time', 'end_time']:
    if time_col in df.columns:
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce').dt.time

# Drop incomplete rows
df.dropna(subset=['date', 'common_name', 'initial_three_min_cnt'], inplace=True)

# Combine common and scientific names
df['full_name'] = df['common_name']
if 'scientific_name' in df.columns:
    df['scientific_name'] = df['scientific_name'].fillna("").str.strip()
    df['full_name'] = df.apply(
        lambda row: f"{row['common_name']} ({row['scientific_name']})" if row['scientific_name'] else row['common_name'],
        axis=1
    )

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Year filter
year_options = sorted(df['date'].dt.year.unique())
year = st.sidebar.selectbox("Select Year", year_options)

# Species filter
species_options = sorted(df['full_name'].unique())
species = st.sidebar.selectbox("Select Bird Species", species_options)

# Interval Length filter
if 'interval_length' in df.columns:
    interval_options = sorted(df['interval_length'].dropna().astype(str).unique())
    interval = st.sidebar.selectbox("Select Interval Length", interval_options)
else:
    interval = None

# Temperature filter
if 'temperature' in df.columns:
    min_temp = int(df['temperature'].min())
    max_temp = int(df['temperature'].max())
    temp_range = st.sidebar.slider("Select Temperature Range (°C)", min_value=min_temp, max_value=max_temp,
                                   value=(min_temp, max_temp))
else:
    temp_range = None

# Humidity filter
if 'humidity' in df.columns:
    min_hum = int(df['humidity'].min())
    max_hum = int(df['humidity'].max())
    hum_range = st.sidebar.slider("Select Humidity Range (%)", min_value=min_hum, max_value=max_hum,
                                  value=(min_hum, max_hum))
else:
    hum_range = None

# ID Method filter
if 'id_method' in df.columns:
    id_methods = df['id_method'].dropna().unique().tolist()
    id_method = st.sidebar.selectbox("Select ID Method", sorted(id_methods))
else:
    id_method = None

# Date Range filter
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
filtered = df.copy()
filtered = filtered[filtered['date'].dt.year == year]
filtered = filtered[filtered['full_name'] == species]

if interval:
    filtered = filtered[filtered['interval_length'].astype(str) == interval]

if temp_range:
    filtered = filtered[(filtered['temperature'] >= temp_range[0]) & (filtered['temperature'] <= temp_range[1])]

if hum_range:
    filtered = filtered[(filtered['humidity'] >= hum_range[0]) & (filtered['humidity'] <= hum_range[1])]

if id_method:
    filtered = filtered[filtered['id_method'] == id_method]

if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered['date'] >= start) & (filtered['date'] <= end)]

# Display section
st.subheader(f"📅 Observations for {species} in {year}")
st.write(f"🔢 Total Records: {len(filtered)}")
st.write(f"🐦 Total Bird Count: {int(filtered['initial_three_min_cnt'].sum())}")

if not filtered.empty:
    st.subheader("📈 Daily Bird Count")
    daily_counts = filtered.groupby('date')['initial_three_min_cnt'].sum()
    st.line_chart(daily_counts)

    st.subheader("📊 Filtered Observation Data")
    st.dataframe(filtered[['date', 'full_name', 'initial_three_min_cnt', 'temperature', 'humidity', 'id_method']])
else:
    st.warning("⚠️ No data available for the selected filters.")

# Top 10 chart
st.subheader("🏆 Top 10 Most Observed Bird Species (Overall)")
top_species = df.groupby('full_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=top_species.values, y=top_species.index, palette='crest', ax=ax)
ax.set_title("Top 10 Bird Species")
ax.set_xlabel("Total Count")
st.pyplot(fig)
