"""Web Search Tool - Search the web using DuckDuckGo.

Provides a CrewAI-compatible tool for performing web searches
using the duckduckgo-search library (free, no API key required).
"""

from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    """Input schema for the web search tool."""

    query: str = Field(..., description="The search query to look up on the web.")
    max_results: int = Field(
        default=5,
        description="Maximum number of search results to return.",
        ge=1,
        le=20,
    )


class WebSearchTool(BaseTool):
    """Search the web using DuckDuckGo and return relevant results.

    Returns a formatted string of search results including titles,
    URLs, and snippets for each result.
    """

    name: str = "web_search"
    description: str = (
        "Search the web for information on a given query. "
        "Returns titles, URLs, and snippets from search results. "
        "Use this to find current information, documentation, and technical resources."
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        """Execute a web search and return formatted results.

        Args:
            query: The search query string.
            max_results: Maximum number of results to return.

        Returns:
            Formatted string of search results, or an error message on failure.
        """
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return "Error: duckduckgo-search package is not installed. Run: pip install duckduckgo-search"

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return f"No results found for query: '{query}'"

            formatted = []
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                url = result.get("href", "No URL")
                snippet = result.get("body", "No description")
                formatted.append(
                    f"[{i}] {title}\n    URL: {url}\n    {snippet}"
                )

            return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)

        except Exception as e:
            return f"Error performing web search for '{query}': {str(e)}"
