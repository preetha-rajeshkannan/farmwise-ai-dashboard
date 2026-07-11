import os
import json
from datetime import datetime

CHAT_FOLDER = "chat_history"

# Create folder if it doesn't exist
os.makedirs(CHAT_FOLDER, exist_ok=True)


def list_chats():
    chats = [
        f for f in os.listdir(CHAT_FOLDER)
        if f.endswith(".json")
    ]
    chats.sort()
    return chats


def create_chat():
    chat_name = f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    filepath = os.path.join(CHAT_FOLDER, chat_name)

    with open(filepath, "w") as f:
        json.dump([], f)

    return chat_name


def load_chat(chat_name):
    filepath = os.path.join(CHAT_FOLDER, chat_name)

    if not os.path.exists(filepath):
        return []

    with open(filepath, "r") as f:
        return json.load(f)


def save_chat(chat_name, messages):
    filepath = os.path.join(CHAT_FOLDER, chat_name)

    with open(filepath, "w") as f:
        json.dump(messages, f, indent=4)


def delete_chat(chat_name):
    filepath = os.path.join(CHAT_FOLDER, chat_name)

    if os.path.exists(filepath):
        os.remove(filepath)