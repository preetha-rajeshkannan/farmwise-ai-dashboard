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
# TOOL 1: DATASET SUMMARY
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
# TOOL 2: UNIQUE VALUES
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
# TOOL 3: AGGREGATION
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
                    "type": ["string", "null"],
                    "enum": [
                        "Area",
                        "Item",
                        "Year",
                        None
                    ]
                },

                "metric": {
                    "type": ["string", "null"],
                    "enum": [
                        "hg/ha_yield",
                        "average_rain_fall_mm_per_year",
                        "pesticides_tonnes",
                        "avg_temp",
                        None
                    ]
                },

                "aggregation": {
                    "type": ["string", "null"],
                    "enum": [
                        "mean",
                        "sum",
                        "max",
                        "min",
                        "count",
                        "avg",
                        None
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

            "required": []
        }
    }
},

# =====================================================
# TOOL 4: MODIFY CHART
# =====================================================

{
    "type": "function",
    "function": {
        "name": "modify_chart",
        "description": "Modify the visual properties or limits of the currently displayed chart without changing the underlying data.",
        "parameters": {
            "type": "object",
            "properties": {
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
                "limit": {
                    "type": ["integer", "null"]
                },
                "sort_by": {
                    "type": ["string", "null"]
                },
                "ascending": {
                    "type": ["boolean", "null"]
                },
                "filters": FILTER_SCHEMA
            },
            "required": []
        }
    }
},

# =====================================================
# TOOL 5: SCATTER ANALYSIS
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
# TOOL 6: CORRELATION
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
# TOOL 7: DESCRIBE METRIC
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
# TOOL 8: OUTLIERS
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



]