"""Report Generation Task definition.

Defines the report task that instructs the report agent to produce
a structured report with executive summary, findings, analysis,
and sources, exported as markdown and PDF.
"""

from crewai import Task, Agent
import re
from datetime import datetime


def create_report_task(
    agent: Agent,
    research_task: Task,
    analysis_task: Task,
    topic: str = "research",
) -> Task:
    """Create a report generation task.

    Args:
        agent: The report agent that will execute this task.
        research_task: The research task whose output provides source material.
        analysis_task: The analysis task whose output provides analyzed findings.
        topic: The research topic (for filename generation).

    Returns:
        A configured CrewAI Task for report generation.
    """
    # Generate filename from topic
    safe_topic = re.sub(r'[^\w\s-]', '', topic.lower())
    safe_topic = re.sub(r'[-\s]+', '_', safe_topic)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}"

    return Task(
        description=(
            "Generate a comprehensive, professional research report based on "
            "the research findings and analysis provided.\n\n"
            "Your report must:\n"
            "1. Start with an Executive Summary (under 200 words) that captures "
            "the most important findings and recommendations\n"
            "2. Include a Key Findings section with the top insights\n"
            "3. Provide a Detailed Analysis section with in-depth discussion\n"
            "4. Include a Sources section with all references and URLs\n"
            "5. Use proper markdown formatting with headers, bullet points, "
            "and code blocks where appropriate\n\n"
            "The report should be suitable for a technical audience and maintain "
            "a professional tone throughout. Ensure all claims are properly "
            "cited with references to the original sources."
        ),
        expected_output=(
            "A polished research report in markdown format with the following structure:\n\n"
            "# Executive Summary\n"
            "(under 200 words)\n\n"
            "# Introduction\n"
            "Background and scope of the research\n\n"
            "# Key Findings\n"
            "The most important discoveries, numbered\n\n"
            "# Detailed Analysis\n"
            "In-depth exploration of each finding with supporting evidence\n\n"
            "# Recommendations\n"
            "Actionable next steps based on the research\n\n"
            "# Conclusion\n"
            "Summary of the research significance\n\n"
            "# Sources\n"
            "Complete bibliography with URLs"
        ),
        agent=agent,
        context=[research_task, analysis_task],
        output_file=f"outputs/{filename}.md",
    )
