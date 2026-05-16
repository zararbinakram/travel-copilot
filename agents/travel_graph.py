import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage

load_dotenv()

try:
    from agents.tools import (
        get_weather,
        convert_currency,
        search_flights,
        search_hotels,
        translate_text
    )
except ImportError:
    try:
        from tools import (
            get_weather,
            convert_currency,
            search_flights,
            search_hotels,
            translate_text
        )
    except ImportError:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "tools",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools.py")
        )
        tools_module = importlib.util.load_from_spec(spec)
        spec.loader.exec_module(tools_module)
        get_weather = tools_module.get_weather
        convert_currency = tools_module.convert_currency
        search_flights = tools_module.search_flights
        search_hotels = tools_module.search_hotels
        translate_text = tools_module.translate_text

SYSTEM_PROMPT = """You are Travel Copilot, a smart and friendly AI travel assistant.
You help travelers with flights, hotels, weather, currency, and translation.
Always be helpful, friendly and concise.
Never show tool names or function calls in your response.
When user gives a city name for flights, convert it to IATA code automatically."""

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