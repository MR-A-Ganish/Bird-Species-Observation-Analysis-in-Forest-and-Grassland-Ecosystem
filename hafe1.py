import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(layout="wide")
st.title("🪶 HAFE Bird Observation Dashboard with Filters")

# Load the CSV
file_path = "Bird_Monitoring_Data_FOREST.XLSX - HAFE.csv"
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f"❌ File '{file_path}' not found.")
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

# Drop rows missing essential info
df.dropna(subset=['common_name', 'date'], inplace=True)

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Year
years = sorted(df['date'].dt.year.dropna().unique())
selected_year = st.sidebar.selectbox("Select Year", years)

# Species
species_list = sorted(df['common_name'].dropna().unique())
selected_species = st.sidebar.selectbox("Select Bird Species", species_list)

# Interval
if 'interval_length' in df.columns:
    interval_list = sorted(df['interval_length'].dropna().astype(str).unique())
    selected_interval = st.sidebar.selectbox("Select Interval Length", interval_list)
else:
    selected_interval = None

# ID Method
if 'id_method' in df.columns:
    id_methods = sorted(df['id_method'].dropna().astype(str).unique())
    selected_id_method = st.sidebar.selectbox("Select ID Method", id_methods)
else:
    selected_id_method = None

# Date Range
min_date, max_date = df['date'].min(), df['date'].max()
selected_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Temperature & Humidity Range (optional)
if 'temperature' in df.columns and df['temperature'].notna().any():
    temp_min, temp_max = int(df['temperature'].min()), int(df['temperature'].max())
    temp_range = st.sidebar.slider("Temperature (°C)", temp_min, temp_max, (temp_min, temp_max))
else:
    temp_range = None

if 'humidity' in df.columns and df['humidity'].notna().any():
    hum_min, hum_max = int(df['humidity'].min()), int(df['humidity'].max())
    hum_range = st.sidebar.slider("Humidity (%)", hum_min, hum_max, (hum_min, hum_max))
else:
    hum_range = None

# --- Apply Filters ---
filtered = df[
    (df['date'].dt.year == selected_year) &
    (df['common_name'] == selected_species)
]

if selected_interval:
    filtered = filtered[filtered['interval_length'].astype(str) == selected_interval]

if selected_id_method:
    filtered = filtered[filtered['id_method'].astype(str) == selected_id_method]

if len(selected_range) == 2:
    start_date, end_date = pd.to_datetime(selected_range[0]), pd.to_datetime(selected_range[1])
    filtered = filtered[(filtered['date'] >= start_date) & (filtered['date'] <= end_date)]

if temp_range:
    filtered = filtered[(df['temperature'] >= temp_range[0]) & (df['temperature'] <= temp_range[1])]

if hum_range:
    filtered = filtered[(df['humidity'] >= hum_range[0]) & (df['humidity'] <= hum_range[1])]

# --- Display Results ---
st.subheader(f"📊 Observations for '{selected_species}' in {selected_year}")
st.write(f"🔢 Total Records: {len(filtered)}")
st.write(f"🐦 Total Bird Count: {filtered['initial_three_min_cnt'].sum()}")

# Chart
if not filtered.empty:
    daily = filtered.groupby('date')['initial_three_min_cnt'].sum()
    st.line_chart(daily)

    st.dataframe(filtered[['date', 'common_name', 'scientific_name' if 'scientific_name' in df.columns else 'common_name', 
                           'interval_length' if 'interval_length' in df.columns else None,
                           'temperature' if 'temperature' in df.columns else None,
                           'humidity' if 'humidity' in df.columns else None,
                           'initial_three_min_cnt']])
else:
    st.warning("No data available for selected filters.")

# --- Top Species Chart ---
st.subheader("🏆 Top 10 Bird Species (Overall)")
top_species = df.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_species)
