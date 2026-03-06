"""Job management system for EnableMind research tasks."""

import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from queue import Queue
from typing import Dict, Optional, List, Callable
import time

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobInfo:
    """Information about a research job."""
    job_id: str
    topic: str
    max_iterations: int
    status: JobStatus
    progress: int = 0  # 0-100
    stage: str = "Pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    files: Dict[str, str] = field(default_factory=dict)  # {format: filepath}

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "job_id": self.job_id,
            "topic": self.topic,
            "max_iterations": self.max_iterations,
            "status": self.status.value,
            "progress": self.progress,
            "stage": self.stage,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "files": self.files,
        }


class JobManager:
    """Singleton job manager with in-memory queue and background worker."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize job manager (only once)."""
        if self._initialized:
            return

        self._jobs: Dict[str, JobInfo] = {}
        self._job_queue: Queue = Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self._job_handler: Optional[Callable] = None
        self._cleanup_thread: Optional[threading.Thread] = None
        self._initialized = True

        logger.info("JobManager initialized")

    def start(self, job_handler: Callable):
        """Start the background worker thread.

        Args:
            job_handler: Callable that processes jobs (job_id, topic, max_iterations)
        """
        if self._running:
            logger.warning("JobManager already running")
            return

        self._job_handler = job_handler
        self._running = True

        # Start worker thread
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

        logger.info("JobManager worker threads started")

    def stop(self):
        """Stop the background worker thread."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        logger.info("JobManager stopped")

    def create_job(self, topic: str, max_iterations: int = 3) -> str:
        """Create a new research job.

        Args:
            topic: Research topic
            max_iterations: Maximum research iterations

        Returns:
            job_id: Unique job identifier
        """
        job_id = str(uuid.uuid4())
        job = JobInfo(
            job_id=job_id,
            topic=topic,
            max_iterations=max_iterations,
            status=JobStatus.PENDING,
            stage="Queued for processing"
        )

        with self._lock:
            self._jobs[job_id] = job
            self._job_queue.put(job_id)

        logger.info(f"Created job {job_id} for topic: {topic}")
        return job_id

    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Get job information by ID.

        Args:
            job_id: Job identifier

        Returns:
            JobInfo or None if not found
        """
        with self._lock:
            return self._jobs.get(job_id)

    def update_progress(self, job_id: str, progress: int, stage: str):
        """Update job progress and stage.

        Args:
            job_id: Job identifier
            progress: Progress percentage (0-100)
            stage: Stage description
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.progress = min(100, max(0, progress))
                job.stage = stage
                logger.debug(f"Job {job_id}: {progress}% - {stage}")

    def complete_job(self, job_id: str, files: Dict[str, str]):
        """Mark job as completed.

        Args:
            job_id: Job identifier
            files: Dictionary of format to filepath
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.stage = "Complete"
                job.completed_at = datetime.now()
                job.files = files
                logger.info(f"Job {job_id} completed successfully")

    def fail_job(self, job_id: str, error: str):
        """Mark job as failed.

        Args:
            job_id: Job identifier
            error: Error message
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.FAILED
                job.stage = "Failed"
                job.completed_at = datetime.now()
                job.error = error
                logger.error(f"Job {job_id} failed: {error}")

    def get_recent_jobs(self, limit: int = 10) -> List[JobInfo]:
        """Get recent completed jobs.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of JobInfo objects
        """
        with self._lock:
            completed = [
                job for job in self._jobs.values()
                if job.status == JobStatus.COMPLETED
            ]
            # Sort by completion time (most recent first)
            completed.sort(
                key=lambda j: j.completed_at or datetime.min,
                reverse=True
            )
            return completed[:limit]

    def _worker_loop(self):
        """Background worker that processes jobs from queue."""
        logger.info("Worker loop started")

        while self._running:
            try:
                # Get next job from queue (blocking with timeout)
                try:
                    job_id = self._job_queue.get(timeout=1)
                except:
                    continue

                with self._lock:
                    job = self._jobs.get(job_id)
                    if not job:
                        continue
                    job.status = JobStatus.RUNNING
                    job.started_at = datetime.now()
                    job.stage = "Starting research"
                    job.progress = 0

                logger.info(f"Processing job {job_id}: {job.topic}")

                # Process the job
                try:
                    if self._job_handler:
                        self._job_handler(job_id, job.topic, job.max_iterations)
                except Exception as e:
                    logger.exception(f"Error processing job {job_id}")
                    self.fail_job(job_id, str(e))

                self._job_queue.task_done()

            except Exception as e:
                logger.exception(f"Error in worker loop: {e}")

        logger.info("Worker loop stopped")

    def _cleanup_loop(self):
        """Background thread that cleans up old jobs."""
        while self._running:
            try:
                time.sleep(600)  # Run every 10 minutes
                self._cleanup_old_jobs()
            except Exception as e:
                logger.exception(f"Error in cleanup loop: {e}")

    def _cleanup_old_jobs(self):
        """Remove old completed/failed jobs to prevent memory leaks."""
        MAX_JOBS = 50
        MAX_AGE_HOURS = 1

        with self._lock:
            # Keep only last 50 jobs
            if len(self._jobs) > MAX_JOBS:
                sorted_jobs = sorted(
                    self._jobs.items(),
                    key=lambda x: x[1].started_at or datetime.min
                )
                to_remove = sorted_jobs[:-MAX_JOBS]
                for job_id, _ in to_remove:
                    del self._jobs[job_id]
                logger.info(f"Cleaned up {len(to_remove)} old jobs (max limit)")

            # Remove jobs older than 1 hour
            cutoff = datetime.now() - timedelta(hours=MAX_AGE_HOURS)
            old_jobs = [
                job_id for job_id, job in self._jobs.items()
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED)
                and job.completed_at
                and job.completed_at < cutoff
            ]
            for job_id in old_jobs:
                del self._jobs[job_id]

            if old_jobs:
                logger.info(f"Cleaned up {len(old_jobs)} jobs older than {MAX_AGE_HOURS}h")


# Global instance
job_manager = JobManager()
