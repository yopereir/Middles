# Tech Stack:
| Responsibility   | Tool / Library                              | Notes                                  |
| ---------------- | ------------------------------------------- | -------------------------------------- |
| Scraping         | `requests`, `BeautifulSoup` or `playwright` | Modularized into a scheduled job       |
| Price comparison | eBay Browse API, Amazon PA API              | Cache results, normalize product names |
| AI Model call    | `subprocess.run` with JSON in/out           | Async, error handling, retries         |
| Storage          | `jsonlines` file + SQLite                   | Reliable append, history storage       |
| Messaging        | Twilio Python SDK                           | Rate-limited notifications             |
| Orchestration    | `asyncio` / `APScheduler`                   | Non-blocking, modular                  |
| Config & secrets | `.env` + `pydantic`                         | Secure configuration                   |
