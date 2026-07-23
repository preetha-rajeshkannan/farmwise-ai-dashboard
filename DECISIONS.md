# Architectural & Design Decisions

This document summarizes the major architectural and implementation decisions made during the development of the **FarmwiseAI Analytics Dashboard**. Each decision explains the chosen approach, the alternatives considered, and the reasoning behind the final implementation.


# 1. AI-Driven Chart Generation

## Decision
Use **LLM Tool Calling (Function Calling)** instead of hardcoded keyword-based chart selection.

## Why?

Traditional dashboards often rely on manually written rules such as:

```python
if "yield" in query:
    return bar_chart()

if "rainfall" in query:
    return line_chart()
```

While simple, this approach quickly becomes difficult to maintain and cannot understand natural language variations or complex analytical questions.

Instead, FarmwiseAI allows the language model to determine:

- whether a visualization is required,
- which chart type is most appropriate,
- which dataset columns should be plotted,
- which filters should be applied,
- and which aggregation should be performed.

The backend simply executes the tool requested by the model.

---

## Implementation

The LLM receives:

- complete dataset schema
- available analytical tools
- chart generation tool definition
- visualization rules
- conversation history

When a user asks:

> Compare rice yield in India and Brazil over the last five years.

the model automatically generates a structured tool call similar to:

```json
{
  "chart_type": "line",
  "x_column": "Year",
  "y_column": "Yield",
  "filters": {
    "Country": ["India", "Brazil"],
    "Crop": "Rice"
  }
}
```

The backend:

1. validates the tool call
2. filters the dataset using Pandas
3. generates Plotly visualizations
4. returns both the chart and conversational explanation

---

## Advantages

- No hardcoded chart rules
- Understands natural language
- Easily extensible
- Supports unseen user queries
- Cleaner backend architecture
- Separation between reasoning (LLM) and execution (backend)

---

## Trade-offs

- Requires prompt engineering
- Depends on accurate tool definitions
- Slightly higher latency than rule-based systems

---

# 2. Conversation Memory

## Decision

Maintain persistent conversations using **UUID-based browser sessions** instead of relying solely on Streamlit session state.

---

## Problem

Streamlit's default `st.session_state`

- disappears after page refresh
- is tied only to the current browser session
- cannot restore previous chats

This creates a poor conversational experience.

---

## Solution

Every anonymous visitor receives a unique UUID stored inside browser cookies.

Example:

```
farmwise_user_id
```

Each UUID owns an isolated folder:

```
chats/
    8c18d7d5...
        chat1.json
        chat2.json
```

Conversation history is loaded automatically whenever the same browser reconnects.

---

## Benefits

- Conversation survives refresh
- Multiple evaluators remain isolated
- No login required
- Lightweight storage
- Simple deployment

---

## Trade-offs

- Local file storage is not suitable for very large deployments
- Database storage would be preferred in production

---

# 3. Context Preservation

## Decision

Pass previous conversation history back to the LLM for every request.

---

## Why?

Without conversational context, the chatbot cannot resolve follow-up questions.

Example:

User:

> Show rice yield in India.

Later:

> Now compare it with Brazil.

Without memory:

The model does not know what "it" refers to.

With memory:

The backend reloads previous messages before every API request.

This enables natural conversations.

---

## Benefits

- Multi-turn conversations
- Context-aware responses
- Better analytical experience
- Human-like interaction

---

# 4. Overcoming AI Hallucinations

## Decision

Implement a multi-layered defense system to strictly bound the LLM to the provided dataset and prevent hallucinations.

---

## Why?

LLMs naturally attempt to answer every question, even when information does not exist. Left unchecked, a data analytics AI will confidently hallucinate metrics, countries, or crops that are not actually in the CSV.

To preserve analytical integrity, the chatbot enforces strict factual accuracy.

---

## How Hallucinations Were Overcome

I implemented a 4-layer defense architecture to prevent the AI from making things up:

### 1. System Prompt Bounding
The system prompt strictly commands the AI to act as an agricultural expert and absolutely refuse any queries outside the domain.
* **Example**: If asked *"Which tractor brand is best?"*, it politely refuses.

### 2. Dynamic Schema Injection
The exact dataset schema, column names, and allowed metric types are injected into the system prompt. The model knows exactly what variables it is allowed to plot, preventing it from hallucinating non-existent columns (like "GDP").

### 3. Data Verification Tools
Before making an aggregate chart, the LLM is given access to a `list_unique_values` tool. If a user asks about "Corn", the AI can query the database, realize "Corn" is actually listed as "Maize", and use the correct factual term.

### 4. Backend Validation (Python Layer)
Even if the AI hallucinates a filter (e.g., trying to filter for "Mars" as a country), the Python backend intercepts the tool call. The `apply_filters` function strictly checks the requested filter against `df[column].unique()`. If the value doesn't exist, it throws an error back to the LLM, forcing the AI to self-correct rather than silently failing or hallucinating data.

---

## Benefits

- Guarantees 100% factual insights based *only* on the CSV data.
- Prevents fabricated metrics or hallucinated countries.
- Maintains enterprise-grade user trust.

---

# 5. Chart Rendering Framework

## Decision

Use Plotly for all visualizations.

---

## Why Plotly?

Plotly provides:

- Interactive charts
- Zoom
- Hover tooltips
- Responsive layouts
- Easy integration with Streamlit

---

## Advantages

- Professional appearance
- Interactive analytics
- Rich visualization support

---

# 6. Backend Architecture

## Decision

Separate the application into independent services.

```
Frontend
(Streamlit)
      │
      │ REST API
      ▼
Backend
(FastAPI)
      │
      ▼
Groq API

      │
      ▼
Plotly + Pandas
```

---

## Why?

Separating responsibilities improves maintainability.

### Streamlit

Responsible for:

- UI
- Chat interface
- Displaying charts

### FastAPI

Responsible for:

- LLM communication
- Tool execution
- Data processing
- Conversation history

---

## Benefits

- Modular architecture
- Easier debugging
- Independent deployment
- Better scalability

---

# 7. AI Model Selection

During development, several Groq-hosted models were evaluated before selecting the final production model.

---

## Model 1

### llama-3.1-8b-instant

### Why it was selected

- Extremely fast
- Low latency
- Excellent for conversational tasks
- Ideal for rapid prototyping

### Limitations encountered

The model quickly reached Groq's token-per-minute quota because every request included:

- dataset schema
- tool definitions
- visualization instructions
- conversation history

These larger prompts consumed tokens rapidly.

### Pros

- Very fast
- Low cost
- Great for simple chat

### Cons

- Lower reasoning capability
- Smaller context handling
- Frequent rate-limit interruptions for analytics workloads

---

## Model 2

### llama-3.3-70b-versatile

### Why it was selected

The 70B model provides significantly stronger reasoning abilities, making it suitable for interpreting complex analytical queries and generating accurate JSON tool calls.

### Limitations encountered

Groq Free Tier limits this model to approximately **100,000 tokens per day**.

During testing, the application consumed nearly the entire daily allocation (around **99,364 tokens**), after which requests were rejected until the quota reset.

### Pros

- Excellent reasoning
- Highly accurate tool calling
- Better handling of complex prompts
- Strong natural language understanding

### Cons

- Daily token quota exhausted quickly
- Higher computational cost
- Less suitable for prolonged testing on the free tier

---

## Model 3

### gemma2-9b-it

### Why it was selected

Google's Gemma model was evaluated because Groq maintains separate usage quotas for different model families, allowing development to continue after exhausting the Llama quotas.

### Limitations encountered

Although the model performed adequately, its responses were less consistent when producing strict JSON structures required for tool calling. To improve reliability, a different model was chosen.

### Pros

- Separate usage quota
- Good conversational quality
- Efficient performance

### Cons

- Less reliable structured output
- Required additional validation for JSON generation

---

## Final Production Model

### openai/gpt-oss-120b

### Why this model was chosen

After the deprecation of Llama 4 Scout, we migrated to OpenAI's open-source 120B model. It provides exceptional reasoning capabilities and highly reliable function calling for our tool usage.

It consistently generated valid structured outputs.

### Advantages

- Excellent structured JSON generation
- Strong reasoning
- Optimized for instruction following
- Reliable chart generation

### Limitations

- Slightly slower than 8B models
- Still dependent on Groq API rate limits

---

## Final Decision

**Selected Model**

> **openai/gpt-oss-120b**

It offered the best overall trade-off between:

- reasoning quality
- structured tool calling
- latency
- API quota efficiency
- deployment reliability

making it the most suitable model for FarmwiseAI.

---

# 8. Why Groq API?

## Decision

Use the **Groq API** as the inference provider for all LLM interactions.

---

## Why?

The application requires real-time responses for conversational analytics and chart generation. Groq's hardware-accelerated inference provides significantly lower latency compared to many traditional cloud-hosted LLM APIs.

Additionally, Groq offers access to multiple open-source models through a unified API, allowing models to be switched during development without major code changes.

---

## Advantages

- Very low inference latency
- Easy integration through a single API
- Access to multiple open-source LLMs
- Ideal for rapid experimentation
- Free-tier availability for development
- Supports function/tool calling

---

## Limitations

- Rate limits on the free tier
- Daily token quotas for some models
- Model availability may change
- Requires internet connectivity

---

### DEPLOYED URL:
https://farmwise-ai-dashboard-preetha.streamlit.app/


# Summary of Key Decisions

| **Area**                     | **Decision**                                 |
|------------------------------|----------------------------------------------|
| Visualization                | LLM Tool Calling (Function Calling)          |
| Conversation Memory          | UUID-based Persistent Chat History           |
| Context Preservation         | Previous Conversation Passed to the LLM      |
| Hallucination Prevention     | Dataset-Bounded System Prompt                |
| Chart Rendering              | Plotly                                       |
| Backend Framework            | FastAPI                                      |
| Frontend Framework           | Streamlit                                    |
| Data Processing              | Pandas                                       |
| LLM Provider                 | Groq API                                     |
| Production Model             | `openai/gpt-oss-120b`  |
