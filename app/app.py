
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
    ["Overview", "Global Insights", "Comparisons", "PCA Analysis", "Model Comparison", "Prediction"]
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

    plot_df = filtered_df.copy()
    plot_df["Population"] = np.ceil(plot_df["Population"]).astype(int)

    fig2 = px.scatter(
        plot_df,
        x="GDP",
        y="Life expectancy",
        color="Status",
        size="Population",
        hover_name="Country",
        animation_frame="Year",
        template="plotly_dark",
        size_max=60
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
# 📉 PCA ANALYSIS
# =====================================================
elif page == "PCA Analysis":

    st.subheader("📉 Principal Component Analysis")

    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.impute import SimpleImputer

    # -------------------------
    # PREPARE DATA
    # -------------------------
    filtered_df = base_df.copy()
    numeric_df = filtered_df.select_dtypes(include=np.number)

    if "Life expectancy" in numeric_df.columns:
        X = numeric_df.drop(columns=["Life expectancy"])
    else:
        X = numeric_df

    # Impute missing values
    imputer = SimpleImputer(strategy="mean")
    X_imputed = imputer.fit_transform(X)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    pca = PCA(n_components=2)
    components = pca.fit_transform(X_scaled)

    pca_df = pd.DataFrame(data=components, columns=["PC1", "PC2"])
    
    # Ensuring categorical data for hover and color
    # Reset indices to safely merge array slices back to dataframe
    pca_df["Country"] = filtered_df["Country"].reset_index(drop=True)
    if "Status" in filtered_df.columns:
        pca_df["Status"] = filtered_df["Status"].reset_index(drop=True)
    if "Continent" in filtered_df.columns:
        pca_df["Continent"] = filtered_df["Continent"].reset_index(drop=True)

    st.markdown("PCA helps reduce the dimensionality to show underlying patterns and clusters of countries based on all socioeconomic and macroeconomic indicators.")
    st.subheader("🔍 Covariance Matrix")
    
    cov_matrix = np.cov(X_scaled, rowvar=False)
    fig_cov = px.imshow(
        cov_matrix, 
        x=X.columns, 
        y=X.columns, 
        color_continuous_scale='RdBu_r',
        title="Predictor Covariance Matrix",
        template='plotly_dark'
    )
    fig_cov.update_layout(width=700, height=700)
    st.plotly_chart(fig_cov, use_container_width=True)

    # === FULL PCA FOR ELBOW PLOT AND EIGEN VALUES ===
    st.markdown("---")
    st.subheader("📐 Eigenvalues & Elbow Plot")
    
    full_pca = PCA()
    full_pca.fit(X_scaled)
    
    # Eigen Values
    eigen_values = full_pca.explained_variance_
    eigen_df = pd.DataFrame({
        "Component": [f"PC{i+1}" for i in range(len(eigen_values))],
        "Eigenvalue": eigen_values,
        "Variance Ratio": full_pca.explained_variance_ratio_,
        "Cumulative Variance": np.cumsum(full_pca.explained_variance_ratio_)
    })
    
    col1, col2 = st.columns((1, 1.5))
    with col1:
        st.write("**Top 10 Eigenvalues**")
        st.dataframe(eigen_df.head(10).style.format({"Eigenvalue": "{:.2f}", "Variance Ratio": "{:.2%}", "Cumulative Variance": "{:.2%}"}))
        
    with col2:
        # Elbow plot
        fig_elbow = px.line(
            x=range(1, len(full_pca.explained_variance_ratio_) + 1),
            y=np.cumsum(full_pca.explained_variance_ratio_),
            markers=True,
            labels={'x': 'Number of Components', 'y': 'Cumulative Explained Variance'},
            title='Scree Plot (Elbow Method)',
            template='plotly_dark'
        )
        fig_elbow.add_vline(x=5, line_dash="dash", line_color="red", annotation_text="Chosen PCs (5)")
        st.plotly_chart(fig_elbow, use_container_width=True)

    st.markdown("---")
    st.subheader("🤖 Model Selection & Configuration")
    st.success(
        "Based on the Elbow plot and variance retention, we compress the data to **5 Principal Components** "
        "before feeding it to our machine learning model. \n\n"
        "**Chosen Model**: `RandomForestRegressor` (An ensemble learning method for regression that operates by constructing a multitude of decision trees)."
    )

    st.markdown("---")
    st.subheader("🌐 2D Projection of Principal Components")

    fig_pca = px.scatter(
        pca_df,
        x="PC1",
        y="PC2",
        color="Continent" if "Continent" in pca_df.columns else "Status",
        hover_name="Country",
        template="plotly_dark",
        title="2D Plot of the First Two Principal Components"
    )
    st.plotly_chart(fig_pca, use_container_width=True)

    explained_variance = pca.explained_variance_ratio_
    st.info(f"**Variance Explained (2D Plot):** PC1 ({explained_variance[0]:.2%}) | PC2 ({explained_variance[1]:.2%}) | Total: {explained_variance.sum():.2%}")


# =====================================================
# 📊 MODEL COMPARISON
# =====================================================
elif page == "Model Comparison":

    st.subheader("📊 Regression Models Comparison")
    st.markdown("We evaluate multiple machine learning algorithms using our 5 Principal Components.")

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.tree import DecisionTreeRegressor

    filtered_df = base_df.copy()
    numeric_df = filtered_df.select_dtypes(include=np.number)
    
    if "Life expectancy" in numeric_df.columns:
        X = numeric_df.drop(columns=["Life expectancy"])
        y = numeric_df["Life expectancy"]
    else:
        st.error("Life expectancy column not found!")
        st.stop()

    # Preprocessing
    imputer = SimpleImputer(strategy="mean")
    X_imputed = imputer.fit_transform(X)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    pca = PCA(n_components=5)
    X_pca = pca.fit_transform(X_scaled)

    # Train Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.2, random_state=42)

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
    }

    results = []
    
    with st.spinner("Training models for comparison..."):
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            r2 = r2_score(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            results.append({"Model": name, "R² Score": r2, "RMSE": rmse})
            
    results_df = pd.DataFrame(results).sort_values(by="R² Score", ascending=False)
    
    col1, col2 = st.columns((1, 1.5))
    
    with col1:
        st.write("**Model Performance Metrics**")
        st.dataframe(results_df.style.format({"R² Score": "{:.4f}", "RMSE": "{:.4f}"}), use_container_width=True)
        
    with col2:
        fig = px.bar(
            results_df,
            x="R² Score",
            y="Model",
            orientation="h",
            color="R² Score",
            text="R² Score",
            template="plotly_dark",
            title="Model Accuracy (R² Score) Comparison",
            color_continuous_scale="Blues"
        )
        fig.update_traces(texttemplate='%{text:.3f}', textposition='auto')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
    st.info(f"🏆 The **{results_df.iloc[0]['Model']}** achieved the highest accuracy!")

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