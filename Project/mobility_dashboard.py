import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="COVID Mobility Analysis", layout="wide")

# Title and Introduction
st.title("📊 COVID Mobility Trends Dashboard")
st.markdown("""
This dashboard explores how human mobility changed during the COVID-19 pandemic across different continents and categories using Google Mobility Reports.
""")

# Load the data
@st.cache_data
def load_data():
    # Replace with your actual data source path
    df = pd.read_csv("final_data.csv", parse_dates=["date"])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_continent = st.sidebar.selectbox("Select Continent", df["continent"].unique())
selected_category = st.sidebar.selectbox("Select Category", df["category"].unique())

# Filtered data
filtered_df = df[(df["continent"] == selected_continent) & (df["category"] == selected_category)]

# Line Chart
st.subheader(f"Mobility Trends Over Time - {selected_category} in {selected_continent}")
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=filtered_df, x="date", y="trend", hue="country", ax=ax)
plt.xlabel("Date")
plt.ylabel("Mobility Trend (%)")
st.pyplot(fig)

# Histogram
st.subheader("Distribution of Mobility Trend (%)")
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.histplot(df["trend"], bins=50, kde=True, ax=ax2)
st.pyplot(fig2)

# Add more sections (e.g., bar plots, comparison charts, etc.)
