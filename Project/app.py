import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
# date_range = st.sidebar.date_input("Select Date Range", [merged_df["date"].min(), merged_df["date"].max()])
selected_country = st.sidebar.selectbox("Select a Country", sorted(merged_df["country"].dropna().unique()))
multi_countries = st.sidebar.multiselect("Select Multiple Countries", sorted(merged_df["country"].dropna().unique()))

# Filter merged_df based on selected date range
merged_df = merged_df[
    (merged_df["date"] >= pd.to_datetime(date_range[0])) &
    (merged_df["date"] <= pd.to_datetime(date_range[1]))
]

# ---------- Tabs ----------
global_tab, top_tab, single_tab, multi_tab,  = st.tabs(["🌍 Global Overview", "🌟 Top Countries", "🏳️ Single Country", "🌐 Multi-Country"])

# ---------- Global Overview ----------
with global_tab:
    # st.subheader("1. Global Mobility Trends Over Time")
    # global_trend = merged_df.groupby("date")["trend"].mean().reset_index()
    # fig5 = px.line(global_trend, x="date", y="trend", title="Global Mobility Over Time",
    #                labels={"trend": "Mobility (%)", "date": "Date"})
    # st.plotly_chart(fig5, use_container_width=True)
    st.subheader("1. Global Mobility Trends Over Time")
    global_trend = merged_df.groupby("date")["trend"].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=global_trend["date"], y=global_trend["trend"],
                            mode="lines", name="Mobility Index"))
    # Add range slider and selectors
    fig.update_layout(
        title="Global Mobility Over Time",
        xaxis_title="Date",
        yaxis_title="Mobility (%)",
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
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("2. Year-wise Global Mobility Comparison")
    # “This chart compares global movement trends across pandemic years.
    # As you can see, 2020 shows a sharp drop below 0, reflecting the onset of COVID-19 lockdowns.
    # Mobility gradually recovered in 2021 and peaked in 2022, showing a global adaptation and reopening.
    # Interestingly, in 2023, mobility slightly declined again — possibly due to stabilization or residual restrictions in some regions.”
    yearly = merged_df.groupby("year")["trend"].mean().reset_index()
    fig6 = px.bar(yearly, x="year", y="trend", title="Year-wise Global Mobility",
                  labels={"trend": "Mobility Index (%)", "year": "Year"})
    st.plotly_chart(fig6, use_container_width=True)
    
    st.subheader("3. Treemap – Mobility under Combined Government Policies")
    # Filter valid rows
    policy_cols = [
        "c1m_school_closing", "c2m_workplace_closing",
        "c6m_stay_at_home_requirements", "c7m_restrictions_on_internal_movement"
    ]
    treemap_df = merged_df.dropna(subset=["country", "trend"] + policy_cols)
    # Compute average mobility & combined policy score per country
    treemap_grouped = treemap_df.groupby("country").agg({
        "trend": "mean",
        "c1m_school_closing": "mean",
        "c2m_workplace_closing": "mean",
        "c6m_stay_at_home_requirements": "mean",
        "c7m_restrictions_on_internal_movement": "mean"
    }).reset_index()
    # Create a combined policy intensity score
    treemap_grouped["policy_score"] = (
        treemap_grouped["c1m_school_closing"] +
        treemap_grouped["c2m_workplace_closing"] +
        treemap_grouped["c6m_stay_at_home_requirements"] +
        treemap_grouped["c7m_restrictions_on_internal_movement"]
    )
    # Plot treemap
    fig_treemap = px.treemap(
        treemap_grouped,
        path=["country"],
        values="trend",  # box size = mobility
        color="policy_score",  # box color = policy strength
        color_continuous_scale="Reds",
        title="Mobility vs Combined Government Policy Intensity",
        labels={
            "trend": "Avg Mobility (%)",
            "policy_score": "Policy Strength Score"
        }
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

    # st.subheader("4. Heatmap – Mobility at Vaccination Start")
    # fig = px.choropleth(
    #     merged_df,
    #     locations="country",
    #     locationmode="country names",
    #     color="trend",
    #     hover_name="country",
    #     animation_frame=merged_df["date"].dt.strftime("%Y-%m"),
    #     color_continuous_scale="RdBu_r",
    #     range_color=[-50, 50],
    #     title="Global Mobility Animation"
    # )
    # st.plotly_chart(fig, use_container_width=True)

    # Assuming merged_df is already filtered by the selected date range
    merged_df["two_month"] = merged_df["date"].dt.to_period("2M").astype(str)
    # Aggregate mobility for animation (every 2 months)
    two_month_df = merged_df.groupby(
        ["country", "latitude", "longitude", "two_month"], as_index=False
    )["trend"].mean()
    # Ensure bubble size is non-negative
    two_month_df["mobility_size"] = two_month_df["trend"].clip(lower=0)
    # Create animated bubble geo chart
    fig = px.scatter_geo(
        two_month_df,
        lat="latitude",
        lon="longitude",
        color="trend",
        size="mobility_size",
        hover_name="country",
        animation_frame="two_month",
        color_continuous_scale="RdBu_r",
        size_max=25,
        projection="orthographic",  # nice 3D globe
        title="Global Mobility – Animated (Every 2 Months)"
    )
    fig.update_layout(height=650)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Top Countries ----------
with top_tab:
    st.subheader("Top Countries – COVID-19 Impact and Mobility")

    # Selector inside the tab, not sidebar
    top_n = st.selectbox(
        "Select number of top countries to display",
        options=[5, 10, 15, 20, 25, 30],
        index=1  # Default is 10
    )

    st.subheader("1. Pareto Chart – Top Countries by New Cases")
    # Filter valid countries (exclude aggregate regions)
    top_df = merged_df[~merged_df["country"].str.contains("World|Asia|Africa|Europe|America|Oceania", case=False)]

    # -- Pareto Chart --
    top_cases = top_df.groupby("country", as_index=False).agg({
        "new_cases": "sum",
        "trend": "mean"
    }).rename(columns={"trend": "mobility_index"})
    top_cases = top_cases.dropna(subset=["new_cases", "mobility_index"])
    top_cases["mobility_index"] = top_cases["mobility_index"].round(2)
    top_cases_sorted = top_cases.sort_values(by="new_cases", ascending=False).head(top_n)

    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
    fig_pareto.add_trace(
        go.Bar(x=top_cases_sorted["country"], y=top_cases_sorted["new_cases"], name="New Cases"),
        secondary_y=False,
    )
    fig_pareto.add_trace(
        go.Scatter(x=top_cases_sorted["country"], y=top_cases_sorted["mobility_index"], name="Mobility Index"),
        secondary_y=True,
    )
    fig_pareto.update_layout(
        title=f"Pareto Chart: New Cases vs Mobility (Top {top_n} Countries)",
        xaxis_title="Country",
        yaxis_title="New Cases",
        yaxis2_title="Mobility Index (%)"
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # -- Funnel Chart --
    st.subheader("2. Funnel Chart – Top Countries by Mobility")
    top_mobility = top_df.groupby("country", as_index=False)["trend"].mean()
    top_mobility = top_mobility.dropna()
    top_mobility = top_mobility[top_mobility["trend"] > 0]
    top_mobility = top_mobility.sort_values(by="trend", ascending=False).head(top_n)
    top_mobility["trend"] = top_mobility["trend"].round(2)

    fig_funnel = px.funnel(
        top_mobility,
        x="trend",
        y="country",
        title=f"Funnel Chart: Mobility Index of Top {top_n} Countries",
        labels={"trend": "Mobility Index (%)", "country": "Country"}
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

# ---------- Single Country ----------
with single_tab:
    country_df = merged_df[merged_df["country"] == selected_country]

    st.subheader(f"1. Mobility Index Over Time – {selected_country}")
    fig1 = px.line(country_df, x="date", y="trend", title="Mobility Trend Over Time",
                   labels={"trend": "Mobility Index (%)", "date": "Date"})
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader(f"2. Mobility vs New COVID-19 Cases – {selected_country}")
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(go.Scatter(x=country_df["date"], y=country_df["trend"], name="Mobility Index"), secondary_y=False)
    fig2.add_trace(go.Scatter(x=country_df["date"], y=country_df["new_cases"], name="New Cases"), secondary_y=True)
    fig2.update_layout(title="Mobility vs New Cases", xaxis_title="Date")
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Multi-Country ----------
with multi_tab:
    if multi_countries:
        # Extract unique years from the dataset
        merged_df["year"] = merged_df["date"].dt.year
        years = sorted(merged_df["year"].dropna().unique())
        # Filter by year and selected countries
        filtered = merged_df[merged_df["country"].isin(multi_countries)]

        st.subheader("1. Line Chart – Mobility Trends Over Time")
        fig3 = px.line(filtered, x="date", y="trend", color="country",
                       labels={"trend": "Mobility Index (%)", "date": "Date"},
                       title="Multi-Country Mobility Comparison")
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("2. Bar Chart – Total Mobility Comparison Across Countries")
        # Year selector
        selected_year = st.selectbox("Select Year", years, index=years.index(2021) if 2021 in years else 0)
        # Filter the already multi-country filtered df for selected year
        filtered_year = filtered[filtered["year"] == selected_year]

        # Group and calculate average mobility
        avg_mobility = filtered_year.groupby("country", as_index=False)["trend"].mean()
        avg_mobility["trend"] = avg_mobility["trend"].round(2)
        avg_mobility = avg_mobility.sort_values(by="trend", ascending=False)

        # Bar plot
        fig_bar = px.bar(
            avg_mobility,
            x="country",
            y="trend",
            text="trend",
            title=f"Average Mobility by Country in {selected_year}",
            labels={"trend": "Mobility Index (%)", "country": "Country"},
            color="country"
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(yaxis_title="Mobility Index (%)", xaxis_title="Country")
        st.plotly_chart(fig_bar, use_container_width=True)

        # st.subheader("3. Histogram – Comparing Key Metrics Across Years")
        # # Define metrics to visualize
        # metric_map = {
        #     "New Cases": "new_cases",
        #     "New Deaths": "new_deaths",
        #     "Tests": "new_tests",
        #     "Vaccinations": "people_vaccinated_per_hundred",
        #     "Policy Stringency": "stringency_index",
        #     "Mobility Index": "trend"
        # }
        # # Ensure 'year' column exists
        # merged_df["year"] = merged_df["date"].dt.year
        # # Filter for selected countries only
        # filtered_df = merged_df[merged_df["country"].isin(multi_countries)]
        # # Compute yearly means of each metric
        # yearly_summary = (
        #     filtered_df.groupby("year")[list(metric_map.values())]
        #     .mean()
        #     .round(2)
        #     .reset_index()
        # )
        # # Melt to long format for grouped bars
        # long_df = yearly_summary.melt(
        #     id_vars="year", var_name="metric_code", value_name="avg_value"
        # )
        # # Replace column names with readable metric labels
        # metric_labels = {v: k for k, v in metric_map.items()}
        # long_df["Metric"] = long_df["metric_code"].map(metric_labels)
        # # Plot grouped bar chart
        # fig_histogram = px.bar(
        #     long_df,
        #     x="Metric",
        #     y="avg_value",
        #     color=long_df["year"].astype(str),
        #     barmode="group",  # side-by-side bars
        #     labels={"avg_value": "Average Value", "year": "Year"},
        #     title="Key Metrics Comparison by Year"
        # )
        # fig_histogram.update_layout(
        #     xaxis_title="Metric",
        #     yaxis_title="Average Value",
        #     legend_title="Year"
        # )
        # st.plotly_chart(fig_histogram, use_container_width=True)
    else:
        st.warning("Please select multiple countries from the sidebar.")
