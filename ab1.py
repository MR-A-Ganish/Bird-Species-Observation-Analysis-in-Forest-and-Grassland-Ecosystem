import streamlit as st
import pandas as pd

# Page config
st.set_page_config(layout="wide")
st.title("🐦 Bird Species Observation Dashboard")

# Load CSV
try:
    df = pd.read_csv("Bird_Monitoring_Data_FOREST.XLSX - ANTI.csv")
except FileNotFoundError:
    st.error("❌ File 'Bird_Monitoring_Data_FOREST.XLSX - ANTI.csv' not found in current directory.")
    st.stop()

# Clean column names: lowercase, no spaces
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Show column names for verification
st.sidebar.subheader("🗂 Available Columns")
st.sidebar.write(df.columns.tolist())

# Check required columns
required = ['date', 'common_name', 'initial_three_min_cnt', 'interval_length']
missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

# Parse date column
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])

# Clean initial count
df['initial_three_min_cnt'] = df['initial_three_min_cnt'].apply(lambda x: str(x).lower() == 'true').astype(int)

# Parse interval column for filtering
df['interval_length'] = df['interval_length'].astype(str).str.strip()

# Optional: parse time columns if needed
for time_col in ['start_time', 'end_time']:
    if time_col in df.columns:
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce').dt.time

# Sidebar filters
st.sidebar.subheader("🔍 Filters")
year_options = sorted(df['date'].dt.year.unique())
species_options = sorted(df['common_name'].dropna().unique())
interval_options = sorted(df['interval_length'].unique())

year = st.sidebar.selectbox("Select Year", year_options)
species = st.sidebar.selectbox("Select Bird Species", species_options)
interval = st.sidebar.selectbox("Select Interval Length", interval_options)

# Date range filter
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
if len(date_range) == 2:
    start, end = date_range
    df = df[(df['date'] >= pd.to_datetime(start)) & (df['date'] <= pd.to_datetime(end))]

# Filter data
filtered = df[
    (df['date'].dt.year == year) &
    (df['common_name'] == species) &
    (df['interval_length'] == interval)
]

st.subheader(f"📅 Observations for '{species.title()}' in {year} at '{interval}' intervals")
st.write(f"🔢 Total Records: {len(filtered)} | 🐦 Total Count: {filtered['initial_three_min_cnt'].sum()}")

# Line chart by date
if not filtered.empty:
    daily_interval_counts = filtered.groupby(['date'])['initial_three_min_cnt'].sum()
    st.line_chart(daily_interval_counts)
    
    # Optional table
    st.dataframe(filtered[['date', 'interval_length', 'initial_three_min_cnt']])
else:
    st.warning("No data available for the selected filters.")

# Top 10 species overall
st.subheader("🏆 Top 10 Most Observed Bird Species")
top_species = df.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_species)
