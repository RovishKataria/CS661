import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")
st.title("COVID-19 Mobility Analysis Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("final_data.csv", parse_dates=["date"])

merged_df = load_data()

# Sidebar filters
countries = merged_df["country"].dropna().unique().tolist()
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=["India", "United States"])
filtered_df = merged_df[merged_df["country"].isin(selected_countries)]

# 1. Global Mobility Trends Over Time
st.subheader("1. Global Mobility Trends Over Time")
mobility_trend = merged_df.groupby("date")["trend"].mean().reset_index()
fig1 = px.line(mobility_trend, x="date", y="trend", title="Average Global Mobility Trend Over Time")
st.plotly_chart(fig1, use_container_width=True)

# 2. Mobility vs COVID-19 New Cases
st.subheader("2. Mobility vs New COVID-19 Cases")
daily = merged_df.groupby("date")[["trend", "new_cases"]].mean().reset_index()
fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(go.Scatter(x=daily["date"], y=daily["trend"], name="Mobility Trend (%)"), secondary_y=False)
fig2.add_trace(go.Scatter(x=daily["date"], y=daily["new_cases"], name="New Cases"), secondary_y=True)
fig2.update_layout(title_text="Mobility vs New Cases Over Time")
st.plotly_chart(fig2, use_container_width=True)

# 3. Country-wise Average Mobility
st.subheader("3. Country-wise Average Mobility")
top_countries = merged_df.groupby("country")["trend"].mean().sort_values(ascending=False).head(20).reset_index()
fig3 = px.bar(top_countries, x="country", y="trend", title="Top 20 Countries by Average Mobility", text_auto=True)
st.plotly_chart(fig3, use_container_width=True)

# 4. Mobility vs Vaccination Rate
st.subheader("4. Mobility vs Vaccination Rate")
scatter_df = merged_df[["trend", "people_vaccinated_per_hundred"]].dropna()
fig4 = px.scatter(scatter_df, x="people_vaccinated_per_hundred", y="trend",
                  trendline="ols", title="Mobility vs Vaccination Rate")
st.plotly_chart(fig4, use_container_width=True)

# 5. Mobility vs Government Stringency Index
st.subheader("5. Mobility vs Government Stringency Index")
stringency_df = merged_df.groupby("date")[["trend", "stringency_index"]].mean().reset_index()
fig5 = make_subplots(specs=[[{"secondary_y": True}]])
fig5.add_trace(go.Scatter(x=stringency_df["date"], y=stringency_df["trend"], name="Mobility Trend"), secondary_y=False)
fig5.add_trace(go.Scatter(x=stringency_df["date"], y=stringency_df["stringency_index"], name="Stringency Index"), secondary_y=True)
fig5.update_layout(title_text="Mobility vs Policy Strictness Over Time")
st.plotly_chart(fig5, use_container_width=True)

# 6. Regional Mobility Over Time
st.subheader("6. Regional Mobility Over Time")
if "continent" in merged_df.columns:
    regional = merged_df.groupby(["date", "continent"])["trend"].mean().reset_index()
    fig6 = px.line(regional, x="date", y="trend", color="continent", title="Mobility by Region")
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.warning("Continent information missing.")

# 7. Testing Intensity vs Mobility
st.subheader("7. Testing vs Mobility")
test_df = merged_df[["new_tests_per_thousand", "trend"]].dropna()
fig7 = px.scatter(test_df, x="new_tests_per_thousand", y="trend", title="Mobility vs Testing Rate", trendline="ols")
st.plotly_chart(fig7, use_container_width=True)

# 8. Heatmap of Mobility Trend by Country and Time
st.subheader("8. Mobility Heatmap by Country and Month")
heatmap_df = merged_df.copy()
heatmap_df["month"] = heatmap_df["date"].dt.to_period("M").astype(str)
pivot = heatmap_df.groupby(["country", "month"])["trend"].mean().unstack().fillna(0)
fig8 = px.imshow(pivot, aspect="auto", color_continuous_scale="RdBu_r", origin="lower",
                 labels=dict(color="Mobility Trend"), title="Country-wise Monthly Mobility")
st.plotly_chart(fig8, use_container_width=True)
