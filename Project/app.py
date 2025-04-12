import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Google Mobility Analysis Dashboard")

# Load merged data
merged_df = pd.read_csv("final_data.csv", parse_dates=["date"])
# If you're already running in a script, use the existing merged_df

# Sidebar filters
st.sidebar.header("Filters")
selected_country = st.sidebar.selectbox("Select Country", merged_df['country'].dropna().unique())
selected_continent = st.sidebar.selectbox("Select Continent (Optional)", merged_df['continent'].dropna().unique())

filtered_df = merged_df[merged_df['country'] == selected_country]

# 1. Mobility Trend Over Time
st.subheader("1. Mobility Trend Over Time")
fig1, ax1 = plt.subplots(figsize=(12, 4))
sns.lineplot(data=filtered_df, x="date", y="trend", ax=ax1)
ax1.set_title(f"Mobility Trend (%) in {selected_country}")
st.pyplot(fig1)

# 2. Mobility vs New Cases
st.subheader("2. Mobility vs New COVID-19 Cases")
fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.plot(filtered_df["date"], filtered_df["trend"], label="Mobility (%)", color='blue')
ax2.set_ylabel("Mobility (%)", color='blue')
ax3 = ax2.twinx()
ax3.plot(filtered_df["date"], filtered_df["new_cases"], label="New Cases", color='red')
ax3.set_ylabel("New Cases", color='red')
ax2.set_title("Mobility vs New COVID-19 Cases")
st.pyplot(fig2)

# 3. Mobility vs Stringency Index
st.subheader("3. Mobility vs Policy Stringency")
fig3, ax4 = plt.subplots(figsize=(12, 4))
sns.lineplot(data=filtered_df, x="date", y="trend", label="Mobility", ax=ax4)
sns.lineplot(data=filtered_df, x="date", y="stringency_index", label="Stringency Index", ax=ax4)
ax4.set_title("Mobility vs Policy Stringency")
st.pyplot(fig3)

# 4. Mobility vs Vaccination Progress
st.subheader("4. Mobility vs Vaccination Progress")
fig4, ax5 = plt.subplots(figsize=(12, 4))
sns.lineplot(data=filtered_df, x="date", y="trend", label="Mobility", ax=ax5)
sns.lineplot(data=filtered_df, x="date", y="people_fully_vaccinated_per_hundred", label="Fully Vaccinated (%)", ax=ax5)
ax5.set_title("Mobility vs Vaccination Progress")
st.pyplot(fig4)

# 5. Mobility vs Testing Trends
st.subheader("5. Mobility vs Testing Trends")
fig5, ax6 = plt.subplots(figsize=(12, 4))
sns.lineplot(data=filtered_df, x="date", y="trend", label="Mobility", ax=ax6)
sns.lineplot(data=filtered_df, x="date", y="new_tests_per_thousand", label="New Tests per Thousand", ax=ax6)
ax6.set_title("Mobility vs Testing Trends")
st.pyplot(fig5)

# 6. Region-wise Mobility Comparison
st.subheader("6. Region-wise Mobility Trend")
continent_df = merged_df[merged_df['continent'] == selected_continent]
continent_avg = continent_df.groupby("date")["trend"].mean().reset_index()
fig6, ax7 = plt.subplots(figsize=(12, 4))
sns.lineplot(data=continent_avg, x="date", y="trend", ax=ax7)
ax7.set_title(f"Average Mobility Trend in {selected_continent}")
st.pyplot(fig6)

# 7. Correlation Heatmap
st.subheader("7. Correlation Between Variables")
numeric_cols = merged_df.select_dtypes(include="number")
corr = numeric_cols.corr()
fig7, ax8 = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, cmap="coolwarm", center=0)
ax8.set_title("Correlation Heatmap")
st.pyplot(fig7)

# 8. Top 10 Countries with Highest Drop in Mobility
st.subheader("8. Top 10 Countries by Lowest Average Mobility")
country_trends = merged_df.groupby("country")["trend"].mean().sort_values().head(10)
fig8, ax9 = plt.subplots(figsize=(10, 5))
sns.barplot(x=country_trends.values, y=country_trends.index, palette="Reds_r", ax=ax9)
ax9.set_title("Top 10 Countries by Lowest Avg Mobility")
ax9.set_xlabel("Average Mobility (%)")
st.pyplot(fig8)
