"""Task definitions for the enablemind research system."""

from src.tasks.research_task import create_research_task
from src.tasks.analysis_task import create_analysis_task
from src.tasks.report_task import create_report_task

__all__ = [
    "create_research_task",
    "create_analysis_task",
    "create_report_task",
]
