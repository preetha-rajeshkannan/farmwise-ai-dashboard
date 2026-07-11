import pandas as pd
from data_loader import get_dataframe


# ==========================================================
# Helper Functions
# ==========================================================

def apply_filters(df, filters=None):
    """
    Apply filters to the dataframe.
    Supports:
    - country/crop/year
    - multiple values
    - last N years
    """

    if not filters:
        return df

    max_year = df["Year"].max()

    for column, value in filters.items():

        if value is None or value == []:
            continue

        if column == "country":
            column = "Area"
        elif column == "crop":
            column = "Item"
        elif column == "year":
            column = "Year"

            if isinstance(value, dict) and "last" in value:
                n = value["last"]
                years = list(range(max_year - n + 1, max_year + 1))
                df = df[df["Year"].isin(years)]
                continue

        if column not in df.columns:
            continue

        if not isinstance(value, list):
            value = [value]

        actual_values = df[column].unique()
        resolved_values = []
        missing_values = []

        for v in value:
            if v in actual_values:
                resolved_values.append(v)
            else:
                v_lower = str(v).lower()
                matches = [av for av in actual_values if v_lower in str(av).lower()]
                if matches:
                    resolved_values.extend(matches)
                else:
                    missing_values.append(v)
        
        if missing_values:
            raise ValueError(f"The following values are not in the dataset for {column}: {', '.join(missing_values)}")
        
        df = df[df[column].isin(resolved_values)]

    return df


def get_filtered_dataframe(filters=None):
    """
    Returns dataframe after applying filters.
    """
    df = get_dataframe()
    return apply_filters(df, filters)


# ==========================================================
# Dataset Summary
# ==========================================================

def get_dataset_summary():

    df = get_dataframe()

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "countries": df["Area"].nunique(),
        "crops": df["Item"].nunique(),
        "year_range": [
            int(df["Year"].min()),
            int(df["Year"].max())
        ]
    }


def list_unique_values(column):

    df = get_dataframe()

    if column not in df.columns:
        raise ValueError(f"Invalid column: {column}")

    return sorted(df[column].dropna().unique().tolist())


# ==========================================================
# Statistical Analysis
# ==========================================================

def describe_metric(metric, filters=None):

    df = get_filtered_dataframe(filters)

    if metric not in df.columns:
        raise ValueError(f"Invalid metric: {metric}")

    return df[metric].describe().to_dict()


def correlation_analysis(columns, filters=None):

    df = get_filtered_dataframe(filters)

    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Invalid column: {col}")

    return df[columns].corr()


def detect_outliers(metric, filters=None):

    df = get_filtered_dataframe(filters)

    if metric not in df.columns:
        raise ValueError(f"Invalid metric: {metric}")

    q1 = df[metric].quantile(0.25)
    q3 = df[metric].quantile(0.75)

    iqr = q3 - q1

    return df[
        (df[metric] < q1 - 1.5 * iqr) |
        (df[metric] > q3 + 1.5 * iqr)
    ]


# ==========================================================
# Scatter Analysis
# ==========================================================

def scatter_analysis(
    x_column,
    y_column,
    filters=None
):

    df = get_filtered_dataframe(filters)

    if x_column not in df.columns:
        raise ValueError(f"Invalid column: {x_column}")

    if y_column not in df.columns:
        raise ValueError(f"Invalid column: {y_column}")

    return df[[x_column, y_column]]


# ==========================================================
# Trend Analysis
# ==========================================================

# def trend_analysis(
#     x_column,
#     metric,
#     aggregation="mean",
#     filters=None
# ):

#     df = get_filtered_dataframe(filters)

#     if x_column not in df.columns:
#         raise ValueError(f"Invalid column: {x_column}")

#     if metric not in df.columns:
#         raise ValueError(f"Invalid metric: {metric}")

#     return (
#         df.groupby(x_column)[metric]
#         .agg(aggregation)
#         .reset_index()
#     )


# ==========================================================
# Top K Records
# ==========================================================

# def top_k_records(
#     group_by,
#     metric,
#     aggregation="mean",
#     k=5,
#     ascending=False,
#     filters=None
# ):

#     df = get_filtered_dataframe(filters)

#     if group_by not in df.columns:
#         raise ValueError(f"Invalid column: {group_by}")

#     if metric not in df.columns:
#         raise ValueError(f"Invalid metric: {metric}")

#     return (
#         df.groupby(group_by)[metric]
#         .agg(aggregation)
#         .reset_index()
#         .sort_values(metric, ascending=ascending)
#         .head(k)
#     )


# ==========================================================
# General Aggregation Tool
# ==========================================================

def aggregate_data(
    group_by,
    metric,
    aggregation,
    filters=None,
    sort_by=None,
    ascending=False,
    limit=None
):

    if aggregation == "avg":
        aggregation = "mean"

    df = get_filtered_dataframe(filters)

    if group_by not in df.columns:
        raise ValueError(f"Invalid group_by column: {group_by}")

    if metric not in df.columns:
        raise ValueError(f"Invalid metric column: {metric}")

    print("\n========== FILTER DEBUG ==========")
    print("Filters:", filters)
    print("Rows:", len(df))
    print("==================================\n")

    result = (
        df.groupby(group_by)[metric]
        .agg(aggregation)
        .reset_index()
    )

    if sort_by and sort_by in result.columns:
        result = result.sort_values(
            by=sort_by,
            ascending=ascending
        )

    if limit:
        result = result.head(limit)

    return result