"""Research Task definition.

Defines the research task that instructs the research agent to find
comprehensive information on a given topic with structured output
including citations.
"""

from crewai import Task, Agent


def create_research_task(agent: Agent, topic: str) -> Task:
    """Create a research task for the given topic.

    Args:
        agent: The research agent that will execute this task.
        topic: The technical topic to research.

    Returns:
        A configured CrewAI Task for research.
    """
    return Task(
        description=(
            f"Conduct comprehensive technical research on the following topic:\n\n"
            f"'{topic}'\n\n"
            f"Your research must:\n"
            f"1. Search for information from at least 3-5 different sources\n"
            f"2. Include web articles, official documentation, and academic papers "
            f"where available\n"
            f"3. Verify key claims across multiple sources\n"
            f"4. Note any conflicting information found across sources\n"
            f"5. Provide URLs and proper citations for all sources used\n\n"
            f"Focus on accuracy and comprehensiveness. Include both foundational "
            f"concepts and recent developments related to the topic."
        ),
        expected_output=(
            "A structured research report containing:\n"
            "1. **Topic Overview**: Brief description of the research topic\n"
            "2. **Key Findings**: Numbered list of the most important findings, "
            "each with supporting evidence\n"
            "3. **Technical Details**: In-depth technical information including "
            "code examples, architecture details, or specifications where relevant\n"
            "4. **Recent Developments**: Latest news, updates, or trends related "
            "to the topic\n"
            "5. **Conflicting Information**: Any contradictions found across sources\n"
            "6. **Sources**: Complete list of all sources with URLs and brief "
            "descriptions of what was found at each source"
        ),
        agent=agent,
    )
