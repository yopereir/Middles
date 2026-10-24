import os
import mlflow
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from utils.import_env import MODEL, MODEL_URL, MODEL_API_KEY, ML_FLOW_ENDPOINT
from langchain.agents import create_agent

mlflow.set_tracking_uri(ML_FLOW_ENDPOINT)
mlflow.set_experiment("openrouter-agent")
mlflow.langchain.autolog()

#llm = ChatGoogleGenerativeAI(model=MODEL, google_api_key=MODEL_API_KEY, temperature=0)
#llm = ChatOpenAI(model=MODEL, base_url=MODEL_URL, api_key=MODEL_API_KEY, default_headers={"HTTP-Referer": "http://localhost", "X-Title": "my-agent"},)
llm = ChatOpenRouter(model=MODEL, base_url=MODEL_URL, api_key=MODEL_API_KEY)

@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Sunny in {city}"

agent = create_agent(llm, tools=[get_weather])
result = agent.invoke({"messages": [{"role": "user", "content": "weather in sf?"}]})
print(result["messages"][-1].content)