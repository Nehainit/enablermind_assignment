"""Analysis Task definition.

Defines the analysis task that instructs the analysis agent to synthesize
research findings, identify gaps, calculate a quality score, and optionally
delegate back to the researcher for additional information.
"""

from crewai import Task, Agent


def create_analysis_task(
    agent: Agent,
    research_task: Task,
    max_iterations: int = 3,
) -> Task:
    """Create an analysis task that processes research findings.

    Args:
        agent: The analysis agent that will execute this task.
        research_task: The research task whose output provides context.
        max_iterations: Maximum number of analysis-research iterations
            for gap filling before forcing completion.

    Returns:
        A configured CrewAI Task for analysis.
    """
    return Task(
        description=(
            f"Analyze and synthesize the research findings provided by the "
            f"Technical Research Specialist.\n\n"
            f"Your analysis must:\n"
            f"1. Synthesize all research findings into coherent themes and insights\n"
            f"2. Evaluate the quality and completeness of the research\n"
            f"3. Identify any gaps, contradictions, or areas needing clarification\n"
            f"4. Generate actionable insights and recommendations\n"
            f"5. Calculate a research quality score from 0.0 to 1.0 based on:\n"
            f"   - Source diversity (multiple types of sources)\n"
            f"   - Claim verification (findings confirmed across sources)\n"
            f"   - Coverage depth (thorough exploration of the topic)\n"
            f"   - Recency (up-to-date information)\n\n"
            f"If the quality score is below 0.7 and you have remaining iterations "
            f"(max {max_iterations}), delegate back to the Technical Research "
            f"Specialist with specific questions to fill identified gaps.\n\n"
            f"Iteration control: You may request up to {max_iterations} additional "
            f"research rounds. After that, proceed with the best available data."
        ),
        expected_output=(
            "A structured analysis containing:\n"
            "1. **Research Quality Score**: A score from 0.0 to 1.0 with justification\n"
            "2. **Executive Synthesis**: A concise synthesis of all key findings "
            "(3-5 paragraphs)\n"
            "3. **Key Insights**: Numbered list of the most important insights "
            "derived from the research\n"
            "4. **Gaps Identified**: Any gaps or areas where research was insufficient, "
            "and whether they were resolved through additional research\n"
            "5. **Contradictions**: Analysis of any conflicting information and "
            "assessment of which sources are more reliable\n"
            "6. **Recommendations**: Actionable recommendations based on the findings\n"
            "7. **Confidence Assessment**: Overall confidence level in the findings "
            "and any caveats"
        ),
        agent=agent,
        context=[research_task],
    )
