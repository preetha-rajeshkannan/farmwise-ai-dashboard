# 🌾 FarmwiseAI Analytics Dashboard

FarmwiseAI is an AI-powered agricultural analytics dashboard that allows users to ask natural language questions about crop yields and instantly generate data tables and Plotly visualizations. 

It is built with a decoupled architecture using a **FastAPI** backend for LLM routing/data processing and a **Streamlit** frontend for the interactive user interface.

## Getting Started

Follow these steps to run the application locally on your machine.

### 1. Prerequisites
- Python 3.9+
- A [Groq API Key](https://console.groq.com/) (Free tier is perfectly fine)

### 2. Installation
First, open your terminal and navigate to the project directory. Create a virtual environment and install the required dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all required packages
pip install -r backend/requirements.txt
```

### 3. Environment Variables
In the `backend/` folder, create a new file called `.env`. Paste your Groq API key into this file:

```env
GROQ_API_KEY="your_groq_api_key_here"
```

### 4. Running the Application
Because this is a decoupled application, you need to start **both** the backend and the frontend. Open two separate terminal windows (make sure your `venv` is activated in both).

**Terminal 1 (Start the Backend):**
```bash
cd backend
uvicorn main:app --reload
```
*The FastAPI server will start running on http://127.0.0.1:8000*

**Terminal 2 (Start the Frontend):**
```bash
cd frontend
streamlit run app.py
```
*The Streamlit dashboard will automatically open in your web browser!*

---

## 🤖 AI Architecture & Tools Used

### 1. The Groq Model
The application relies on Groq for extremely fast inference. 
- **Production Model:** `meta-llama/llama-4-scout-17b-16e-instruct`
- **Why?** After testing the 8B and 70B variants, the 17B Scout model was chosen because it strikes the perfect balance. It is highly optimized for following strict coding and JSON instructions (which is required for our dynamic chart generation) without burning through the free tier token limits as fast as the 70B model.

### 2. Internal AI Tools (Function Calling)
We explicitly chose *not* to use hardcoded keyword rules (e.g. `if "yield" in query: return chart`). Instead, the LLM is given access to semantic tools:
- `generate_chart`: An internal tool defined in `tool_definitions.py`. The LLM autonomously analyzes the dataset schema and outputs a structured JSON defining the `chart_type`, `x_column`, `y_column`, and `filters`. The backend intercepts this JSON to dynamically filter Pandas dataframes and render Plotly charts.
- `dataset_summary`: Allows the LLM to fetch top-level metrics to answer high-level overview questions.

### 3. AI Coding Assistant
This project was pair-programmed using **Antigravity** (Google Deepmind's Advanced Agentic AI Assistant). It was heavily utilized for:
- Architecting the decoupled FastAPI/Streamlit structure.
- Engineering the strict system prompts to prevent out-of-scope hallucinations.
- Designing the responsive UI and CSS grid layouts in Streamlit.
- Implementing the anonymous UUID cookie system to securely sandbox concurrent chat histories for evaluators.

---

### DEPLOYED URL:
https://farmwise-ai-dashboard-preetha.streamlit.app/

*For an in-depth breakdown of the technical choices made during development, please refer to the `DECISIONS.md` file.*
