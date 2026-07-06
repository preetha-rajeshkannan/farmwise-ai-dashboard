import pandas as pd
from pathlib import Path

# Locate the dataset
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "yield_df.csv"

# Load dataset
df = pd.read_csv(DATA_PATH)

print("=" * 50)
print("First 5 Rows")
print("=" * 50)
print(df.head())

print("\n" + "=" * 50)
print("Dataset Shape")
print("=" * 50)
print(df.shape)

print("\n" + "=" * 50)
print("Columns")
print("=" * 50)
print(df.columns.tolist())

print("\n" + "=" * 50)
print("Data Types")
print("=" * 50)
print(df.dtypes)

print("\n" + "=" * 50)
print("Missing Values")
print("=" * 50)
print(df.isnull().sum())

print("\n" + "=" * 50)
print("Statistics")
print("=" * 50)
print(df.describe())

print("\n" + "=" * 50)
print("Unique Countries")
print("=" * 50)
print(df["Area"].nunique())

print("\n" + "=" * 50)
print("Unique Crops")
print("=" * 50)
print(df["Item"].nunique())

print("\n" + "=" * 50)
print("Year Range")
print("=" * 50)
print(df["Year"].min(), "-", df["Year"].max())