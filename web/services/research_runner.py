"""Research runner service - wraps the core EnableMind research system."""

import logging
import os
import re
import glob
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add project root and src directory to path for imports
project_root = Path(__file__).parent.parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

from src.main import create_research_crew
from web.services.job_manager import job_manager
from web.services.llm_manager import get_llm_manager, initialize_llm_manager
from config.settings import get_settings

logger = logging.getLogger(__name__)


def sanitize_topic(topic: str) -> str:
    """Sanitize topic for filename matching.

    Args:
        topic: Raw research topic

    Returns:
        Sanitized topic string matching report_task.py logic
    """
    safe_topic = re.sub(r'[^\w\s-]', '', topic.lower())
    safe_topic = re.sub(r'[-\s]+', '_', safe_topic)
    return safe_topic


def discover_output_files(topic: str, max_age_minutes: int = 10) -> Dict[str, str]:
    """Discover generated report files for a topic.

    Args:
        topic: Research topic
        max_age_minutes: Only consider files created in last N minutes

    Returns:
        Dictionary mapping format to absolute filepath
    """
    safe_topic = sanitize_topic(topic)
    output_dir = Path("./outputs")

    # Create outputs directory if it doesn't exist
    if not output_dir.exists():
        logger.info("Creating outputs directory")
        output_dir.mkdir(parents=True, exist_ok=True)

    # Find files matching pattern: {safe_topic}_{timestamp}.*
    pattern = f"{safe_topic}_*"
    files = {}

    # Check for markdown
    md_files = list(output_dir.glob(f"{pattern}.md"))
    if md_files:
        # Get most recent file
        md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        files["markdown"] = str(md_files[0].absolute())

    # Check for PDF
    pdf_files = list(output_dir.glob(f"{pattern}.pdf"))
    if pdf_files:
        pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        files["pdf"] = str(pdf_files[0].absolute())

    # Check for HTML (fallback if PDF generation failed)
    html_files = list(output_dir.glob(f"{pattern}.html"))
    if html_files:
        html_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        files["html"] = str(html_files[0].absolute())

    # Filter by age
    cutoff_time = time.time() - (max_age_minutes * 60)
    files = {
        fmt: path for fmt, path in files.items()
        if Path(path).stat().st_mtime >= cutoff_time
    }

    logger.info(f"Discovered {len(files)} output files for topic: {topic}")
    return files


def estimate_progress(elapsed_seconds: float, total_estimate: float = 180) -> int:
    """Estimate progress based on elapsed time.

    Args:
        elapsed_seconds: Seconds since job started
        total_estimate: Estimated total duration in seconds (default 3 minutes)

    Returns:
        Progress percentage (0-90, capped to avoid showing 100% before completion)
    """
    # Use sigmoid curve for natural progress feel
    # Progress accelerates early then slows
    progress = int((elapsed_seconds / total_estimate) * 100)
    return min(90, progress)  # Cap at 90% until actually complete


def update_progress_periodically(job_id: str, start_time: float, stop_event: threading.Event):
    """Background thread to update job progress periodically.

    Args:
        job_id: Job identifier
        start_time: Job start timestamp
        stop_event: Event to signal when to stop
    """
    stages = [
        (0, "Initializing research agents"),
        (15, "Gathering information from web sources"),
        (35, "Analyzing gathered data"),
        (60, "Synthesizing findings"),
        (75, "Generating comprehensive report"),
        (85, "Finalizing report and citations"),
    ]

    stage_idx = 0

    while not stop_event.is_set():
        elapsed = time.time() - start_time
        progress = estimate_progress(elapsed)

        # Update stage based on progress
        for idx, (threshold, stage_text) in enumerate(stages):
            if progress >= threshold:
                stage_idx = idx

        current_stage = stages[stage_idx][1]
        job_manager.update_progress(job_id, progress, current_stage)

        # Wait 2 seconds before next update
        stop_event.wait(2)


def is_rate_limit_error(error: Exception) -> bool:
    """Check if an error is due to rate limiting or model availability.

    Args:
        error: Exception to check

    Returns:
        True if it's a rate limit error or should trigger fallback
    """
    error_str = str(error).lower()

    # Rate limit indicators
    rate_limit_indicators = [
        "rate limit",
        "rate_limit",
        "ratelimit",
        "429",
        "quota exceeded",
        "too many requests",
        "resource exhausted",
        "capacity",
        "overloaded",
        "model_decommissioned",
        "invalid_model",
        "model not found",
    ]

    is_rate_limit = any(indicator in error_str for indicator in rate_limit_indicators)

    if is_rate_limit:
        logger.warning(f"Rate limit or model error detected: {error_str[:200]}")

    return is_rate_limit


def run_research_with_fallback(job_id: str, topic: str, max_iterations: int) -> str:
    """Run research with automatic fallback on rate limits.

    Args:
        job_id: Job identifier
        topic: Research topic
        max_iterations: Maximum research iterations

    Returns:
        Research result string

    Raises:
        Exception: If all providers fail
    """
    settings = get_settings()
    llm_manager = get_llm_manager()

    # Initialize LLM manager if not already done
    if not llm_manager.providers:
        initialize_llm_manager(settings)

    # Reset to primary provider at start of new job
    llm_manager.reset_to_primary()

    max_retries = len(llm_manager.providers)
    last_error = None

    for attempt in range(max_retries):
        try:
            # Get current LLM from manager
            current_llm = llm_manager.get_current_llm()
            provider_info = llm_manager.get_provider_info()

            job_manager.update_progress(
                job_id,
                10 + (attempt * 5),
                f"Starting research with {provider_info['current']['name']}"
            )

            logger.info(
                f"Attempt {attempt + 1}/{max_retries} with provider: {provider_info['current']['name']}"
            )

            # Create crew with current LLM
            from agents.research_agent import create_research_agent
            from agents.analysis_agent import create_analysis_agent
            from agents.report_agent import create_report_agent
            from tasks.research_task import create_research_task
            from tasks.analysis_task import create_analysis_task
            from tasks.report_task import create_report_task
            from crewai import Crew, Process

            # Create agents with the configured LLM
            research_agent = create_research_agent(llm=current_llm)
            analysis_agent = create_analysis_agent(llm=current_llm)
            report_agent = create_report_agent(llm=current_llm)

            # Create tasks
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

            # Run the crew
            result = crew.kickoff()
            logger.info(f"Research completed successfully with {provider_info['current']['name']}")

            # Save the result as a fallback in case the agent didn't use export tools
            result_str = str(result)
            safe_topic = sanitize_topic(topic)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_topic}_{timestamp}"

            # Ensure outputs directory exists
            outputs_dir = Path("./outputs")
            outputs_dir.mkdir(parents=True, exist_ok=True)

            # Save markdown
            md_path = outputs_dir / f"{filename}.md"
            with open(md_path, "w") as f:
                f.write(result_str)
            logger.info(f"Saved fallback markdown to: {md_path}")

            # Try to save HTML and PDF
            try:
                import markdown
                from datetime import datetime

                html_content = markdown.markdown(
                    result_str,
                    extensions=["extra", "tables", "fenced_code"]
                )

                current_time = datetime.now().strftime("%B %d, %Y")
                styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Research Report</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm 2cm;
        }}
        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #1a1a1a;
            font-size: 28pt;
            margin: 0 0 10px 0;
        }}
        .header p {{
            color: #666;
            font-size: 10pt;
            margin: 0;
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 20pt;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        h2 {{
            color: #2563eb;
            font-size: 16pt;
            margin-top: 25px;
        }}
        h3 {{
            color: #1e40af;
            font-size: 13pt;
            margin-top: 20px;
        }}
        p {{ margin-bottom: 10pt; text-align: justify; }}
        code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            color: #dc2626;
        }}
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            border-left: 4px solid #3b82f6;
        }}
        pre code {{
            background: transparent;
            color: #e2e8f0;
            padding: 0;
        }}
        ul, ol {{
            margin-bottom: 12pt;
            padding-left: 25pt;
        }}
        li {{
            margin-bottom: 6pt;
            line-height: 1.5;
        }}
        strong {{
            color: #1a1a1a;
            font-weight: bold;
        }}
        a {{
            color: #2563eb;
            text-decoration: none;
            word-break: break-all;
        }}
        blockquote {{
            border-left: 4px solid #d1d5db;
            padding-left: 16px;
            margin-left: 0;
            color: #6b7280;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #d1d5db;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f3f4f6;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Research Report</h1>
        <p>Generated on {current_time}</p>
    </div>
    {html_content}
</body>
</html>"""

                # Save HTML
                html_path = outputs_dir / f"{filename}.html"
                with open(html_path, "w") as f:
                    f.write(styled_html)
                logger.info(f"Saved fallback HTML to: {html_path}")

                # Try to generate PDF using WeasyPrint
                try:
                    from weasyprint import HTML
                    pdf_path = outputs_dir / f"{filename}.pdf"
                    HTML(string=styled_html).write_pdf(pdf_path)
                    logger.info(f"Saved fallback PDF to: {pdf_path}")
                except (ImportError, OSError) as pdf_error:
                    logger.warning(f"Could not generate PDF (WeasyPrint unavailable): {pdf_error}")
                    logger.info("HTML file can be opened in browser and printed to PDF")

            except Exception as e:
                logger.warning(f"Could not generate HTML/PDF: {e}")

            return result_str

        except Exception as e:
            last_error = e
            error_msg = str(e)
            logger.error(f"Research attempt {attempt + 1}/{max_retries} failed: {error_msg}")

            # Check if it's a rate limit error
            is_rate_limited = is_rate_limit_error(e)
            has_fallback = llm_manager.current_provider_index < len(llm_manager.providers) - 1

            logger.info(f"is_rate_limited={is_rate_limited}, has_fallback={has_fallback}")

            if is_rate_limited and has_fallback:
                # Try to fallback to next provider
                if llm_manager.fallback_to_next_provider():
                    next_provider = llm_manager.get_provider_info()['current']
                    logger.warning(f"Falling back to: {next_provider['name']} ({next_provider['model']})")
                    job_manager.update_progress(
                        job_id,
                        15 + (attempt * 5),
                        f"Switching to {next_provider['name']}..."
                    )
                    continue
                else:
                    logger.error("Fallback failed - no more providers")
                    raise
            else:
                # Not a rate limit error or no more fallbacks
                if not is_rate_limited:
                    logger.error(f"Non-rate-limit error, not falling back: {error_msg[:200]}")
                else:
                    logger.error("Rate limited but no fallback providers available")
                raise

    # All providers exhausted
    raise Exception(
        f"All {max_retries} LLM providers failed. Last error: {str(last_error)}"
    )


def run_research_job(job_id: str, topic: str, max_iterations: int):
    """Run a research job and update its progress.

    This is called by the JobManager worker thread.

    Args:
        job_id: Job identifier
        topic: Research topic
        max_iterations: Maximum research iterations
    """
    logger.info(f"Starting research job {job_id}: {topic}")
    start_time = time.time()

    # Start background thread for progress updates
    stop_event = threading.Event()
    progress_thread = threading.Thread(
        target=update_progress_periodically,
        args=(job_id, start_time, stop_event),
        daemon=True
    )
    progress_thread.start()

    try:
        # Initial progress
        job_manager.update_progress(job_id, 5, "Starting research crew")

        # Run research with automatic fallback
        result = run_research_with_fallback(
            job_id=job_id,
            topic=topic,
            max_iterations=max_iterations
        )

        # Stop progress updates
        stop_event.set()
        progress_thread.join(timeout=2)

        # Discover output files
        job_manager.update_progress(job_id, 95, "Discovering generated reports")

        # Ensure outputs directory exists before checking
        outputs_dir = Path("./outputs")
        outputs_dir.mkdir(parents=True, exist_ok=True)

        files = discover_output_files(topic)

        if not files:
            logger.warning(f"No output files found for job {job_id}")
            logger.warning(f"Checked directory: {outputs_dir.absolute()}")
            logger.warning(f"Directory contents: {list(outputs_dir.glob('*'))}")
            raise Exception(f"Report files not found after research. The research may have completed but file generation failed. Please try again.")

        # Mark job as complete
        job_manager.complete_job(job_id, files)

        elapsed = time.time() - start_time
        logger.info(f"Research job {job_id} completed in {elapsed:.1f}s")

    except Exception as e:
        # Stop progress updates
        stop_event.set()
        progress_thread.join(timeout=2)

        logger.exception(f"Research job {job_id} failed")
        job_manager.fail_job(job_id, str(e))
        raise
