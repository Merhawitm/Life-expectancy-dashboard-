import pandas as pd
import numpy as np

def preprocess_data(df):
    # Remove whitespace from columns
    df.columns = df.columns.str.strip()

    # Select numeric columns
    numeric_cols = df.select_dtypes(include=np.number).columns

    # Fill missing values with mean
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    return df