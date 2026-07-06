from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def home():
    return {
        "message":"Farmwise AI Backend Running"
    }