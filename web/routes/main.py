"""Main routes - homepage and research submission."""

import logging
from pathlib import Path

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from web.services.job_manager import job_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Setup templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Render the homepage with research form."""
    # Get recent completed jobs
    recent_jobs = job_manager.get_recent_jobs(limit=5)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "recent_jobs": recent_jobs,
        }
    )


@router.post("/research")
async def submit_research(
    request: Request,
    topic: str = Form(...),
    max_iterations: int = Form(3)
):
    """Submit a new research job.

    Args:
        topic: Research topic (required, max 500 chars)
        max_iterations: Maximum research iterations (1-5, default 3)

    Returns:
        Redirect to job status page
    """
    # Validate topic
    if not topic or not topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")

    topic = topic.strip()

    if len(topic) > 500:
        raise HTTPException(
            status_code=400,
            detail="Topic too long (max 500 characters)"
        )

    # Validate max_iterations
    try:
        max_iterations = int(max_iterations)
        if max_iterations < 1 or max_iterations > 5:
            raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Max iterations must be between 1 and 5"
        )

    # Create job
    try:
        job_id = job_manager.create_job(topic=topic, max_iterations=max_iterations)
        logger.info(f"Created job {job_id} for topic: {topic}")

        # Redirect to job status page
        return RedirectResponse(
            url=f"/job/{job_id}",
            status_code=303  # See Other - proper redirect after POST
        )

    except Exception as e:
        logger.exception("Failed to create research job")
        raise HTTPException(status_code=500, detail="Failed to create research job")
