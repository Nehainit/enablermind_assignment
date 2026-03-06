"""Report Generation Agent - Technical Writer.

Responsible for structuring findings into a coherent report with
executive summary, key findings, detailed analysis, and sources.
Exports to markdown and PDF formats.
"""

from crewai import Agent

from src.tools.export_tool import MarkdownExportTool, PDFExportTool


def create_report_agent(llm=None) -> Agent:
    """Create and return the report generation agent.

    The report agent is a Technical Writer that structures findings
    into a polished report with proper formatting, citations, and
    executive summary. It exports to markdown and PDF.

    Args:
        llm: Optional LLM instance to use for the agent.
    """
    agent_config = {
        "role": "Technical Writer",
        "goal": (
            "Create a well-structured, professional research report from the "
            "analyzed findings. The report must include an executive summary "
            "(under 200 words), key findings, detailed analysis sections, and "
            "a comprehensive list of sources with proper citations. Export the "
            "final report in both markdown and PDF formats."
        ),
        "backstory": (
            "You are an experienced technical writer who specializes in creating "
            "clear, well-organized research reports. You know how to distill "
            "complex technical analysis into readable prose while maintaining "
            "accuracy. You always include proper citations, create informative "
            "executive summaries, and structure reports for maximum clarity. "
            "You take pride in producing publication-ready documents."
        ),
        "tools": [MarkdownExportTool(), PDFExportTool()],
        "allow_delegation": False,
        "verbose": True,
        "max_iter": 5,
        "max_retry_limit": 2,
    }

    if llm:
        agent_config["llm"] = llm

    return Agent(**agent_config)
