import joblib
import pandas as pd

def predict_life_expectancy(input_data):
    model, scaler, pca, columns = joblib.load("models/model.pkl")

    input_df = pd.DataFrame([input_data])
    input_df = input_df[columns]

    input_scaled = scaler.transform(input_df)
    input_pca = pca.transform(input_scaled)

    prediction = model.predict(input_pca)

    return prediction[0]