import os
from groq import Groq
from dotenv import load_dotenv
from tool_definitions import TOOLS
load_dotenv()
client=Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
def ask_llm(messages):
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            return response.choices[0].message
        except Exception as e:
            if attempt == 2:
                raise e
            print(f"LLM Error on attempt {attempt+1}: {e}. Retrying...")