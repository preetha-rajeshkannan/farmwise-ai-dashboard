import streamlit as st
import requests
import plotly.io as pio
import pandas as pd
import os
import json
from datetime import datetime

# -----------------------
# Page Config
# -----------------------

st.set_page_config(
    page_title="FarmwiseAI Dashboard",
    page_icon="🌾",
    layout="wide"
)

# -----------------------
# Load CSS
# -----------------------

try:
    with open("style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except FileNotFoundError:
    pass

# -----------------------
# Chat Storage
# -----------------------

CHAT_DIR = "chats"

os.makedirs(CHAT_DIR, exist_ok=True)


def create_chat():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def chat_path(chat_id):
    return os.path.join(CHAT_DIR, f"{chat_id}.json")


def save_chat(chat_id, messages):
    with open(chat_path(chat_id), "w") as f:
        json.dump(messages, f)


def load_chat(chat_id):
    path = chat_path(chat_id)

    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)

    return []


def list_chats():
    chats = []

    for file in os.listdir(CHAT_DIR):
        if file.endswith(".json"):
            chats.append(file[:-5])

    chats.sort()

    return chats


def delete_chat(chat_id):
    path = chat_path(chat_id)

    if os.path.exists(path):
        os.remove(path)

# -----------------------
# Initialize Session
# -----------------------

if "chat_id" not in st.session_state:

    chats = list_chats()

    if chats:

        st.session_state.chat_id = chats[-1]
        st.session_state.messages = load_chat(chats[-1])

    else:

        new_chat = create_chat()

        save_chat(new_chat, [])

        st.session_state.chat_id = new_chat
        st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------
# Sidebar
# -----------------------

with st.sidebar:

    st.markdown("# 🌾 FarmwiseAI")
    st.caption("AI Analytics Dashboard")

    # New Chat
    if st.button("➕ New Chat", use_container_width=True):

        new_chat = create_chat()
        save_chat(new_chat, [])

        st.session_state.chat_id = new_chat
        st.session_state.messages = []

        st.rerun()

    st.divider()

    # Chat History
    st.subheader("💬 Chat History")

    chats = list_chats()
    chats.reverse()

    def get_chat_title(chat_id):
        messages = load_chat(chat_id)
        for msg in messages:
            if msg.get("role") == "user" and "text" in msg:
                title = msg["text"]
                return title[:30] + "..." if len(title) > 30 else title
        return "New Chat"

    for chat in chats:

        c1, c2 = st.columns([5, 1])

        chat_title = get_chat_title(chat)
        label = f"🟢 {chat_title}" if chat == st.session_state.chat_id else chat_title

        with c1:

            if st.button(
                label,
                key=f"open_{chat}",
                use_container_width=True
            ):

                st.session_state.chat_id = chat
                st.session_state.messages = load_chat(chat)

                st.rerun()

        with c2:

            if st.button(
                "🗑",
                key=f"delete_{chat}"
            ):

                delete_chat(chat)

                chats = list_chats()

                if chats:

                    st.session_state.chat_id = chats[-1]
                    st.session_state.messages = load_chat(chats[-1])

                else:

                    new_chat = create_chat()
                    save_chat(new_chat, [])

                    st.session_state.chat_id = new_chat
                    st.session_state.messages = []

                st.rerun()

    st.divider()

    # Dataset Overview

    st.subheader("📊 Dataset Overview")

    st.markdown("""
<div style="
background:#3FA34D;
padding:15px;
border-radius:12px;
color:white;
">

<b>🌍 Countries</b> : 101<br><br>

<b>🌱 Crop Types</b> : 10<br><br>

<b>📅 Years</b> : 1990–2013<br><br>

<b>📈 Records</b> : 28K+

</div>
""", unsafe_allow_html=True)
    st.divider()

    st.markdown(
        "<center><small>Made with ❤️ by <b>Preetha</b></small></center>",
        unsafe_allow_html=True
    )
# -----------------------
# Header
# -----------------------

st.markdown("""
# 🌾 FarmwiseAI Analytics Dashboard

### AI-powered Agricultural Intelligence

Ask questions in natural language and instantly generate charts, insights, and downloadable reports.
""")

st.divider()

# -----------------------
# KPI Cards
# -----------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("🌍 Countries", "101")
c2.metric("📅 Years", "1990-2013")
c3.metric("🌱 Crop Types", "10")
c4.metric("📈 Records", "28K+")

st.divider()

# -----------------------
# Welcome Screen
# -----------------------

if len(st.session_state.messages) == 0:

    st.info("""
### 👋 Welcome to FarmwiseAI

Try asking:

- Show average crop yield by country

The AI will generate charts automatically.
""")

# -----------------------
# Chat History
# -----------------------

for i, msg in enumerate(st.session_state.messages):

    with st.chat_message(msg["role"]):

        # Display text
        if "text" in msg:
            st.markdown(msg["text"])

        # Display chart
        if "chart" in msg:

            fig = pio.from_json(msg["chart"])

            fig.update_layout(
                height=520,
                paper_bgcolor="white",
                plot_bgcolor="white",
                margin=dict(l=20, r=20, t=50, b=20),
                font=dict(size=15)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # Display returned data
        if "data" in msg:

            # Dataset Summary Tool
            if msg.get("tool") == "dataset_summary":

                data = msg["data"]

                st.subheader("📊 Dataset Summary")

                c1, c2, c3, c4 = st.columns(4)

                c1.metric("Rows", data["rows"])
                c2.metric("Countries", data["countries"])
                c3.metric("Crops", data["crops"])
                c4.metric(
                    "Years",
                    f"{data['year_range'][0]} - {data['year_range'][1]}"
                )

                st.markdown("### Dataset Columns")

                st.write(", ".join(data["columns"]))

            # General Data Rendering (Lists or Dicts)
            else:
                data_payload = msg["data"]

                # If the payload is a dictionary of scalars (e.g. describe_metric),
                # wrap it in a list so pandas can build a single-row DataFrame.
                if isinstance(data_payload, dict):
                    if all(not isinstance(v, (list, dict)) for v in data_payload.values()):
                        data_payload = [data_payload]

                df = pd.DataFrame(data_payload)

                st.dataframe(
                    df,
                    use_container_width=True
                )

                st.download_button(
                    label="⬇ Download CSV",
                    data=df.to_csv(index=False),
                    file_name=f"analysis_{i}.csv",
                    mime="text/csv",
                    key=f"download_csv_{i}"
                )


# -----------------------
# Chat Input
# -----------------------

prompt = st.chat_input(
    "Ask anything about crop analytics..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "text": prompt
        }
    )

    with st.spinner("🌾 Analyzing crop data..."):

        try:

            backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
            response = requests.post(
                f"{backend_url}/chat",
                json={
                    "chat_id": st.session_state.chat_id,
                    "message": prompt
                }
            )

            result = response.json()

        except Exception as e:

            st.error(f"Backend Error: {e}")
            st.stop()

    assistant_message = {
        "role": "assistant"
    }

    if "message" in result:
        assistant_message["text"] = result["message"]

    if "chart" in result:
        assistant_message["chart"] = result["chart"]

    if "data" in result:
        assistant_message["data"] = result["data"]

    if "tool" in result:
        assistant_message["tool"] = result["tool"]

    st.session_state.messages.append(assistant_message)
    save_chat(st.session_state.chat_id, st.session_state.messages)  

    st.rerun()

# -----------------------
# Footer
# -----------------------

st.divider()

st.markdown(
"""
<div style="text-align:center;color:gray;">

Made with ❤️ by <b>Preetha</b>

FastAPI • Streamlit • Plotly • Groq LLM

</div>
""",
unsafe_allow_html=True
)