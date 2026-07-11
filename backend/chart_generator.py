import plotly.express as px

def create_chart(df, chart_type, x_column, y_column=None, title="Chart"):
    if chart_type is None:
        chart_type = "bar"
        
    if chart_type=="bar":
        fig=px.bar(
            df,
            x=x_column,
            y=y_column,
            title=title
        )
    elif chart_type=="line":
        fig=px.line(
            df,
            x=x_column,
            y=y_column,
            title=title
        )
    elif chart_type == "scatter":
        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=title
        )

    elif chart_type == "pie":
        fig = px.pie(
            df,
            names=x_column,
            values=y_column,
            title=title
        )

    elif chart_type == "histogram":
        fig = px.histogram(
            df,
            x=x_column,
            title=title
        )

    elif chart_type == "box":
        fig = px.box(
            df,
            x=x_column,
            y=y_column,
            title=title
        )
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    return fig