# ✈️ FlexFly: Agentic Flight Arbitrage

**Standard search engines are for people with fixed dates. FlexFly is for people with freedom.**

A Multi-Agent System powered by **DeepSeek V3** and **CrewAI** that bypasses standard flight APIs to scrape the "Hidden Web" of travel hacking forums.

<img width="773" height="657" alt="flexfly" src="https://github.com/user-attachments/assets/a1b4c28c-d264-4734-b037-af1c6d8b86da" />

## 🤖 The Architecture
Unlike Expedia or Skyscanner which query rigid GDS databases, FlexFly employs two autonomous agents:

1.  **The Forum Lurker (Agent A):** Uses advanced search operators to scan hacker forums (FlyerTalk, Secret Flying) for "Error Fares" and "Flash Sales."
2.  **The Auditor (Agent B):** Verifies the freshness of deals, filtering out expired offers from previous months.

## 🛠️ Tech Stack
* **Orchestration:** CrewAI
* **Intelligence:** DeepSeek V3 (via OpenAI Compatible API)
* **Frontend:** Streamlit (Google-Style Minimalist UI)
* **Search:** DuckDuckGo Tooling

## 🚀 Quick Start
1.  Clone repo
2.  `pip install -r requirements.txt`
3.  Add DeepSeek API Key to `.streamlit/secrets.toml`
4.  `streamlit run app.py`

---
*Built as a proof-of-concept for the Reinvention with Agentic AI Credly Badge.*
