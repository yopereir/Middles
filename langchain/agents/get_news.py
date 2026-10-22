import feedparser
from deepagents import create_deep_agent

def get_google_news() -> str:
    """Fetch the latest top news headlines from news.google.com."""
    url = "https://news.google.com/rss"
    feed = feedparser.parse(url)
    
    if not feed.entries:
        return "Could not fetch news at this time."
        
    headlines = []
    # Extract the top 5 latest news articles
    for entry in feed.entries[:5]:
        headlines.append(f"- {entry.title}")
        
    return "\n".join(headlines)

# 1. Create the agent and equip it with the news tool
agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    tools=[get_google_news],
    system_prompt="You are a helpful news assistant. Use your tools to fetch and summarize the latest news for the user."
)

# 2. Instruct the agent to find the news
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Find the latest news on news.google.com"}]}
)

# 3. Print the output cleanly to stdout
final_message = response["messages"][-1]

if isinstance(final_message.content, list):
    print(final_message.content[0]["text"])
else:
    print(final_message.content)