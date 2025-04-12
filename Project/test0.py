import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set page layout
st.set_page_config(layout="wide")
st.title("COVID-19 Mobility and Policy Analysis")

# Load your cleaned DataFrame
@st.cache_data
def load_data():
    return pd.read_csv("final_data.csv", parse_dates=["date"])  # Update the filename accordingly

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
countries = df['country'].dropna().unique()
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=["India", "United States"])

min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

df_filtered = df[
    (df['country'].isin(selected_countries)) &
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1]))
]

# 1. Distribution of Mobility Trends
st.subheader("1. Distribution of Mobility Trend (%)")
fig1, ax1 = plt.subplots()
sns.histplot(df_filtered["trend"], bins=50, kde=True, ax=ax1)
ax1.set_title("Distribution of Mobility Trend (%)")
ax1.set_xlabel("Trend (%)")
st.pyplot(fig1)

# 2. Mobility Trends Over Time
st.subheader("2. Mobility Trend Over Time")
fig2, ax2 = plt.subplots()
sns.lineplot(data=df_filtered, x="date", y="trend", hue="country", ax=ax2)
ax2.set_title("Mobility Trend Over Time")
st.pyplot(fig2)

# 3. Policy Stringency vs Mobility
st.subheader("3. Policy Stringency vs Mobility")
fig3, ax3 = plt.subplots()
sns.scatterplot(data=df_filtered, x="stringency_index", y="trend", hue="country", ax=ax3)
ax3.set_title("Policy Stringency vs Mobility")
st.pyplot(fig3)

# 4. New Cases vs Mobility
st.subheader("4. New Cases vs Mobility")
fig4, ax4 = plt.subplots()
sns.scatterplot(data=df_filtered, x="new_cases", y="trend", hue="country", ax=ax4)
ax4.set_title("New Cases vs Mobility")
st.pyplot(fig4)

# 5. Testing vs Mobility
st.subheader("5. New Tests vs Mobility")
fig5, ax5 = plt.subplots()
sns.scatterplot(data=df_filtered, x="new_tests", y="trend", hue="country", ax=ax5)
ax5.set_title("New Tests vs Mobility")
st.pyplot(fig5)

# 6. Vaccination vs Mobility
st.subheader("6. Vaccination vs Mobility")
fig6, ax6 = plt.subplots()
sns.scatterplot(data=df_filtered, x="people_vaccinated_per_hundred", y="trend", hue="country", ax=ax6)
ax6.set_title("Vaccination vs Mobility")
st.pyplot(fig6)

# 7. Policy Timeline (Stringency Index Over Time)
st.subheader("7. Policy Stringency Over Time")
fig7, ax7 = plt.subplots()
sns.lineplot(data=df_filtered, x="date", y="stringency_index", hue="country", ax=ax7)
ax7.set_title("Policy Stringency Over Time")
st.pyplot(fig7)

# 8. Correlation Heatmap
st.subheader("8. Correlation Between Mobility and Other Factors")
correlation_cols = [
    'trend', 'new_cases', 'new_deaths', 'new_tests', 'stringency_index',
    'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred'
]
corr_df = df_filtered[correlation_cols].dropna()
corr = corr_df.corr()
fig8, ax8 = plt.subplots(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax8)
ax8.set_title("Correlation Heatmap")
st.pyplot(fig8)
