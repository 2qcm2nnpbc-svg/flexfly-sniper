"""
FlexFly - Agentic Flight Deal Search System

This module implements a multi-agent system using CrewAI to search for flight deals
from travel hacking forums and verify their freshness.
"""

import os
import logging
from time import sleep
from datetime import datetime, timezone, timedelta
from typing import Optional

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# ============================================================================
# Configuration Constants
# ============================================================================

# Deal freshness thresholds (in hours)
DEAL_FRESHNESS_THRESHOLD_HOURS = int(os.environ.get("DEAL_FRESHNESS_HOURS", "48"))
SEARCH_WINDOW_DAYS = int(os.environ.get("SEARCH_WINDOW_DAYS", "14"))

# LLM Configuration
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))

# Search Configuration
SEARCH_RETRIES = int(os.environ.get("SEARCH_RETRIES", "3"))
SEARCH_INITIAL_DELAY = int(os.environ.get("SEARCH_INITIAL_DELAY", "2"))

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Helper Functions
# ============================================================================

def audit_deal_freshness(post_date_str: str, threshold_hours: int = DEAL_FRESHNESS_THRESHOLD_HOURS) -> str:
    """
    Audit deal freshness to ensure it's not expired.
    
    Args:
        post_date_str: ISO format date string of when the deal was posted
        threshold_hours: Number of hours after which a deal is considered expired
        
    Returns:
        Status string indicating if deal is fresh or expired
        
    Raises:
        ValueError: If date string format is invalid
    """
    try:
        # Handle different date formats
        if 'T' in post_date_str:
            post_date = datetime.fromisoformat(post_date_str.replace('Z', '+00:00'))
        else:
            # Try parsing as date only
            post_date = datetime.fromisoformat(post_date_str)
        
        # Ensure timezone awareness
        if post_date.tzinfo is None:
            post_date = post_date.replace(tzinfo=timezone.utc)
        else:
            post_date = post_date.astimezone(timezone.utc)
        
        now = datetime.now(timezone.utc)
        hours_old = (now - post_date).total_seconds() / 3600
        
        if hours_old > threshold_hours:
            return f"⚠️ HIGH RISK: Likely Expired ({hours_old:.1f} hours old)"
        return f"✅ FRESH: Actionable ({hours_old:.1f} hours old)"
        
    except (ValueError, AttributeError) as e:
        logger.warning(f"Invalid date format '{post_date_str}': {e}")
        return "⚠️ UNKNOWN: Date format invalid"
    except Exception as e:
        logger.error(f"Error auditing deal freshness: {e}")
        return "⚠️ ERROR: Could not verify freshness"


def duck_duck_go_search(query: str, retries: int = SEARCH_RETRIES) -> str:
    """
    Perform DuckDuckGo search with exponential backoff retry logic.
    
    Args:
        query: Search query string
        retries: Number of retry attempts
        
    Returns:
        Search results as string, or error message if all retries fail
    """
    if not query or not query.strip():
        logger.warning("Empty search query provided")
        return "Error: Empty search query"
    
    delay = SEARCH_INITIAL_DELAY
    
    for attempt in range(retries):
        try:
            result = DuckDuckGoSearchRun().run(query)
            
            # Validate result
            if not result or not result.strip():
                logger.warning(f"Empty search result for query: {query}")
                if attempt < retries - 1:
                    logger.info(f"Retrying search (Attempt {attempt + 1}/{retries})...")
                    sleep(delay)
                    delay *= 2
                    continue
                return f"Error: No results found for '{query}'"
            
            return result
            
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"Search failed (Attempt {attempt + 1}/{retries}). Retrying in {delay}s... Error: {e}")
                sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"Search failed after {retries} attempts for query: {query}")
                return f"Error: Could not perform search for '{query}' after {retries} attempts. Last error: {str(e)}"
    
    return f"Error: Could not perform search for '{query}' after {retries} attempts."


# ============================================================================
# CrewAI Tools
# ============================================================================

@tool("DuckDuckGoSearch")
def search_tool(query: str) -> str:
    """
    Search the web for flight deals and forum discussions with retry logic.
    
    Args:
        query: Search query string
        
    Returns:
        Search results as string
    """
    return duck_duck_go_search(query)


@tool("AuditDealFreshness")
def audit_freshness_tool(post_date_str: str) -> str:
    """
    Check if a deal is still fresh based on when it was posted.
    Use this to filter out expired deals.
    
    Args:
        post_date_str: ISO format date string (e.g., '2024-01-15T10:30:00Z')
        
    Returns:
        Status string indicating deal freshness
    """
    return audit_deal_freshness(post_date_str)


# ============================================================================
# Main Function
# ============================================================================

def run_flight(query: str) -> str:
    """
    Execute the flight deal search using a multi-agent CrewAI system.
    
    Args:
        query: User's flight search query (e.g., "Business Class London to Tokyo")
        
    Returns:
        Formatted markdown table of flight opportunities
        
    Raises:
        ValueError: If API key is missing
        Exception: If crew execution fails
    """
    # Validate API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Validate query
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    logger.info(f"Starting flight search for: {query}")
    
    # Setup LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=api_key,
        temperature=LLM_TEMPERATURE
    )
    
    # Agent 1: The Forum Hunter
    hunter = Agent(
        role='Flight Deal Analyst',
        goal=f'Find active "error fares" or "flash sales" matching: {query}',
        backstory=(
            "You are an expert travel hacker with years of experience finding hidden flight deals. "
            "You ignore generic booking sites like Expedia or Skyscanner. You only trust specialized "
            "sources like Secret Flying, Fly4Free, and FlyerTalk forums where real travel hackers "
            "share genuine error fares and flash sales."
        ),
        tools=[search_tool],
        verbose=True,
        llm=llm
    )

    # Agent 2: The Deal Auditor
    auditor = Agent(
        role='Deal Verifier',
        goal=f'Filter findings to ensure they are CURRENT (posted within last {SEARCH_WINDOW_DAYS} days) and actionable.',
        backstory=(
            "You are the quality control expert. You verify deal dates, check if deals are still active, "
            "and ensure the booking platform is clearly specified (e.g., 'Book via Agoda mobile app'). "
            "You use the audit_freshness_tool to verify deal freshness. You reject any deals older than "
            f"{DEAL_FRESHNESS_THRESHOLD_HOURS} hours as they are likely expired."
        ),
        tools=[audit_freshness_tool],
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
        4. "mistake fare" {query}
        5. "error fare" {query}

        Identify any deals posted in the last {SEARCH_WINDOW_DAYS} days. Look for "Error Fare", 
        "Open Jaw", "Business Class", "Flash Sale", or "Mistake Fare" keywords.
        
        For each deal found, extract:
        - Route (origin to destination)
        - Estimated price
        - Source URL
        - Post date (if available)
        - Booking instructions
        """,
        expected_output=(
            "A comprehensive list of raw deal URLs, snippets, and metadata found on these "
            "specific sites, including post dates when available."
        ),
        agent=hunter
    )

    # Task 2: The Clean Report
    report_task = Task(
        description=(
            f"Review the deals found by the Flight Deal Analyst. Use the audit_freshness_tool "
            f"to verify each deal is still fresh (posted within last {DEAL_FRESHNESS_THRESHOLD_HOURS} hours). "
            f"Filter out any deals older than {SEARCH_WINDOW_DAYS} days or that appear expired.\n\n"
            "Format the active, fresh deals into a clean Markdown table with these columns:\n"
            "- **Route**: Origin to Destination\n"
            "- **Est. Price**: Estimated cost\n"
            "- **Source**: URL or forum name\n"
            "- **Freshness**: Result from audit_freshness_tool\n"
            "- **Hacker Tip**: Specific booking instructions or tips\n\n"
            "Only include deals that are verified as fresh and actionable."
        ),
        expected_output="A clean markdown table of verified, fresh flight opportunities.",
        agent=auditor,
        context=[hunt_task]  # Explicit dependency on hunt_task
    )

    # Crew Execution
    crew = Crew(
        agents=[hunter, auditor],
        tasks=[hunt_task, report_task],
        process=Process.sequential,
        verbose=True
    )

    try:
        result = crew.kickoff()
        logger.info("Flight search completed successfully")
        return str(result)
    except Exception as e:
        logger.error(f"Error during crew execution: {e}")
        raise
