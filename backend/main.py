from fastapi import FastAPI
from tools import get_dataset_summary, aggregate_data

app=FastAPI()

@app.get("/")
def home():
    return {
        "message":"Farmwise AI Backend Running"
    }
@app.get("/summary")
def summary():
    return get_dataset_summary()

@app.get("/average-yield")
def average_yield():
    result=aggregate_data(
        group_by="Item",
        metric="hg/ha_yield",
        aggregation="mean"
    )
    return result.to_dict(orient="records")