import streamlit as st
import requests
import plotly.io as pio
import pandas as pd
import os
import json
import uuid
import extra_streamlit_components as stx
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
# User Session (Cookies)
# -----------------------

cookie_manager = stx.CookieManager(key="cookies")
user_id = cookie_manager.get(cookie="farmwise_user_id")

if not user_id:
    user_id = str(uuid.uuid4())
    cookie_manager.set("farmwise_user_id", user_id)

# -----------------------
# Chat Storage
# -----------------------

CHAT_DIR = os.path.join("chats", user_id)

os.makedirs(CHAT_DIR, exist_ok=True)


def create_chat():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


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

    if st.button("➕ New Chat", use_container_width=True):
        # Don't create a new chat if the current one is already empty
        if st.session_state.get("messages"):
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
        label = f"🔴 {chat_title}" if chat == st.session_state.chat_id else chat_title

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
                "❌",
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
background: linear-gradient(135deg, #16a34a 0%, #2563eb 100%);
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
# Header & KPI Cards
# -----------------------

head_col, kpi_col = st.columns([8.5, 5.5], gap="large")

with head_col:
    st.markdown("""
    # 🌾 FarmwiseAI Analytics Dashboard
    
    ### AI-powered Agricultural Intelligence
    
    Ask questions in natural language and instantly generate charts, insights, and downloadable reports.
    """)

with kpi_col:
    # 2x2 Grid for smaller metrics
    c1, c2 = st.columns(2)
    c1.metric("🌍 Countries", "101")
    c2.metric("📅 Years", "1990-2013")
    
    c3, c4 = st.columns(2)
    c3.metric("🌱 Crop Types", "10")
    c4.metric("📈 Records", "28K+")

st.divider()

# -----------------------
# Dashboard Helper Functions
# -----------------------


@st.dialog("Full View", width="large")
def full_view_dialog(item):
    st.markdown(f"### {item['query']}")
    
    if item.get("chart"):
        fig = pio.from_json(item["chart"])
        fig.update_layout(
            height=600,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(size=15)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    if item.get("data"):
        st.divider()
        st.markdown("#### Data Source")
        
        if item.get("tool") == "dataset_summary":
            data = item["data"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows", data["rows"])
            c2.metric("Countries", data["countries"])
            c3.metric("Crops", data["crops"])
            c4.metric("Years", f"{data['year_range'][0]} - {data['year_range'][1]}")
            st.markdown("**Columns:** " + ", ".join(data["columns"]))
        else:
            data_payload = item["data"]
            if isinstance(data_payload, dict):
                if all(not isinstance(v, (list, dict)) for v in data_payload.values()):
                    data_payload = [data_payload]
            
            df = pd.DataFrame(data_payload)
            st.dataframe(df, use_container_width=True)
            
            st.download_button(
                label="⬇ Download CSV",
                data=df.to_csv(index=False),
                file_name=f"analysis_{item['id']}.csv",
                mime="text/csv",
                key=f"download_csv_modal_{item['id']}"
            )

# -----------------------
# Dashboard & Chat Layout
# -----------------------

is_expanded = st.session_state.get("chat_expanded_mode", False)

if is_expanded:
    chat_col = st.container()
else:
    dash_col, chat_col = st.columns([8.5, 5.5], gap="large")

    with dash_col:
        # Collect all charts and data from history
        history_items = []
        current_query = "Analysis"

        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                current_query = msg.get("text", "Analysis")
            elif msg["role"] == "assistant":
                if "chart" in msg or "data" in msg:
                    history_items.append({
                        "id": i,
                        "query": current_query,
                        "chart": msg.get("chart"),
                        "data": msg.get("data"),
                        "tool": msg.get("tool")
                    })
                    
        history_items.reverse() # Newest first

        if not history_items:
            st.info("""
            ### 👋 Welcome to FarmwiseAI

            Try asking:

            - Show average crop yield by country

            The AI will generate charts automatically.
            """)
        else:
            st.markdown("## 📊 Current Analysis")
            
            # Render the most recent item prominently
            latest_item = history_items[0]
            
            with st.container(border=True):
                cols = st.columns([8, 2])
                cols[0].markdown(f"**{latest_item['query']}**")
                if cols[1].button("🔍 Full View", key=f"expand_{latest_item['id']}", use_container_width=True):
                    full_view_dialog(latest_item)
                    
                if latest_item.get("chart"):
                    fig = pio.from_json(latest_item["chart"])
                    fig.update_layout(height=450, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                elif latest_item.get("data"):
                    st.success("Data successfully generated. Click 'Full View' to examine the tables.")
                    
            # Render older items in a grid
            older_items = history_items[1:]
            
            if older_items:
                st.divider()
                st.markdown("### 🕒 Previous Insights")
                
                # Create a 2-column grid
                grid_cols = st.columns(2)
                
                for idx, item in enumerate(older_items):
                    col = grid_cols[idx % 2]
                    with col:
                        with st.container(border=True):
                            st.caption(f"{item['query'][:40]}...")
                            
                            if item.get("chart"):
                                fig = pio.from_json(item["chart"])
                                # Small thumbnail layout
                                fig.update_layout(
                                    height=250, 
                                    margin=dict(l=10, r=10, t=20, b=10),
                                    showlegend=False
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            elif item.get("data"):
                                st.info("Data Table Available")
                                
                            if st.button("🔍 Expand", key=f"expand_{item['id']}", use_container_width=True):
                                full_view_dialog(item)

with chat_col:
    main_chat_wrapper = st.container(border=True)
    with main_chat_wrapper:
        c1, c2 = st.columns([6.0, 4.0])
        c1.markdown("💬 FarmVista AI")
        
        if is_expanded:
            if c2.button("✖ Collapse", key="collapse_chat_btn", use_container_width=True):
                st.session_state.chat_expanded_mode = False
                st.rerun()
        else:
            if c2.button("🔍 Expand", key="expand_chat_btn", use_container_width=True):
                st.session_state.chat_expanded_mode = True
                st.rerun()
                
        st.caption("Generate visualisations instantly with natural language.")
        
        container_height = 800 if is_expanded else 600
        chat_container = st.container(height=container_height)
        
        with chat_container:
            for i, msg in enumerate(st.session_state.messages):
                avatar = "🧑‍🌾" if msg["role"] == "user" else "🤖"
                with st.chat_message(msg["role"], avatar=avatar):
                    if msg.get("text"):
                        st.markdown(msg["text"])
                    elif msg["role"] == "assistant":
                        st.markdown("✅ Task completed.")
                        
                    # Add a button to view the chart/data directly from the chat log
                    if msg["role"] == "assistant" and ("chart" in msg or "data" in msg):
                        if st.button("🔍 View Chart in Dashboard", key=f"chat_expand_{i}"):
                            # Find the corresponding query
                            query_text = "Analysis"
                            if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                                query_text = st.session_state.messages[i-1].get("text", "Analysis")
                            
                            item = {
                                "id": f"chat_btn_{i}",
                                "query": query_text,
                                "chart": msg.get("chart"),
                                "data": msg.get("data"),
                                "tool": msg.get("tool")
                            }
                            full_view_dialog(item)
    
        # Chat Input
        prompt = st.chat_input("Ask FarmVista AI to generate a chart...")

if prompt:
    st.session_state.messages.append({"role": "user", "text": prompt})
    
    with chat_col:
        with chat_container:
            # Render the user's new message instantly
            with st.chat_message("user", avatar="🧑‍🌾"):
                st.markdown(prompt)
            # Render the generating placeholder
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("✨ Generating..."):
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
                
    assistant_message = {"role": "assistant"}
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