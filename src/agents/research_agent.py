"""Research Agent - Technical Research Specialist.

Responsible for searching multiple sources (web, documentation, papers),
extracting and validating information on a given technical topic.
"""

from crewai import Agent

from src.tools.search_tool import WebSearchTool
from src.tools.scraper_tool import WebScraperTool


def create_research_agent(llm=None) -> Agent:
    """Create and return the research agent with web search and scraping tools.

    The research agent is a Technical Research Specialist that searches
    multiple sources, extracts information, and validates findings.
    It does not delegate work to other agents.
    """
    agent_config = {
        "role": "Technical Research Specialist",
        "goal": (
            "Conduct thorough technical research on the given topic by searching "
            "multiple sources including web pages, documentation, and academic papers. "
            "Extract accurate, up-to-date information and validate findings across sources."
        ),
        "backstory": (
            "You are an expert technical researcher with years of experience in "
            "finding, evaluating, and synthesizing information from diverse sources. "
            "You are meticulous about verifying facts across multiple references and "
            "always provide proper citations. You know how to search effectively, "
            "identify authoritative sources, and extract the most relevant information "
            "from lengthy documents."
        ),
        "tools": [WebSearchTool(), WebScraperTool()],
        "allow_delegation": False,
        "verbose": True,
        "max_iter": 5,
        "max_retry_limit": 3,
    }

    if llm:
        agent_config["llm"] = llm

    return Agent(**agent_config)
