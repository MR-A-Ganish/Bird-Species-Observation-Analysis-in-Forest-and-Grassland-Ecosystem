import streamlit as st
import pandas as pd

# Set up the page
st.set_page_config(layout="wide")
st.title("🦜 MONO - Bird Species Observation Dashboard")

# Load the dataset
file_path = "Bird_Monitoring_Data_FOREST.XLSX - MONO.csv"
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f"❌ File '{file_path}' not found.")
    st.stop()

# Clean and preprocess data
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.time
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce').dt.time
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
df['temperature'] = pd.to_numeric(df.get('temperature'), errors='coerce')
df['humidity'] = pd.to_numeric(df.get('humidity'), errors='coerce')

df.dropna(subset=['common_name', 'date'], inplace=True)

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Year Filter
year_options = sorted(df['date'].dt.year.dropna().unique())
year = st.sidebar.selectbox("Select Year", year_options)

# Species Filter
species_options = sorted(df['common_name'].dropna().unique())
species = st.sidebar.selectbox("Select Bird Species", species_options)

# Interval Filter
interval_options = sorted(df['interval_length'].dropna().unique()) if 'interval_length' in df.columns else []
interval = st.sidebar.selectbox("Select Interval Length", interval_options) if interval_options else None

# ID Method Filter (if present)
if 'id_method' in df.columns:
    id_method_options = sorted(df['id_method'].dropna().unique())
    id_method = st.sidebar.selectbox("Select ID Method", id_method_options)
else:
    id_method = None

# Temperature Range
if 'temperature' in df.columns:
    min_temp = int(df['temperature'].min())
    max_temp = int(df['temperature'].max())
    temp_range = st.sidebar.slider("Temperature (°C)", min_temp, max_temp, (min_temp, max_temp))
else:
    temp_range = None

# Humidity Range
if 'humidity' in df.columns:
    min_hum = int(df['humidity'].min())
    max_hum = int(df['humidity'].max())
    hum_range = st.sidebar.slider("Humidity (%)", min_hum, max_hum, (min_hum, max_hum))
else:
    hum_range = None

# Date Range Filter
min_date = df['date'].min()
max_date = df['date'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply all filters
filtered = df[
    (df['date'].dt.year == year) &
    (df['common_name'] == species)
]

if interval:
    filtered = filtered[filtered['interval_length'] == interval]

if id_method:
    filtered = filtered[filtered['id_method'] == id_method]

if temp_range:
    filtered = filtered[(df['temperature'] >= temp_range[0]) & (df['temperature'] <= temp_range[1])]

if hum_range:
    filtered = filtered[(df['humidity'] >= hum_range[0]) & (df['humidity'] <= hum_range[1])]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[(filtered['date'] >= pd.to_datetime(start_date)) & (filtered['date'] <= pd.to_datetime(end_date))]

# Main Display
st.subheader(f"📅 Filtered Observations for {species} in {year}")
st.write(f"🔢 Records: {len(filtered)} | 🐦 Total Bird Count: {filtered['initial_three_min_cnt'].sum()}")

if not filtered.empty:
    # Line Chart of Bird Count by Date
    daily_counts = filtered.groupby('date')['initial_three_min_cnt'].sum()
    st.line_chart(daily_counts)

    # Data Table
    st.dataframe(filtered[['date', 'common_name', 'scientific_name', 'initial_three_min_cnt',
                           'interval_length', 'temperature', 'humidity', 'id_method']], use_container_width=True)
else:
    st.warning("⚠️ No data available for the selected filters.")

# Global Analysis
st.subheader("🏆 Top 10 Most Observed Bird Species (Overall)")
top_species = df.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_species)
