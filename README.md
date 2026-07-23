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
- **Production Model:** `openai/gpt-oss-120b`
- **Why?** Migrated to OpenAI's open-source 120B model after the deprecation of Llama 4 Scout. It provides exceptional reasoning and is highly optimized for following strict coding and JSON instructions (which is required for our dynamic chart generation).

### 2. Internal AI Tools (Function Calling)
I explicitly chose *not* to use hardcoded keyword rules (e.g. `if "yield" in query: return chart`). Instead, the LLM is given access to semantic tools:
- `generate_chart`: An internal tool defined in `tool_definitions.py`. The LLM autonomously analyzes the dataset schema and outputs a structured JSON defining the `chart_type`, `x_column`, `y_column`, and `filters`. The backend intercepts this JSON to dynamically filter Pandas dataframes and render Plotly charts.
- `dataset_summary`: Allows the LLM to fetch top-level metrics to answer high-level overview questions.

### 3. AI Coding Assistant
This project was pair-programmed using **Antigravity** (Google Deepmind's Advanced Agentic AI Assistant). It was heavily utilized for:
- Architecting the decoupled FastAPI/Streamlit structure.
- Engineering the strict system prompts to prevent out-of-scope hallucinations.
- Designing the responsive UI and CSS grid layouts in Streamlit.
- Implementing the anonymous UUID cookie system to securely sandbox concurrent chat histories for evaluators.

---

## 💡 Example Dashboard Queries

Here are some example queries you can try in the dashboard to explore the data, categorized by analytical capabilities:

### 1. General Exploration & Summaries
Explore what data is available without generating charts:
* *"How many rows of data do we have, and what is the date range?"*
* *"What are all the unique crops available in this dataset?"*
* *"List all the countries included in the data."*

### 2. Aggregations & Charting
Group metrics, apply filters, and dynamically generate charts:
* *"Show me a bar chart of the average crop yield by country."*
* *"Plot a line chart showing the total pesticide usage in India over the last 10 years."*
* *"What is the total yield of Wheat, Maize, and Rice in Brazil? Show it as a pie chart."*
* *"Which 5 countries have the highest average temperature? Show a bar chart."*

### 3. Statistical Analysis & Outliers
Dive deeper with statistical insights and anomaly detection:
* *"Give me the descriptive statistics for crop yield in the United States."*
* *"Are there any outliers in pesticide usage for Potatoes?"*
* *"What is the maximum and minimum average rainfall recorded?"*

### 4. Correlation & Scatter Analysis
Find relationships between variables:
* *"Is there a correlation between average temperature and crop yield?"*
* *"Show me a scatter plot comparing pesticide usage vs. crop yield."*
* *"How does average rainfall correlate with pesticide usage in India?"*

### 5. Modifying Existing Charts
Dynamically update the current chart without losing your place:
* *"Change this to a line chart."*
* *"Sort the chart in descending order."*
* *"Only show me the top 10 results from this chart."*
* *"Filter this chart to only show data from 2010 to 2013."*

---

### DEPLOYED URL:
https://farmwise-ai-dashboard-preetha.streamlit.app/

*For an in-depth breakdown of the technical choices made during development, please refer to the `DECISIONS.md` file.*
