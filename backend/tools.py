from data_loader import get_dataframe

def get_dataset_summary():
    df=get_dataframe()
    return{
        "rows":len(df),
        "columns":list(df.columns),
        "countries":sorted(df["Area"].unique().tolist()),
        "crops":sorted(df["Item"].unique().tolist()),
        "year_range":{
            "min":int(df["Year"].min()),
            "max":int(df["Year"].max())
        }
    }

def aggregate_data(group_by, metric, aggregation):
    df=get_dataframe()
    result=(
        df.groupby(group_by)[metric]
        .agg(aggregation)
        .reset_index()
    )
    return result