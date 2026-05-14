import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from agents.tools import (
    get_weather,
    convert_currency,
    search_flights,
    search_hotels,
    translate_text
)

load_dotenv()

SYSTEM_PROMPT = """You are Travel Copilot, a smart and friendly AI travel assistant.

You help travelers with:
- Searching flights (use IATA codes e.g. ISB=Islamabad, DXB=Dubai, LHR=London)
- Finding hotels in any city
- Checking weather at destinations
- Converting currencies
- Translating text for travelers

Rules:
- Always be helpful, friendly and concise
- Never show tool names or function calls in your response
- Always show only the final clean answer to the user
- When user gives a city name for flights, convert it to IATA code automatically
- If user asks about Pakistan tourism give extra helpful tips
- If you cannot find something, say so honestly"""

tools = [
    get_weather,
    convert_currency,
    search_flights,
    search_hotels,
    translate_text
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT
)

def run_agent(message: str, history: list) -> str:
    try:
        messages = history + [{"role": "user", "content": message}]
        result = agent.invoke({"messages": messages})
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content
        return "Sorry I could not process that. Please try again."
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"