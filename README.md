# ✈️ FlexFly: Agentic Flight Arbitrage

**"Standard search engines are for people with fixed dates. FlexFly is for people with freedom."**

A Multi-Agent System powered by **DeepSeek V3** and **CrewAI** that bypasses standard flight APIs to scrape the "Hidden Web" of travel hacking forums.
<img width="785" height="634" alt="flexfly" src="https://github.com/user-attachments/assets/ae9c7f83-b019-44a3-b998-7a5420e317ee" />


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
