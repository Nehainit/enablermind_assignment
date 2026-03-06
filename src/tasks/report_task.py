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
            "and code blocks where appropriate\n"
            f"6. Export the report to BOTH formats:\n"
            f"   - Markdown: export_markdown(content=your_report, filename='{filename}')\n"
            f"   - PDF: export_pdf(content=your_report, filename='{filename}')\n\n"
            "The report should be suitable for a technical audience and maintain "
            "a professional tone throughout. Ensure all claims are properly "
            "cited with references to the original sources.\n\n"
            f"IMPORTANT: Use the filename '{filename}' when exporting the report."
        ),
        expected_output=(
            "A polished research report in the following structure:\n"
            "1. **Executive Summary** (under 200 words)\n"
            "2. **Introduction**: Background and scope of the research\n"
            "3. **Key Findings**: The most important discoveries, numbered\n"
            "4. **Detailed Analysis**: In-depth exploration of each finding "
            "with supporting evidence\n"
            "5. **Recommendations**: Actionable next steps based on the research\n"
            "6. **Conclusion**: Summary of the research significance\n"
            "7. **Sources**: Complete bibliography with URLs\n\n"
            f"The report must be exported to BOTH formats:\n"
            f"- Markdown: outputs/{filename}.md\n"
            f"- PDF: outputs/{filename}.pdf (with professional formatting)"
        ),
        agent=agent,
        context=[research_task, analysis_task],
    )
