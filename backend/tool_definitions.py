FILTER_SCHEMA = {
    "type": "object",
    "properties": {
        "country": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "array",
                    "items": {"type": "string"}
                },
                {"type": "null"}
            ]
        },
        "crop": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "array",
                    "items": {"type": "string"}
                },
                {"type": "null"}
            ]
        },
        "year": {
            "oneOf": [
                {"type": "integer"},
                {
                    "type": "object",
                    "properties": {
                        "last": {
                            "type": ["integer", "null"]
                        }
                    }
                },
                {"type": "null"}
            ]
        }
    }
}


TOOLS = [

# =====================================================
# DATASET SUMMARY
# =====================================================

{
    "type": "function",
    "function": {
        "name": "dataset_summary",
        "description": "Return metadata about the agricultural dataset including rows, columns, countries, crops and year range.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
},

# =====================================================
# UNIQUE VALUES
# =====================================================

{
    "type": "function",
    "function": {
        "name": "list_unique_values",
        "description": "Return all unique values from Area, Item or Year.",
        "parameters": {
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "enum": [
                        "Area",
                        "Item",
                        "Year"
                    ]
                }
            },
            "required": [
                "column"
            ]
        }
    }
},

# =====================================================
# AGGREGATION
# =====================================================

{
    "type": "function",
    "function": {
        "name": "aggregate_data",
        "description": "Aggregate numerical agricultural data grouped by Area, Item or Year. Supports filtering, sorting and charts.",
        "parameters": {
            "type": "object",
            "properties": {

                "group_by": {
                    "type": "string",
                    "enum": [
                        "Area",
                        "Item",
                        "Year"
                    ]
                },

                "metric": {
                    "type": "string",
                    "enum": [
                        "hg/ha_yield",
                        "average_rain_fall_mm_per_year",
                        "pesticides_tonnes",
                        "avg_temp"
                    ]
                },

                "aggregation": {
                    "type": "string",
                    "enum": [
                        "mean",
                        "sum",
                        "max",
                        "min",
                        "count",
                        "avg"
                    ]
                },

                "chart_type": {
                    "type": ["string", "null"],
                    "enum": [
                        "bar",
                        "line",
                        "scatter",
                        "pie",
                        "histogram",
                        "box",
                        None
                    ]
                },

                "filters": FILTER_SCHEMA,

                "sort_by": {
                    "type": ["string", "null"]
                },

                "ascending": {
                    "type": ["boolean", "null"]
                },

                "limit": {
                    "type": ["integer", "null"]
                }

            },

            "required": [
                "group_by",
                "metric",
                "aggregation"
            ]
        }
    }
},

# =====================================================
# SCATTER ANALYSIS
# =====================================================

{
    "type": "function",
    "function": {
        "name": "scatter_analysis",
        "description": "Return raw values of two numerical variables for scatter plot analysis.",
        "parameters": {
            "type": "object",
            "properties": {

                "x_column": {
                    "type": "string",
                    "enum": [
                        "hg/ha_yield",
                        "average_rain_fall_mm_per_year",
                        "pesticides_tonnes",
                        "avg_temp"
                    ]
                },

                "y_column": {
                    "type": "string",
                    "enum": [
                        "hg/ha_yield",
                        "average_rain_fall_mm_per_year",
                        "pesticides_tonnes",
                        "avg_temp"
                    ]
                },

                "filters": FILTER_SCHEMA

            },

            "required": [
                "x_column",
                "y_column"
            ]
        }
    }
},

# =====================================================
# CORRELATION
# =====================================================

{
    "type": "function",
    "function": {
        "name": "correlation_analysis",
        "description": "Calculate correlation matrix between numerical columns.",
        "parameters": {
            "type": "object",
            "properties": {

                "columns": {
                    "type": "array",
                    "minItems": 2,
                    "items": {
                        "type": "string",
                        "enum": [
                            "hg/ha_yield",
                            "average_rain_fall_mm_per_year",
                            "pesticides_tonnes",
                            "avg_temp"
                        ]
                    }
                },

                "filters": FILTER_SCHEMA

            },

            "required": [
                "columns"
            ]
        }
    }
},

# =====================================================
# DESCRIBE METRIC
# =====================================================

{
    "type": "function",
    "function": {
        "name": "describe_metric",
        "description": "Return descriptive statistics for a numerical metric.",
        "parameters": {
            "type": "object",
            "properties": {

                "metric": {
                    "type": "string",
                    "enum": [
                        "hg/ha_yield",
                        "average_rain_fall_mm_per_year",
                        "pesticides_tonnes",
                        "avg_temp"
                    ]
                },

                "filters": FILTER_SCHEMA

            },

            "required": [
                "metric"
            ]
        }
    }
},

# =====================================================
# OUTLIERS
# =====================================================

{
    "type": "function",
    "function": {
        "name": "detect_outliers",
        "description": "Detect outliers using the IQR method.",
        "parameters": {
            "type": "object",
            "properties": {

                "metric": {
                    "type": "string",
                    "enum": [
                        "hg/ha_yield",
                        "average_rain_fall_mm_per_year",
                        "pesticides_tonnes",
                        "avg_temp"
                    ]
                },

                "filters": FILTER_SCHEMA

            },

            "required": [
                "metric"
            ]
        }
    }
},

# =====================================================
# TREND ANALYSIS
# =====================================================

{
    "type": "function",
    "function": {
        "name": "trend_analysis",
        "description": "Analyze trends over Area, Item or Year.",
        "parameters": {
            "type": "object",
            "properties": {

                "x_column": {
                    "type": "string",
                    "enum": [
                        "Area",
                        "Item",
                        "Year"
                    ]
                },

                "metric": {
                    "type": "string",
                    "enum": [
                        "hg/ha_yield",
                        "average_rain_fall_mm_per_year",
                        "pesticides_tonnes",
                        "avg_temp"
                    ]
                },

                "aggregation": {
                    "type": "string",
                    "enum": [
                        "mean",
                        "sum",
                        "max",
                        "min",
                        "count"
                    ]
                },

                "filters": FILTER_SCHEMA

            },

            "required": [
                "x_column",
                "metric"
            ]
        }
    }
},

# =====================================================
# TOP K
# =====================================================

{
    "type": "function",
    "function": {
        "name": "top_k_records",
        "description": "Return top or bottom K grouped records ranked by a numerical metric.",
        "parameters": {
            "type": "object",
            "properties": {

                "group_by": {
                    "type": "string",
                    "enum": [
                        "Area",
                        "Item",
                        "Year"
                    ]
                },

                "metric": {
                    "type": "string",
                    "enum": [
                        "hg/ha_yield",
                        "average_rain_fall_mm_per_year",
                        "pesticides_tonnes",
                        "avg_temp"
                    ]
                },

                "aggregation": {
                    "type": "string",
                    "enum": [
                        "mean",
                        "sum",
                        "max",
                        "min",
                        "count"
                    ]
                },

                "k": {
                    "type": "integer"
                },

                "ascending": {
                    "type": "boolean"
                },

                "filters": FILTER_SCHEMA

            },

            "required": [
                "group_by",
                "metric"
            ]
        }
    }
}

]