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

# Stores conversation history for each chat separately
chat_histories = {}

# Stores filter context for each chat separately
chat_contexts = {}


def process_user_query(chat_id, query):

    # Create new conversation for new chat
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    # Create new context for new chat
    if chat_id not in chat_contexts:
        chat_contexts[chat_id] = {
            "filters": {}
        }

    conversation_history = chat_histories[chat_id]
    current_context = chat_contexts[chat_id]

    # Add user message
    conversation_history.append(
        {
            "role": "user",
            "content": query
        }
    )

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

    conversation_history.append({
        "role": "system",
        "content": f"The tool '{tool_name}' was successfully executed with arguments: {json.dumps(args)}. The results were displayed to the user."
    })

    print("\n========== TOOL ==========")
    print(tool_name)
    print(tool_call.function.arguments)
    print("==========================")

    print("\n========== TOOL ARGS ==========")
    print(json.dumps(args, indent=2))
    print("===============================\n")

    try:
        # ==========================================
        # Tool 1 : Dataset Summary
        # ==========================================
        if tool_name == "dataset_summary":

            summary = get_dataset_summary()

            return {
                "tool": "dataset_summary",
                "data": summary
            }

        # ==========================================
        # Tool 2 : List Unique Values
        # ==========================================
        elif tool_name == "list_unique_values":

            values = list_unique_values(args["column"])

            return {
                "tool": "list_unique_values",
                "column": args["column"],
                "data": values
            }

        # ==========================================
        # Tool 3 : Scatter Analysis
        # ==========================================
        elif tool_name == "scatter_analysis":

            filters = args.get("filters", {})

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

            result = correlation_analysis(
                columns=args["columns"],
                filters=filters
            )

            return {
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

            return {
                "tool": "detect_outliers",
                "data": result.to_dict(orient="records")
            }

        # ==========================================
        # Tool 7 : Aggregate Data
        # ==========================================
        elif tool_name == "aggregate_data":

            if "filters" in args and args["filters"]:
                current_context["filters"] = args["filters"]

            filters = {}

            if "filters" in args and args["filters"]:
                filters.update(args["filters"])

            if args.get("country"):
                filters["country"] = args["country"]

            if args.get("crop"):
                filters["crop"] = args["crop"]

            if "country" in filters:
                filters["Area"] = filters.pop("country")

            if "crop" in filters:
                filters["Item"] = filters.pop("crop")

            filters = filters if filters else None

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

            return {
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