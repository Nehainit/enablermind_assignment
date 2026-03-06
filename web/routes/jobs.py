"""Job status routes - tracking and polling."""

import logging
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from web.services.job_manager import job_manager, JobStatus

logger = logging.getLogger(__name__)

router = APIRouter()

# Setup templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/job/{job_id}", response_class=HTMLResponse)
async def job_status_page(request: Request, job_id: str):
    """Render job status page with progress tracking.

    Args:
        job_id: Job identifier

    Returns:
        HTML page with HTMX polling
    """
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return templates.TemplateResponse(
        "job_status.html",
        {
            "request": request,
            "job": job,
        }
    )


@router.get("/api/job/{job_id}/status")
async def job_status_api(request: Request, job_id: str):
    """Get job status for HTMX polling.

    This endpoint is called every 2 seconds by HTMX to update progress.

    Args:
        request: Request object for templating
        job_id: Job identifier

    Returns:
        HTML fragment with progress bar component
    """
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Return HTML fragment for HTMX
    return templates.TemplateResponse(
        "components/progress_bar.html",
        {"request": request, "job": job},
    )


@router.get("/api/jobs/history")
async def jobs_history():
    """Get list of recent completed jobs.

    Returns:
        JSON array of recent jobs
    """
    recent_jobs = job_manager.get_recent_jobs(limit=10)

    return JSONResponse(
        content={
            "jobs": [job.to_dict() for job in recent_jobs]
        }
    )
