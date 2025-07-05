import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(layout="wide")
st.title("🌾 ANTI Grassland Bird Observation Dashboard")

# Load dataset
file_path = "Bird_Monitoring_Data_GRASSLAND.XLSX - ANTI.csv"
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f"❌ File not found: {file_path}")
    st.stop()

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert data types
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.time
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce').dt.time
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')

# Drop rows with missing essential data
df.dropna(subset=['common_name', 'date'], inplace=True)

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Year
year_options = sorted(df['date'].dt.year.dropna().unique())
year = st.sidebar.selectbox("Select Year", year_options)

# Species
species_options = sorted(df['common_name'].dropna().unique())
species = st.sidebar.selectbox("Select Bird Species", species_options)

# Interval Length
interval_options = sorted(df['interval_length'].dropna().astype(str).unique())
interval = st.sidebar.selectbox("Select Interval Length", interval_options)

# Date Range
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Temperature Range
if 'temperature' in df.columns:
    temp_min, temp_max = int(df['temperature'].min()), int(df['temperature'].max())
    temperature = st.sidebar.slider("Temperature Range (°C)", temp_min, temp_max, (temp_min, temp_max))
else:
    temperature = None

# Humidity Range
if 'humidity' in df.columns:
    hum_min, hum_max = int(df['humidity'].min()), int(df['humidity'].max())
    humidity = st.sidebar.slider("Humidity Range (%)", hum_min, hum_max, (hum_min, hum_max))
else:
    humidity = None

# ID Method
if 'id_method' in df.columns:
    id_methods = sorted(df['id_method'].dropna().unique())
    id_method = st.sidebar.selectbox("Select ID Method", id_methods)
else:
    id_method = None

# Apply Filters
filtered = df[
    (df['date'].dt.year == year) &
    (df['common_name'] == species) &
    (df['interval_length'].astype(str) == interval)
]

if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered['date'] >= start) & (filtered['date'] <= end)]

if temperature:
    filtered = filtered[(filtered['temperature'] >= temperature[0]) & (filtered['temperature'] <= temperature[1])]

if humidity:
    filtered = filtered[(filtered['humidity'] >= humidity[0]) & (filtered['humidity'] <= humidity[1])]

if id_method:
    filtered = filtered[filtered['id_method'] == id_method]

# Display Results
st.subheader(f"📅 Observations for '{species}' in {year}")
st.write(f"🔢 Total Records: {len(filtered)} | 🐦 Total Bird Count: {filtered['initial_three_min_cnt'].sum()}")

if not filtered.empty:
    daily_counts = filtered.groupby('date')['initial_three_min_cnt'].sum()
    st.line_chart(daily_counts)
    st.dataframe(filtered[['date', 'interval_length', 'initial_three_min_cnt', 'temperature', 'humidity', 'id_method']])
else:
    st.warning("No data available for the selected filters.")

# Top 10 species overall
st.subheader("🏆 Top 10 Most Observed Bird Species (All Data)")
top_species = df.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_species)
