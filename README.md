# Global Life Expectancy Analysis & Prediction Dashboard

An interactive dashboard that explores **why life expectancy differs between countries** and **predicts life expectancy** from health, economic and social factors, using World Health Organization (WHO) data for **193 countries from 2000 to 2015**.

---

## What questions does this project answer?

1. **Which factors are linked to how long people live?** For example, adult mortality, schooling, immunisation, GDP and HIV/AIDS.
2. **Which countries are similar to each other?** Countries are grouped by their health and development profiles.
3. **Can we predict a country's life expectancy?** Four prediction models are compared to find the most accurate one.

---

## The data

| Item | Details |
|---|---|
| Source | WHO Life Expectancy dataset (publicly available on Kaggle) |
| Size | 2,938 rows, where each row is one country in one year |
| Coverage | 193 countries, 2000–2015 |
| Target | Life expectancy (in years) |
| Features | 19 numeric indicators, such as adult mortality, infant deaths, alcohol use, health spending, immunisation rates, BMI, GDP, population and years of schooling |

---

## How the analysis works

### Step 1: Cleaning the data
- **Missing values:** some countries have gaps (for example, no GDP for a year). These were filled with the column average.
- **Standardising:** the indicators use very different scales (GDP is in thousands of dollars; schooling is in years). Every indicator was rescaled to the same scale so that no variable dominates just because its numbers are larger.

### Step 2: Reducing the number of variables (PCA)
Many of the 19 indicators carry overlapping information (for example, infant deaths and under-five deaths). **Principal Component Analysis (PCA)** combines them into a small number of new, unrelated variables called *principal components*.

- **5 principal components** were kept.
- Together they keep about **66% of the information** in the original 19 indicators.
- This makes the models simpler and avoids counting the same information twice.

### Step 3: Grouping similar countries (K-means clustering)
**K-means clustering** groups countries with similar health and development profiles.

- Countries were grouped into **3 clusters**, which broadly reflect different levels of development.
- The number of clusters was chosen with the **elbow method**: adding clusters beyond 3 gave little improvement.

### Step 4: Checking how distinct the groups are (LDA)
**Linear Discriminant Analysis (LDA)** finds the directions that best separate the groups.

- The first discriminant function explains **65%** of the separation between groups, and the second explains **35%**.
- This confirms that the groups are clearly different from each other.

### Step 5: Predicting life expectancy (regression models)
Four models were trained on the 5 principal components to predict life expectancy:

- **Linear Regression:** fits a straight-line relationship
- **Decision Tree:** splits the data into simple if-then rules
- **Random Forest:** combines many decision trees and averages their predictions
- **Gradient Boosting:** builds trees one after another, each correcting the previous one's errors

The data was split **80/20**: models learned from 80% of the data and were tested on the remaining 20%, which they had never seen.

---

## Results

| Model | R² (higher is better) | RMSE in years (lower is better) |
|---|---|---|
| **Random Forest** | **0.88** | **3.21** |
| Gradient Boosting | 0.84 | 3.68 |
| Decision Tree | 0.78 | 4.39 |
| Linear Regression | 0.73 | 4.81 |

**How to read these numbers:**
- **R²** shows how much of the difference in life expectancy between countries the model explains. An R² of 0.88 means the model explains **88%** of it.
- **RMSE** is the typical size of a prediction error. An RMSE of 3.21 means predictions are usually **about 3 years** away from the true value.

**Random Forest performed best.** Combining many trees lets it capture non-linear relationships that a straight-line model misses, while averaging protects it from the overfitting a single tree suffers from.

---

## The dashboard

The Streamlit app has seven pages, selected from the sidebar:

| Page | What it shows |
|---|---|
| Overview | Key statistics and a summary of the data |
| Global Insights | Life expectancy trends across countries and continents |
| Comparisons | Side-by-side comparison of countries and indicators |
| PCA Analysis | How much information each principal component keeps, with plots |
| Advanced Analysis | K-means clusters and LDA results |
| Model Comparison | Accuracy of the four prediction models |
| Prediction | Enter values and get a predicted life expectancy |

---

## Repository structure

```
├── app/app.py              # Streamlit dashboard
├── src/                    # code for cleaning, training and prediction
├── notebooks/              # full statistical analysis, with outputs
├── data/raw/               # original WHO data
├── data/processed/         # cleaned data used by the app
├── models/model.pkl        # trained model used by the Prediction page
├── assets/style.css        # dashboard styling
└── requirements.txt        # Python libraries needed
```

---

## How to run it yourself

```bash
# 1. Download the project
git clone https://github.com/Merhawitm/Life-expectancy-dashboard-.git
cd Life-expectancy-dashboard-

# 2. Install the required libraries
pip install -r requirements.txt

# 3. Train and save the prediction model
python src/train.py

# 4. Open the dashboard in your browser
streamlit run app/app.py
```

---

## Tools used

Python, pandas, NumPy, scikit-learn, Streamlit, Plotly, Matplotlib, Seaborn

## Author

**Merhawit Tesfay Kassa** ([@Merhawitm](https://github.com/Merhawitm))
BSc Data Science and Analytics, USIU-Africa

## License

This project is released under the MIT License.
