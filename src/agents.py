import os
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# 1. Setup OpenAI (Clean & Standard)
# We use gpt-4o for maximum reasoning power on your portfolio
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0.7
)

# 2. The Tool Wrapper (Kept to prevent Pydantic errors)
@tool("DuckDuckGoSearch")
def search_tool(query: str):
    """Search the web for flight deals and forum discussions."""
    return DuckDuckGoSearchRun().run(query)

def run_flight_sniper(query):
    # Agent 1: The Forum Lurker
    hunter = Agent(
        role='Flight Deal Analyst',
        goal=f'Find active "error fares" or "flash sales" matching: {query}',
        backstory="You are an expert travel hacker. You ignore generic sites like Expedia. You only trust sources like Secret Flying, Fly4Free, and FlyerTalk forums.",
        tools=[search_tool],
        verbose=True,
        llm=llm
    )

    # Agent 2: The Deal Auditor
    auditor = Agent(
        role='Deal Verifier',
        goal='Filter findings to ensure they are CURRENT (posted < 14 days ago) and actionable.',
        backstory="You are the quality control. You verify the dates and the platform (e.g., 'Book via Agoda mobile app').",
        verbose=True,
        llm=llm
    )

    # Task 1: The Targeted Search
    hunt_task = Task(
        description=f"""
        Analyze the travel intent: "{query}".
        
        Perform targeted searches on these specific "hacker" sites:
        1. site:secretflying.com {query}
        2. site:fly4free.com {query}
        3. site:flyertalk.com/forum {query}
        4. "mistake fare" {query} 2026

        Identify any deals posted in the last 30 days. Look for "Error Fare", "Open Jaw", or "Business Class" keywords.
        """,
        expected_output="A list of raw deal URLs and snippets found on these specific sites.",
        agent=hunter
    )

    # Task 2: The Clean Report
    report_task = Task(
        description="Format the active deals into a Markdown table. Columns: Route, Est. Price, Source, and Hacker Tip.",
        expected_output="A clean markdown table of flight opportunities.",
        agent=auditor
    )

    # Crew Execution
    crew = Crew(
        agents=[hunter, auditor],
        tasks=[hunt_task, report_task],
        process=Process.sequential,
        verbose=True
        # memory=True is default, works fine with OpenAI Key
    )

    return crew.kickoff()