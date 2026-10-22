from deepagents import create_deep_agent
from utils.import_env import MODEL

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    model=MODEL,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Capture the response in a variable
response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
# Print AI last response to stdout.
print(response["messages"][-1].content[0]["text"])