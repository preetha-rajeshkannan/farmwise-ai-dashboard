import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from pydantic import BaseModel
from chat_service import process_user_query

app = FastAPI(title="FarmwiseAI Backend")


class ChatRequest(BaseModel):
    chat_id: str
    message: str


@app.get("/")
def home():
    return {
        "status": "running",
        "application": "FarmwiseAI Backend"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    return process_user_query(
        request.chat_id,
        request.message
    )