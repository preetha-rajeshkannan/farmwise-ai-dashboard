from llm import ask_llm
import json
from tools import (
    aggregate_data,
    get_dataset_summary,
    list_unique_values,
    scatter_analysis,
    correlation_analysis,
    describe_metric,
    detect_outliers
)
from chart_generator import create_chart
from prompts import SYSTEM_PROMPT

# Stores filter context for each chat separately
chat_contexts = {}


def process_user_query(chat_id, query):

    # Create new context for new chat
    if chat_id not in chat_contexts:
        chat_contexts[chat_id] = {
            "filters": {}
        }

    current_context = chat_contexts[chat_id]
    
    system_message = SYSTEM_PROMPT + f"\n\n==================================================\nSESSION MEMORY\n==================================================\n"
    system_message += f"Current active filters: {json.dumps(current_context.get('filters', {}))}\n"
    if "last_tool_args" in current_context:
        # Filter out null values to avoid confusing the LLM
        clean_args = {k: v for k, v in current_context["last_tool_args"].items() if v is not None}
        system_message += f"Last query's tool arguments: {json.dumps(clean_args)}\n"
    system_message += "Use these filters and arguments if the user's query implies modifying or continuing the previous analysis (e.g., 'give pie chart', 'top 5 alone')."

    conversation_history = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": query
        }
    ]

    try:
        response = ask_llm(conversation_history)
    except Exception as e:
        error_msg = str(e)
        conversation_history.append({
            "role": "assistant",
            "content": f"Error: {error_msg}"
        })
        return {
            "message": f"I encountered an error trying to process your request: {error_msg}"
        }

    # ==========================================
    # No tool selected
    # ==========================================
    if not response.tool_calls:
        return {
            "message": response.content
        }

    tool_call = response.tool_calls[0]
    tool_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments or "{}") or {}
    
    # Merge with last_tool_args ONLY for aggregate_data (not other tools)
    if tool_name == "aggregate_data" and "last_tool_args" in current_context:
        last_args = current_context["last_tool_args"]
        for k, v in last_args.items():
            if k not in args or args[k] is None:
                args[k] = v
    
    if "filters" in args and args["filters"]:
        current_context["filters"] = args["filters"]
        
        
    # We will save the context variables at the end of the execution,
    # because modify_chart needs to read the OLD context before it gets overwritten!

    conversation_history.append({
        "role": "system",
        "content": f"The tool '{tool_name}' was successfully executed with arguments: {json.dumps(args)}. The results were displayed to the user."
    })


    try:
        # ==========================================
        # Tool 1 : Dataset Summary
        # ==========================================
        if tool_name == "dataset_summary":

            summary = get_dataset_summary()

            return {
                "message": "✅ Dataset summary generated.",
                "tool": "dataset_summary",
                "data": summary
            }

        # ==========================================
        # Tool 2 : List Unique Values
        # ==========================================
        elif tool_name == "list_unique_values":

            values = list_unique_values(args["column"])

            return {
                "message": f"✅ Found {len(values)} unique values for column {args['column']}.",
                "tool": "list_unique_values",
                "column": args["column"],
                "data": values
            }

        # ==========================================
        # Tool 3 : Scatter Analysis
        # ==========================================
        elif tool_name == "scatter_analysis":

            filters = args.get("filters", {})

            if not args.get("x_column"):
                raise ValueError("Missing required parameter: x_column")
            if not args.get("y_column"):
                raise ValueError("Missing required parameter: y_column")

            result = scatter_analysis(
                x_column=args["x_column"],
                y_column=args["y_column"],
                filters=filters
            )

            fig = create_chart(
                df=result,
                chart_type="scatter",
                x_column=args["x_column"],
                y_column=args["y_column"],
                title=query
            )

            return {
                "message": f"✅ Scatter analysis generated for {args.get('x_metric')} vs {args.get('y_metric')}.",
                "tool": "scatter_analysis",
                "arguments": args,
                "data": result.to_dict(orient="records"),
                "chart": fig.to_json()
            }

        # ==========================================
        # Tool 4 : Correlation Analysis
        # ==========================================
        elif tool_name == "correlation_analysis":

            filters = args.get("filters", {})

            if not args.get("columns"):
                raise ValueError("Missing required parameter: columns")

            result = correlation_analysis(
                columns=args["columns"],
                filters=filters
            )

            return {
                "message": "✅ Correlation analysis generated.",
                "tool": "correlation_analysis",
                "data": result.to_dict()
            }

        # ==========================================
        # Tool 5 : Describe Metric
        # ==========================================
        elif tool_name == "describe_metric":

            filters = args.get("filters", {})

            result = describe_metric(
                metric=args["metric"],
                filters=filters
            )

            return {
                "message": f"✅ Metrics generated for {args['metric']}.",
                "tool": "describe_metric",
                "data": result
            }

        # ==========================================
        # Tool 6 : Detect Outliers
        # ==========================================
        elif tool_name == "detect_outliers":

            filters = args.get("filters", {})

            result = detect_outliers(
                metric=args["metric"],
                filters=filters
            )

            current_context["last_tool_name"] = tool_name
            current_context["last_tool_args"] = args
            return {
                "message": f"✅ Outlier detection completed for {args['metric']}.",
                "tool": "detect_outliers",
                "data": result.to_dict(orient="records")
            }

        # ==========================================
        # Tool 7 : Modify Chart
        # ==========================================
        elif tool_name == "modify_chart":
            if "last_tool_name" not in current_context or current_context["last_tool_name"] != "aggregate_data":
                raise ValueError("Currently only aggregate_data charts can be modified. Please generate a chart first.")
            
            # Use the previous tool's arguments as the base
            last_args = current_context["last_tool_args"].copy()

            # Override with any newly provided arguments (like limit, chart_type, sort_by)
            for k, v in args.items():
                if v is not None:
                    last_args[k] = v

            # Fall through to the aggregate_data implementation by renaming the tool
            tool_name = "aggregate_data"
            args = last_args
            # Do NOT return here, let it fall through to aggregate_data execution

        # ==========================================
        # Tool 8 : Aggregate Data
        # ==========================================
        if tool_name == "aggregate_data":

            # ---- Smart defaults for missing/null parameters ----
            if not args.get("aggregation"):
                args["aggregation"] = "mean"
            if not args.get("group_by"):
                args["group_by"] = "Area"
            if not args.get("metric"):
                raise ValueError("Missing required parameter: metric")

            # ---- Sanitize filters ----
            filters = {}

            # First apply session memory filters
            if current_context.get("filters"):
                filters.update(current_context["filters"])

            # Then apply any new filters from the current tool call
            if "filters" in args and args["filters"] and isinstance(args["filters"], dict):
                for fk, fv in args["filters"].items():
                    # Skip empty arrays, None values, and non-filter keys
                    if fv is None:
                        continue
                    if isinstance(fv, list) and len(fv) == 0:
                        continue
                    # Skip keys that are actually metric names (LLM confusion)
                    if fk in ("metric", "aggregation", "sort_by", "ascending", "limit", "chart_type"):
                        continue
                    filters[fk] = fv

            if args.get("country"):
                filters["country"] = args.pop("country")

            if args.get("crop"):
                filters["crop"] = args.pop("crop")

            if "country" in filters:
                filters["Area"] = filters.pop("country")

            if "crop" in filters:
                filters["Item"] = filters.pop("crop")

            # ---- Validate filter values against actual dataset ----
            validated_filters = {}
            for col, val in filters.items():
                try:
                    actual_values = list(list_unique_values(col))
                    actual_set = set(actual_values)
                except Exception:
                    continue  # Skip unknown columns
                
                def fuzzy_match(v):
                    """Try exact match first, then prefix/contains match."""
                    if v in actual_set:
                        return v
                    # Try case-insensitive exact match
                    for av in actual_values:
                        if str(av).lower() == str(v).lower():
                            return av
                    # Try prefix match (e.g., "China" → "China, mainland")
                    matches = [av for av in actual_values if str(av).lower().startswith(str(v).lower())]
                    if len(matches) == 1:
                        return matches[0]
                    # Try contains match
                    matches = [av for av in actual_values if str(v).lower() in str(av).lower()]
                    if len(matches) == 1:
                        return matches[0]
                    if len(matches) > 1:
                        # Return the shortest match (most likely the right one)
                        return min(matches, key=len)
                    return None

                if isinstance(val, list):
                    valid_vals = []
                    for v in val:
                        matched = fuzzy_match(v)
                        if matched:
                            valid_vals.append(matched)
                        else:
                            print(f"WARNING: Filter value '{v}' for '{col}' not found in dataset, dropping it.")
                    if valid_vals:
                        validated_filters[col] = valid_vals
                    else:
                        print(f"WARNING: All filter values for '{col}' were invalid (hallucinated): {val}")
                else:
                    matched = fuzzy_match(val)
                    if matched:
                        validated_filters[col] = matched
                    else:
                        print(f"WARNING: Filter value '{val}' for '{col}' is invalid (hallucinated), dropping it.")
            
            filters = validated_filters

            # ---- Sanitize sort_by ----
            valid_metrics = ["hg/ha_yield", "average_rain_fall_mm_per_year", "pesticides_tonnes", "avg_temp"]
            if args.get("sort_by") and args["sort_by"] not in valid_metrics:
                args["sort_by"] = args["metric"]

            result = aggregate_data(
                group_by=args["group_by"],
                metric=args["metric"],
                aggregation=args["aggregation"],
                filters=filters,
                sort_by=args.get("sort_by"),
                ascending=args.get("ascending", False),
                limit=args.get("limit")
            )

            fig = create_chart(
                df=result,
                chart_type=args.get("chart_type", "bar"),
                x_column=args["group_by"],
                y_column=args["metric"],
                title=query
            )

            # Save context AFTER successful execution
            current_context["last_tool_name"] = "aggregate_data"
            current_context["last_tool_args"] = args
            
            chart_type = args.get('chart_type', 'bar')
            metric = args.get('metric', 'data')

            return {
                "message": f"✅ {chart_type.title()} chart generated for {metric.replace('_', ' ')}.",
                "tool": "aggregate_data",
                "arguments": args,
                "data": result.to_dict(orient="records"),
                "chart": fig.to_json()
            }

        else:
            return {
                "message": f"Unknown tool: {tool_name}"
            }

    except ValueError as e:
        error_msg = str(e)
        conversation_history.append({
            "role": "assistant",
            "content": f"Error: {error_msg}"
        })
        return {
            "message": f"I cannot fulfill that request: {error_msg}"
        }