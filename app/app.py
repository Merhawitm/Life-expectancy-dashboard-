import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.predict import predict_life_expectancy
from src.utils import add_continent_column, build_summary_report

st.set_page_config(page_title="Life Expectancy Dashboard", layout="wide")

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/cleaned_data.csv")
    df.columns = df.columns.str.strip()
    df = add_continent_column(df)
    return df

df = load_data()

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
st.sidebar.title("🧭 Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Overview", "Global Insights", "Comparisons", "Prediction"]
)

# -------------------------
# CONTINENT FILTER (GLOBAL)
# -------------------------
continents = ["All"] + sorted(df["Continent"].unique())
selected_continent = st.sidebar.selectbox("🌍 Continent", continents)

if selected_continent != "All":
    base_df = df[df["Continent"] == selected_continent]
else:
    base_df = df.copy()

# -------------------------
# HEADER
# -------------------------
st.title("🌍 Global Life Expectancy Dashboard")
st.markdown("### Insight-driven analytics (Power BI style)")

# -------------------------
# KPI CARDS
# -------------------------
avg_life = round(base_df["Life expectancy"].mean(), 2)
avg_gdp = round(base_df["GDP"].mean(), 2)
countries_count = base_df["Country"].nunique()

c1, c2, c3 = st.columns(3)
c1.metric("🌱 Avg Life Expectancy", avg_life)
c2.metric("💰 Avg GDP", f"{avg_gdp:,.0f}")
c3.metric("🌍 Countries", countries_count)

st.markdown("---")

# =====================================================
# 📌 OVERVIEW
# =====================================================
if page == "Overview":

    st.subheader("📊 Dataset Preview")
    st.dataframe(base_df.head())

    st.subheader("🌐 Global Distribution")

    fig = px.histogram(
        base_df,
        x="Life expectancy",
        nbins=30,
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📥 Download Summary")
    report = build_summary_report(base_df, selected_continent, "All")
    st.download_button("Download Report", report, file_name="report.txt")

# =====================================================
# 🌍 GLOBAL INSIGHTS (NO COUNTRY FILTER)
# =====================================================
elif page == "Global Insights":

    filtered_df = base_df  # 🚫 No country filtering here

    st.subheader("🏆 Top vs Bottom Countries")

    country_avg = filtered_df.groupby("Country")["Life expectancy"].mean().sort_values()

    top5 = country_avg.tail(5)
    bottom5 = country_avg.head(5)

    ranking = pd.concat([top5, bottom5])

    fig = px.bar(
        x=ranking.values,
        y=ranking.index,
        orientation="h",
        color=ranking.values,
        template="plotly_dark",
        title="Top vs Bottom Countries"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💰 GDP vs Life Expectancy")

    fig2 = px.scatter(
        filtered_df,
        x="GDP",
        y="Life expectancy",
        color="Status",
        size="Population",
        hover_name="Country",
        animation_frame="Year",
        template="plotly_dark"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🌍 World Map")

    fig3 = px.choropleth(
        filtered_df,
        locations="Country",
        locationmode="country names",
        color="Life expectancy",
        animation_frame="Year",
        template="plotly_dark"
    )

    st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# 📊 COMPARISONS (OPTIONAL COUNTRY FILTER)
# =====================================================
elif page == "Comparisons":

    selected_country = st.selectbox(
        "Optional Country Focus",
        ["All"] + sorted(base_df["Country"].unique())
    )

    if selected_country != "All":
        filtered_df = base_df[base_df["Country"] == selected_country]
    else:
        filtered_df = base_df

    st.subheader("🎯 Developed vs Developing Comparison")

    if "Status" in filtered_df.columns:

        status_group = filtered_df.groupby("Status")[["Life expectancy", "GDP"]].mean()

        col1, col2 = st.columns(2)

        # Life Expectancy
        with col1:
            fig_life = px.bar(
                status_group,
                y="Life expectancy",
                color=status_group.index,
                title="Average Life Expectancy",
                template="plotly_dark"
            )
            fig_life.update_layout(yaxis_title="Years", showlegend=False)
            st.plotly_chart(fig_life, use_container_width=True)

        # GDP
        with col2:
            fig_gdp = px.bar(
                status_group,
                y="GDP",
                color=status_group.index,
                title="Average GDP",
                template="plotly_dark"
            )
            fig_gdp.update_layout(yaxis_title="USD", showlegend=False)
            st.plotly_chart(fig_gdp, use_container_width=True)

        # Insights
        st.markdown("---")
        st.subheader("📌 Key Insights")

        try:
            d_life = status_group.loc["Developed"]["Life expectancy"]
            dev_life = status_group.loc["Developing"]["Life expectancy"]

            d_gdp = status_group.loc["Developed"]["GDP"]
            dev_gdp = status_group.loc["Developing"]["GDP"]

            st.write(f"• Developed countries live **{round(d_life-dev_life,2)} years longer**")
            st.write(f"• GDP difference is **{round(d_gdp-dev_gdp,0):,.0f} USD**")
            st.write("• Strong link between economy and health")

        except:
            st.warning("Not enough data for comparison")

    st.markdown("---")

    st.subheader("🌍 Life Expectancy by Continent")

    cont = filtered_df.groupby("Continent")["Life expectancy"].mean().reset_index()

    fig4 = px.bar(cont, x="Continent", y="Life expectancy", color="Continent", template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("📈 Country Trend")

    country = st.selectbox("Select Country", filtered_df["Country"].unique())

    cdf = filtered_df[filtered_df["Country"] == country]

    fig5 = px.line(cdf, x="Year", y="Life expectancy", markers=True, template="plotly_dark")
    st.plotly_chart(fig5, use_container_width=True)

# =====================================================
# 🔮 PREDICTION (COUNTRY REQUIRED)
# =====================================================
elif page == "Prediction":

    filtered_df = base_df

    st.subheader("🔮 Predict Life Expectancy")

    numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
    numeric_cols.remove("Life expectancy")

    inputs = {}
    col1, col2 = st.columns(2)

    for i, col in enumerate(numeric_cols):
        default = float(filtered_df[col].mean())
        min_val = float(filtered_df[col].min())
        max_val = float(filtered_df[col].max())

        if i % 2 == 0:
            inputs[col] = col1.number_input(col, min_val, max_val, default)
        else:
            inputs[col] = col2.number_input(col, min_val, max_val, default)

    if st.button("Predict"):
        pred = predict_life_expectancy(inputs)
        st.success(f"Predicted Life Expectancy: {pred:.2f}")