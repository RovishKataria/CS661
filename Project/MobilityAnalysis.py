import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# # ---------- Load Cleaned Data ----------
# data_path = os.path.join("Datasets", "Mobility Analysis", "cleaned_data.parquet")
# merged_df = pd.read_parquet(data_path)

# ---------- Load Cleaned Data ----------
merged_df = pd.read_parquet("cleaned_data.parquet")
merged_df["month"] = merged_df["date"].dt.to_period("M").astype(str)
merged_df["year"] = merged_df["date"].dt.year

# ---------- Sidebar ----------
st.sidebar.title("Filters")

min_date = merged_df["date"].min()
max_date = merged_df["date"].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter merged_df based on selected date range
merged_df = merged_df[
    (merged_df["date"] >= pd.to_datetime(date_range[0])) &
    (merged_df["date"] <= pd.to_datetime(date_range[1]))
]

# ---------- Tabs ----------
global_tab, top_tab, single_tab, multi_tab,  = st.tabs(["🌍 Global Overview", "🌟 Top Countries", "🏳️ Single Country", "🌐 Multi-Country"])

# ---------- Global Overview ----------
with global_tab:
    st.subheader("1. Line Chart – Global Average Mobility Index Over Time")
    global_avg_mobility = merged_df.groupby("date")["trend"].mean().reset_index()
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=global_avg_mobility["date"], y=global_avg_mobility["trend"],
                                  mode="lines", name="Mobility Index"))
    fig_line.update_layout(
        xaxis_title="Date",
        yaxis_title="Average Mobility Index (%)",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("2. Bar Chart – Year-wise Global Average Mobility Index Comparison")
    yearly_avg_mobility = merged_df.groupby("year")["trend"].mean().reset_index()
    fig_bar = px.bar(
        yearly_avg_mobility,
        x="year",
        y="trend",
        text_auto=True,
        labels={"trend": "Mobility Index (%)", "year": "Year"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("3. Treemap – Mobility under Combined Government Policies")
    policy_cols = [
        "c1m_school_closing", "c2m_workplace_closing",
        "c6m_stay_at_home_requirements", "c7m_restrictions_on_internal_movement"
    ]
    treemap_data = merged_df.dropna(subset=["country", "trend"] + policy_cols)
    treemap_grouped = treemap_data.groupby("country").agg({
        "trend": "mean",
        "c1m_school_closing": "mean",
        "c2m_workplace_closing": "mean",
        "c6m_stay_at_home_requirements": "mean",
        "c7m_restrictions_on_internal_movement": "mean"
    }).reset_index()
    treemap_grouped["policy_score"] = (
        treemap_grouped["c1m_school_closing"] +
        treemap_grouped["c2m_workplace_closing"] +
        treemap_grouped["c6m_stay_at_home_requirements"] +
        treemap_grouped["c7m_restrictions_on_internal_movement"]
    )
    fig_treemap = px.treemap(
        treemap_grouped,
        path=["country"],
        values="trend",
        color="policy_score",
        color_continuous_scale="Reds",
        labels={
            "trend": "Avg Mobility (%)",
            "policy_score": "Policy Strength Score"
        }
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

    st.subheader("4. Animated Bubble Map – Global Mobility Index by Country Every 2 Months")
    merged_df["two_month"] = merged_df["date"].dt.to_period("2M").astype(str)
    bubble_df = merged_df.groupby(
        ["country", "latitude", "longitude", "two_month"], as_index=False
    )["trend"].mean()
    bubble_df["mobility_size"] = bubble_df["trend"].clip(lower=0)
    fig_geo = px.scatter_geo(
        bubble_df,
        lat="latitude",
        lon="longitude",
        color="trend",
        size="mobility_size",
        hover_name="country",
        animation_frame="two_month",
        color_continuous_scale="RdBu_r",
        size_max=20,
        projection="natural earth"
    )
    fig_geo.update_layout(height=650)
    st.plotly_chart(fig_geo, use_container_width=True)

# ---------- Top Countries ----------
with top_tab:
    # Selector inside the tab
    top_n = st.selectbox(
        "Select number of top countries to display",
        options=[5, 10, 15, 20, 25, 30],
        index=1  # Default is 10
    )

    st.subheader(f"1. Pareto Chart – New Cases vs Mobility (Top {top_n} Countries)")
    # Filter out aggregates like continents
    country_level_df = merged_df[~merged_df["country"].str.contains("World|Asia|Africa|Europe|America|Oceania", case=False)]

    # Group and prepare data
    pareto_data = country_level_df.groupby("country", as_index=False).agg({
        "new_cases": "sum",
        "trend": "mean"
    }).rename(columns={"trend": "mobility_index"})
    pareto_data = pareto_data.dropna(subset=["new_cases", "mobility_index"])
    pareto_data["mobility_index"] = pareto_data["mobility_index"].round(2)

    # Sort and select top N
    top_cases_df = pareto_data.sort_values(by="new_cases", ascending=False).head(top_n)

    # Create Pareto chart
    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
    fig_pareto.add_trace(
        go.Bar(
            x=top_cases_df["country"],
            y=top_cases_df["new_cases"],
            name="New Cases",
            hovertemplate="%{x}<br>New Cases: %{y:,}"
        ),
        secondary_y=False,
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=top_cases_df["country"],
            y=top_cases_df["mobility_index"],
            name="Mobility Index",
            mode="lines+markers",
            hovertemplate="%{x}<br>Mobility Index: %{y:.2f}%"
        ),
        secondary_y=True,
    )
    fig_pareto.update_layout(
        xaxis_title="Country",
        yaxis_title="Total COVID-19 Cases",
        yaxis2_title="Avg. Mobility Index (%)",
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    st.subheader(f"2. Funnel Chart – Top {top_n} Countries by Mobility")
    # Group and prepare mobility data
    mobility_data = country_level_df.groupby("country", as_index=False)["trend"].mean()
    mobility_data = mobility_data.dropna()
    mobility_data = mobility_data[mobility_data["trend"] > 0]
    mobility_data = mobility_data.sort_values(by="trend", ascending=False).head(top_n)
    mobility_data["trend"] = mobility_data["trend"].round(2)

    # Funnel chart
    fig_funnel = px.funnel(
        mobility_data,
        x="trend",
        y="country",
        labels={"trend": "Mobility Index (%)", "country": "Country"},
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

# ---------- Single Country ----------
with single_tab:
    countries_available = merged_df["country"].dropna().unique()
    selected_country = st.selectbox(
        "Select a Country",
        options=sorted(countries_available),
        index=list(sorted(countries_available)).index("United States") if "United States" in countries_available else 0
    )
    country_df = merged_df[merged_df["country"] == selected_country]

    st.subheader(f"1. Line Chart – Mobility Trend Over Time in {selected_country}")
    fig1 = px.line(
        country_df,
        x="date",
        y="trend",
        labels={"trend": "Mobility Index (%)"},
        title=f"Mobility Index in {selected_country} Over Time"
    )
    fig1.update_traces(
        name="Mobility Index",
        hovertemplate="%{x}<br>Mobility Index: %{y:.2f}%"
    )
    fig1.update_layout(xaxis_title="Date", yaxis_title="Mobility Index (%)")
    st.plotly_chart(fig1, use_container_width=True)


    st.subheader(f"2. Dual Axis Chart – Mobility Index vs New COVID-19 Cases in {selected_country}")
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Primary y-axis: Mobility Index
    fig2.add_trace(
        go.Scatter(
            x=country_df["date"],
            y=country_df["trend"],
            name="Mobility Index",
            mode="lines",
            hovertemplate="%{x}<br>Mobility Index: %{y:.2f}%"
        ),
        secondary_y=False
    )
    
    # Secondary y-axis: New Cases
    fig2.add_trace(
        go.Scatter(
            x=country_df["date"],
            y=country_df["new_cases"],
            name="New Cases",
            mode="lines",
            line=dict(color="firebrick"),
            hovertemplate="%{x}<br>New Cases: %{y:,}"
        ),
        secondary_y=True
    )
    
    fig2.update_layout(
        xaxis_title="Date",
        yaxis_title="Mobility Index (%)",
        yaxis2_title="New COVID-19 Cases",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Multi-Country ----------
with multi_tab:
    countries_available = merged_df["country"].dropna().unique()
    multi_countries = st.multiselect(
        "Select Countries to Compare",
        options=sorted(countries_available),
        default=["United States", "India", "Brazil"]
    )
    if multi_countries:
        # Extract unique years for filtering
        merged_df["year"] = merged_df["date"].dt.year
        years = sorted(merged_df["year"].dropna().unique())

        # Filter data for selected countries
        filtered = merged_df[merged_df["country"].isin(multi_countries)]

        st.subheader("1. Line Chart – Multi-Country Mobility Comparison Over Time")
        fig3 = px.line(
            filtered,
            x="date",
            y="trend",
            color="country",
            labels={"trend": "Mobility Index (%)", "date": "Date"},
            title="Mobility Trends Over Time by Country"
        )
        fig3.update_traces(mode="lines", hovertemplate="%{x}<br>%{y:.2f}%")
        fig3.update_layout(legend_title="Country")
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("2. Bar Chart – Average Annual Mobility Comparison")
        selected_year = st.selectbox("Select Year", years, index=years.index(2021) if 2021 in years else 0)

        # Filter further by selected year
        filtered_year = filtered[filtered["year"] == selected_year]
        avg_mobility = (
            filtered_year.groupby("country", as_index=False)["trend"]
            .mean()
            .rename(columns={"trend": "avg_mobility"})
        )
        avg_mobility["avg_mobility"] = avg_mobility["avg_mobility"].round(2)
        avg_mobility = avg_mobility.sort_values(by="avg_mobility", ascending=False)

        # Bar chart
        fig_bar = px.bar(
            avg_mobility,
            x="country",
            y="avg_mobility",
            text="avg_mobility",
            labels={"avg_mobility": "Mobility Index (%)", "country": "Country"},
            title=f"Average Mobility Index in {selected_year} by Country",
            color="country",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            xaxis_title="Country",
            yaxis_title="Mobility Index (%)",
            xaxis_tickangle=-45,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Please select multiple countries from the sidebar.")
