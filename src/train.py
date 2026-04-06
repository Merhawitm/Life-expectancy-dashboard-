import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor

from preprocessing import preprocess_data

# Load data
df = pd.read_csv("data/processed/cleaned_data.csv")

df = preprocess_data(df)

# Features and target
numeric_df = df.select_dtypes(include=np.number)

X = numeric_df.drop(columns=["Life expectancy"])
y = numeric_df["Life expectancy"]

# Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA
pca = PCA(n_components=5)
X_pca = pca.fit_transform(X_scaled)

# Model
model = RandomForestRegressor()
model.fit(X_pca, y)

# Save everything
joblib.dump((model, scaler, pca, X.columns.tolist()), "models/model.pkl")

print("Model trained and saved!")