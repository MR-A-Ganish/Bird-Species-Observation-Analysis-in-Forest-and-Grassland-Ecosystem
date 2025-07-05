import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(layout="wide")
st.title("🐦 Bird Species Observation Dashboard - MANA")

# Load data
try:
    df = pd.read_csv("Bird_Monitoring_Data_FOREST.XLSX - MANA.csv")
except FileNotFoundError:
    st.error("❌ File not found.")
    st.stop()

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert columns
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')

# Optional time fields
for col in ['start_time', 'end_time']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.time

# Drop missing essential rows
df.dropna(subset=['date', 'common_name', 'initial_three_min_cnt'], inplace=True)

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Filter: Year
year_options = sorted(df['date'].dt.year.unique())
year = st.sidebar.selectbox("Select Year", year_options)

# Filter: Species
species_options = sorted(df['common_name'].dropna().unique())
species = st.sidebar.selectbox("Select Bird Species", species_options)

# Filter: Interval Length (if present)
interval = None
if 'interval_length' in df.columns:
    interval_options = sorted(df['interval_length'].dropna().astype(str).unique())
    interval = st.sidebar.selectbox("Select Interval Length", interval_options)
    df['interval_length'] = df['interval_length'].astype(str).str.strip()

# Filter: ID Method (if present)
id_method = None
if 'id_method' in df.columns:
    id_options = sorted(df['id_method'].dropna().unique())
    id_method = st.sidebar.selectbox("Select ID Method", id_options)

# Filter: Date Range
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filter: Temperature
temp_min = int(df['temperature'].min()) if not df['temperature'].isnull().all() else 0
temp_max = int(df['temperature'].max()) if not df['temperature'].isnull().all() else 50
temp_range = st.sidebar.slider("Temperature Range (°C)", temp_min, temp_max, (temp_min, temp_max))

# Filter: Humidity
hum_min = int(df['humidity'].min()) if not df['humidity'].isnull().all() else 0
hum_max = int(df['humidity'].max()) if not df['humidity'].isnull().all() else 100
hum_range = st.sidebar.slider("Humidity Range (%)", hum_min, hum_max, (hum_min, hum_max))

# Apply filters
filtered = df[
    (df['date'].dt.year == year) &
    (df['common_name'] == species) &
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1])) &
    (df['temperature'].between(temp_range[0], temp_range[1], inclusive='both')) &
    (df['humidity'].between(hum_range[0], hum_range[1], inclusive='both'))
]

if interval:
    filtered = filtered[filtered['interval_length'] == interval]

if id_method:
    filtered = filtered[filtered['id_method'] == id_method]

# Display summary
st.subheader(f"📊 Filtered Observations for '{species}' in {year}")
st.write(f"🔢 Records Found: {len(filtered)}")
st.write(f"🐦 Total Bird Count: {filtered['initial_three_min_cnt'].sum()}")

# Line chart (daily trend)
if not filtered.empty:
    daily_counts = filtered.groupby('date')['initial_three_min_cnt'].sum()
    st.line_chart(daily_counts)

    # Table display
    st.dataframe(filtered[['date', 'common_name', 'initial_three_min_cnt', 'temperature', 'humidity']])
else:
    st.warning("No data matches the selected filters.")

# Global Top 10 species
st.subheader("🏆 Top 10 Most Observed Bird Species (Overall)")
top_species = df.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_species)
