"""Download routes - serve generated reports."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from web.services.job_manager import job_manager, JobStatus

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed formats and their MIME types
ALLOWED_FORMATS = {
    "md": "text/markdown",
    "markdown": "text/markdown",
    "pdf": "application/pdf",
    "html": "text/html",
}


@router.get("/download/{job_id}/{format}")
async def download_report(job_id: str, format: str):
    """Download a generated report file.

    Args:
        job_id: Job identifier
        format: File format (md/markdown/pdf/html)

    Returns:
        File download response
    """
    # Normalize format
    format = format.lower()

    # Validate format
    if format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Allowed: {', '.join(ALLOWED_FORMATS.keys())}"
        )

    # Get job
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if job is completed
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed (status: {job.status.value})"
        )

    # Normalize format key for files dict
    file_key = "markdown" if format in ["md", "markdown"] else format

    # Get file path
    file_path = job.files.get(file_key)

    if not file_path:
        raise HTTPException(
            status_code=404,
            detail=f"Report file not available in {format} format"
        )

    # Check if file exists
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found on disk: {file_path}")
        raise HTTPException(
            status_code=404,
            detail="Report file not found on disk"
        )

    # Generate filename for download
    safe_topic = job.topic[:50].replace(" ", "_")
    download_filename = f"{safe_topic}.{format}"

    # Serve file
    return FileResponse(
        path=str(path),
        media_type=ALLOWED_FORMATS[format],
        filename=download_filename,
        headers={
            "Content-Disposition": f'attachment; filename="{download_filename}"'
        }
    )
