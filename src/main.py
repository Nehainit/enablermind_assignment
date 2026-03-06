"""Main orchestration module for the enablemind research system.

Sets up the CrewAI crew with all agents and tasks, and provides
a CLI for running research on a given topic.
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structlog

from config.settings import get_settings
from agents.research_agent import create_research_agent
from agents.analysis_agent import create_analysis_agent
from agents.report_agent import create_report_agent
from tasks.research_task import create_research_task
from tasks.analysis_task import create_analysis_task
from tasks.report_task import create_report_task
from utils.logging_config import setup_logging

try:
    from crewai import Crew, Process, LLM
except ImportError:
    print(
        "Error: crewai package is not installed. Run: pip install crewai",
        file=sys.stderr,
    )
    sys.exit(1)


def create_research_crew(topic: str, max_iterations: int = 3) -> Crew:
    """Create a fully configured research crew for the given topic.

    Args:
        topic: The technical topic to research.
        max_iterations: Maximum feedback loop iterations between
            the analysis and research agents.

    Returns:
        A configured CrewAI Crew ready to be kicked off.
    """
    settings = get_settings()

    # Configure LLM based on provider
    llm = LLM(
        model=settings.get_model(),
        api_key=settings.get_api_key(),
        base_url=settings.get_api_base(),
    )

    # Create agents with the configured LLM
    research_agent = create_research_agent(llm=llm)
    analysis_agent = create_analysis_agent(llm=llm)
    report_agent = create_report_agent(llm=llm)

    # Create tasks (order matters for the sequential process)
    research_task = create_research_task(agent=research_agent, topic=topic)
    analysis_task = create_analysis_task(
        agent=analysis_agent,
        research_task=research_task,
        max_iterations=max_iterations,
    )
    report_task = create_report_task(
        agent=report_agent,
        research_task=research_task,
        analysis_task=analysis_task,
        topic=topic,
    )

    # Assemble the crew
    crew = Crew(
        agents=[research_agent, analysis_agent, report_agent],
        tasks=[research_task, analysis_task, report_task],
        process=Process.sequential,
        memory=True,
        verbose=True,
    )

    return crew


def run(topic: str, max_iterations: int = 3) -> str:
    """Run the research crew on a topic and return the result.

    Args:
        topic: The technical topic to research.
        max_iterations: Maximum feedback loop iterations.

    Returns:
        The final crew output as a string.
    """
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = structlog.get_logger("enablemind")

    logger.info("starting_research", topic=topic, max_iterations=max_iterations)

    crew = create_research_crew(topic=topic, max_iterations=max_iterations)

    try:
        result = crew.kickoff()
        logger.info("research_complete", topic=topic)
        return str(result)
    except Exception:
        logger.exception("research_failed", topic=topic)
        raise


def main() -> None:
    """CLI entry point for the enablemind research system."""
    parser = argparse.ArgumentParser(
        description="enablemind - AI-powered technical research system",
    )
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="The technical topic to research.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum feedback loop iterations between analysis and research agents. "
        "Defaults to the value in settings (MAX_RESEARCH_ITERATIONS or 3).",
    )

    args = parser.parse_args()

    settings = get_settings()
    max_iterations = args.max_iterations or settings.max_research_iterations

    try:
        result = run(topic=args.topic, max_iterations=max_iterations)
        print("\n" + "=" * 60)
        print("RESEARCH COMPLETE")
        print("=" * 60)
        print(result)
    except KeyboardInterrupt:
        print("\nResearch interrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"\nResearch failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
