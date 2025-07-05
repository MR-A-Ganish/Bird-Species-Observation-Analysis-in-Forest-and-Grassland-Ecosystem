import streamlit as st
import pandas as pd

# Page config
st.set_page_config(layout="wide")
st.title("🦜 Bird Observation Dashboard - NACE")

# Load data
try:
    df = pd.read_csv("Bird_Monitoring_Data_FOREST.XLSX - NACE.csv")
except FileNotFoundError:
    st.error("❌ File not found.")
    st.stop()

# Clean and preprocess
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert data types
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.time
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce').dt.time
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
df['temperature'] = pd.to_numeric(df.get('temperature'), errors='coerce')
df['humidity'] = pd.to_numeric(df.get('humidity'), errors='coerce')

# Drop rows with missing key values
df.dropna(subset=['common_name', 'date', 'initial_three_min_cnt'], inplace=True)

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Year Filter
year_options = sorted(df['date'].dt.year.dropna().unique())
year = st.sidebar.selectbox("Select Year", year_options)

# Species Filter
species_options = sorted(df['common_name'].dropna().unique())
species = st.sidebar.selectbox("Select Bird Species", species_options)

# Interval Filter (if exists)
interval_options = sorted(df['interval_length'].dropna().unique()) if 'interval_length' in df.columns else []
if interval_options:
    interval = st.sidebar.selectbox("Select Interval Length", interval_options)
else:
    interval = None

# Temperature Range Filter
if 'temperature' in df.columns:
    min_temp = int(df['temperature'].min())
    max_temp = int(df['temperature'].max())
    temp_range = st.sidebar.slider("Select Temperature Range (°C)", min_temp, max_temp, (min_temp, max_temp))
else:
    temp_range = None

# Humidity Range Filter
if 'humidity' in df.columns:
    min_hum = int(df['humidity'].min())
    max_hum = int(df['humidity'].max())
    hum_range = st.sidebar.slider("Select Humidity Range (%)", min_hum, max_hum, (min_hum, max_hum))
else:
    hum_range = None

# Date range filter
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
filtered = df.copy()
filtered = filtered[filtered['date'].dt.year == year]
filtered = filtered[filtered['common_name'] == species]
if interval and 'interval_length' in df.columns:
    filtered = filtered[filtered['interval_length'] == interval]
if temp_range:
    filtered = filtered[filtered['temperature'].between(*temp_range)]
if hum_range:
    filtered = filtered[filtered['humidity'].between(*hum_range)]
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered['date'] >= start) & (filtered['date'] <= end)]

# Display summary
st.subheader(f"📅 Observations for '{species}' in {year}")
st.write(f"🔢 Total Records: {len(filtered)}")
st.write(f"🐦 Total Bird Count: {filtered['initial_three_min_cnt'].sum()}")

# Show filtered data
if not filtered.empty:
    st.dataframe(filtered[['date', 'common_name', 'initial_three_min_cnt', 'temperature', 'humidity']])
    # Daily counts chart
    daily = filtered.groupby('date')['initial_three_min_cnt'].sum()
    st.line_chart(daily)
else:
    st.warning("No records match the selected filters.")

# Top species chart (entire dataset)
st.subheader("🏆 Top 10 Most Observed Species (Overall)")
top_species = df.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_species)
