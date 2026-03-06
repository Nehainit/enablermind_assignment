"""Web Scraper Tool - Extract content from web pages.

Provides a CrewAI-compatible tool for scraping and extracting
text content from web pages using requests and BeautifulSoup.
"""

from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WebScraperInput(BaseModel):
    """Input schema for the web scraper tool."""

    url: str = Field(..., description="The URL of the web page to scrape.")
    max_length: int = Field(
        default=5000,
        description="Maximum character length of extracted content.",
        ge=100,
        le=50000,
    )


class WebScraperTool(BaseTool):
    """Scrape and extract text content from a web page.

    Fetches the page HTML and extracts readable text content,
    removing scripts, styles, and navigation elements.
    """

    name: str = "web_scraper"
    description: str = (
        "Scrape and extract the main text content from a web page URL. "
        "Use this to read the full content of articles, documentation pages, "
        "or any web page found through search."
    )
    args_schema: Type[BaseModel] = WebScraperInput

    def _run(self, url: str, max_length: int = 5000) -> str:
        """Fetch and extract text content from a web page.

        Args:
            url: The URL to scrape.
            max_length: Maximum character length of the returned content.

        Returns:
            Extracted text content, or an error message on failure.
        """
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            return "Error: requests and/or beautifulsoup4 packages are not installed."

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
                tag.decompose()

            # Extract text from the main content area, falling back to body
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", {"role": "main"})
                or soup.find("body")
            )

            if main_content is None:
                return f"Error: Could not extract content from {url}"

            # Get text and clean up whitespace
            lines = main_content.get_text(separator="\n").splitlines()
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            text = "\n".join(cleaned_lines)

            if not text:
                return f"Error: No readable text content found at {url}"

            # Truncate if needed
            if len(text) > max_length:
                text = text[:max_length] + "\n\n[Content truncated...]"

            return f"Content from {url}:\n\n{text}"

        except requests.exceptions.Timeout:
            return f"Error: Request timed out while fetching {url}"
        except requests.exceptions.HTTPError as e:
            return f"Error: HTTP {e.response.status_code} when fetching {url}"
        except requests.exceptions.ConnectionError:
            return f"Error: Could not connect to {url}"
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"
