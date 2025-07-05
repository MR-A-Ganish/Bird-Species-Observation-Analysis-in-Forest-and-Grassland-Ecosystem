import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(layout="wide")
st.title("🌿 Bird Observation Dashboard with Filters")

# Load dataset
try:
    df = pd.read_csv("Bird_Monitoring_Data_FOREST.XLSX - CATO.csv")
except FileNotFoundError:
    st.error("❌ File not found.")
    st.stop()

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert columns to appropriate types
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['initial_three_min_cnt'] = pd.to_numeric(df['initial_three_min_cnt'], errors='coerce')
df['interval_length'] = df['interval_length'].astype(str).str.strip()

# Drop rows with missing critical values
df = df.dropna(subset=['date', 'common_name', 'interval_length', 'initial_three_min_cnt'])

# Optional: convert time fields if present
for time_col in ['start_time', 'end_time']:
    if time_col in df.columns:
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce').dt.time

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Year filter
year_options = sorted(df['date'].dt.year.unique())
year = st.sidebar.selectbox("Select Year", year_options)

# Species filter
species_options = sorted(df['common_name'].dropna().unique())
species = st.sidebar.selectbox("Select Bird Species", species_options)

# Interval length filter
interval_options = sorted(df['interval_length'].unique())
interval = st.sidebar.selectbox("Select Interval Length", interval_options)

# Date range filter
min_date = df['date'].min()
max_date = df['date'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
if len(date_range) == 2:
    start, end = date_range
    filtered = df[
        (df['date'] >= pd.to_datetime(start)) &
        (df['date'] <= pd.to_datetime(end)) &
        (df['date'].dt.year == year) &
        (df['common_name'] == species) &
        (df['interval_length'] == interval)
    ]
else:
    filtered = pd.DataFrame()  # empty

# Display summary
st.subheader(f"📅 Observations for '{species}' in {year} during '{interval}' intervals")
st.write(f"🔢 Total Records: {len(filtered)}")
st.write(f"🐦 Total Bird Count: {filtered['initial_three_min_cnt'].sum()}")

# Show data & charts
if not filtered.empty:
    # Daily line chart
    daily_counts = filtered.groupby('date')['initial_three_min_cnt'].sum()
    st.line_chart(daily_counts)

    # Table view
    st.dataframe(filtered[['date', 'interval_length', 'initial_three_min_cnt']])
else:
    st.warning("No data available for the selected filters.")

# Global analysis: top 10 species
st.subheader("🏆 Top 10 Most Observed Bird Species (Overall)")
top_species = df.groupby('common_name')['initial_three_min_cnt'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_species)
