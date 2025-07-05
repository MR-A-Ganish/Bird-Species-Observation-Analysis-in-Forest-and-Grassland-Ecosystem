import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page config
st.set_page_config(layout="wide")
st.title("🐦 Bird Observation Dashboard with ID Method")

# Load dataset
FILE = "Bird_Monitoring_Data_FOREST.XLSX - CHOH.csv"
try:
    df = pd.read_csv(FILE)
except FileNotFoundError:
    st.error(f"❌ File '{FILE}' not found.")
    st.stop()

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Type conversions
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')

# Drop missing critical fields
df.dropna(subset=['date', 'common_name', 'initial_three_min_cnt'], inplace=True)

# Optional: convert time fields
for col in ['start_time', 'end_time']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.time

# Sidebar filters
st.sidebar.header("🔍 Filters")

# ✅ ID method (filter by ID if present)
id_col = next((col for col in df.columns if 'id' in col), None)
if id_col:
    id_options = sorted(df[id_col].dropna().astype(str).unique())
    selected_id = st.sidebar.selectbox("🎯 Filter by ID", ["-- All --"] + id_options)
else:
    selected_id = "-- All --"

# Apply ID filter first if selected
if selected_id != "-- All --" and id_col:
    df = df[df[id_col].astype(str) == selected_id]

# Year filter
year_options = sorted(df['date'].dt.year.unique())
year = st.sidebar.selectbox("Year", year_options)

# Species filter
species_options = sorted(df['common_name'].dropna().unique())
species = st.sidebar.selectbox("Species", species_options)

# Interval filter
interval = None
if 'interval_length' in df.columns:
    interval_options = sorted(df['interval_length'].dropna().astype(str).unique())
    interval = st.sidebar.selectbox("Interval Length", interval_options)

# Date range
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Temperature filter
if df['temperature'].notna().any():
    temp_range = st.sidebar.slider("Temperature Range", int(df['temperature'].min()), int(df['temperature'].max()), (int(df['temperature'].min()), int(df['temperature'].max())))
else:
    temp_range = None

# Humidity filter
if df['humidity'].notna().any():
    hum_range = st.sidebar.slider("Humidity Range", int(df['humidity'].min()), int(df['humidity'].max()), (int(df['humidity'].min()), int(df['humidity'].max())))
else:
    hum_range = None

# Apply remaining filters
filtered = df[
    (df['date'].dt.year == year) &
    (df['common_name'] == species)
]

if interval:
    filtered = filtered[filtered['interval_length'].astype(str) == interval]

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered['date'] >= start_date) & (filtered['date'] <= end_date)]

if temp_range:
    filtered = filtered[(filtered['temperature'] >= temp_range[0]) & (filtered['temperature'] <= temp_range[1])]

if hum_range:
    filtered = filtered[(filtered['humidity'] >= hum_range[0]) & (filtered['humidity'] <= hum_range[1])]

# Output
st.subheader("📋 Filtered Results")
st.write(f"🔢 Total Records: {len(filtered)}")
st.write(f"🐦 Total Bird Count: {int(filtered['initial_three_min_cnt'].sum())}")

if not filtered.empty:
    st.dataframe(filtered, use_container_width=True)

    st.subheader("📈 Observation Trend")
    time_series = filtered.groupby('date')['initial_three_min_cnt'].sum()
    st.line_chart(time_series)

    st.subheader("🏆 Top 10 Most Observed Birds (Filtered)")
    top10 = filtered.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top10.values, y=top10.index, palette='crest', ax=ax)
    ax.set_title("Top 10 Bird Species")
    st.pyplot(fig)
else:
    st.warning("⚠️ No records match the selected filters.")
