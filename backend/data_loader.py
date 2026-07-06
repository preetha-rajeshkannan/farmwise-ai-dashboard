import pandas as pd
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
DATA_PATH=BASE_DIR/"data"/"yield_df.csv"
df=pd.read_csv(DATA_PATH)
df=df.drop(columns=["Unnamed: 0"])
def get_dataframe():
    return df