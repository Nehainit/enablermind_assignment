"""Feedback routes - handle user feedback and report regeneration."""

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from web.services.job_manager import job_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class FeedbackRequest(BaseModel):
    """Feedback request model."""
    job_id: str
    feedback_types: List[str]
    feedback_text: str
    additional_instructions: Optional[str] = None


@router.post("/api/feedback/regenerate")
async def regenerate_with_feedback(request: FeedbackRequest):
    """Regenerate report based on user feedback.

    Args:
        request: Feedback request with job ID and feedback details

    Returns:
        JSON with new job ID
    """
    # Get original job
    original_job = job_manager.get_job(request.job_id)

    if not original_job:
        raise HTTPException(status_code=404, detail="Original job not found")

    # Construct enhanced topic with feedback
    feedback_context = f"""
    Original Topic: {original_job.topic}

    User Feedback:
    {request.feedback_text}

    Focus Areas: {', '.join(request.feedback_types) if request.feedback_types else 'General improvement'}

    Additional Instructions: {request.additional_instructions or 'None'}

    Please generate an improved research report addressing the above feedback.
    Incorporate the user's suggestions while maintaining technical accuracy and proper citations.
    """

    # Create new job with feedback-enhanced topic
    new_job_id = job_manager.create_job(
        topic=feedback_context.strip(),
        max_iterations=original_job.max_iterations
    )

    logger.info(
        f"Created feedback job {new_job_id} based on original job {request.job_id}"
    )

    return JSONResponse(
        content={
            "success": True,
            "new_job_id": new_job_id,
            "message": "New research job created with your feedback"
        }
    )


@router.get("/api/feedback/history/{job_id}")
async def get_feedback_history(job_id: str):
    """Get feedback history for a job.

    Args:
        job_id: Job identifier

    Returns:
        JSON with feedback history
    """
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # TODO: Implement feedback history storage
    # For now, return empty history
    return JSONResponse(
        content={
            "job_id": job_id,
            "feedback_count": 0,
            "history": []
        }
    )
