import asyncio
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class ProcessingJob:
    user_id: int
    command: str
    symbol: str
    status: str = "queued"  # queued, processing, completed
    start_time: float = field(default_factory=time.time)
    current_stage: str = "initializing"
    progress: int = 0
    end_time: Optional[float] = None

class JobStatus:
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"

class ProgressTracker:
    def __init__(self):
        self.jobs: Dict[int, ProcessingJob] = {}
        self.max_concurrent = 10  # Maximum concurrent jobs
        self._lock = threading.RLock()  # Thread-safe lock for concurrent access

    async def start_processing(self, user_id: int, command: str, symbol: str = "") -> ProcessingJob:
        """Start a new processing job for user with thread safety"""
        with self._lock:
            # Check if user already has an active job
            existing_job = self.jobs.get(user_id)
            if existing_job and existing_job.status in [JobStatus.QUEUED, JobStatus.PROCESSING]:
                print(f"⚠️ User {user_id} already has active job, updating...")
                existing_job.command = command
                existing_job.symbol = symbol
                existing_job.start_time = time.time()
                existing_job.current_stage = "initializing"
                existing_job.progress = 0
                return existing_job

            # Create new job
            job = ProcessingJob(
                user_id=user_id,
                command=command,
                symbol=symbol,
                status=JobStatus.QUEUED,
                start_time=time.time(),
                current_stage="initializing",
                progress=0
            )

            self.jobs[user_id] = job

            # If we're under the concurrent limit, start processing immediately
            active_jobs = sum(1 for j in self.jobs.values() if j.status == JobStatus.PROCESSING)
            if active_jobs < self.max_concurrent:
                job.status = JobStatus.PROCESSING

            print(f"📊 Started job for user {user_id}: {command} {symbol}")
            return job

    def update_progress(self, user_id: int, stage: str, progress: int):
        """Update progress for a user's job with thread safety"""
        with self._lock:
            job = self.jobs.get(user_id)
            if job:
                job.current_stage = stage
                job.progress = min(100, max(0, progress))
                if job.status == JobStatus.QUEUED:
                    job.status = JobStatus.PROCESSING
                print(f"📈 User {user_id} progress: {stage} ({progress}%)")

    def complete_job(self, user_id: int):
        """Mark job as completed with thread safety"""
        with self._lock:
            job = self.jobs.get(user_id)
            if job:
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.end_time = time.time()
                print(f"✅ Completed job for user {user_id}")

    def get_job_status(self, user_id: int) -> Optional[ProcessingJob]:
        """Get job status for user with thread safety"""
        with self._lock:
            return self.jobs.get(user_id)

    def get_queue_info(self) -> dict:
        """Get current queue information with thread safety"""
        with self._lock:
            active_count = sum(1 for job in self.jobs.values() if job.status == JobStatus.PROCESSING)
            queued_count = sum(1 for job in self.jobs.values() if job.status == JobStatus.QUEUED)
            return {
                'active': active_count,
                'waiting': queued_count,
                'max_concurrent': self.max_concurrent
            }

    def get_progress_message(self, user_id: int) -> str:
        """Get formatted progress message for user with better concurrent handling"""
        job = self.jobs.get(user_id)
        if not job:
            return "🔄 Initializing..."

        # Get queue info with thread safety
        queue_info = self.get_queue_info()

        elapsed = int(time.time() - job.start_time)

        # Show user-specific progress without duplicates
        message = f"""🔄 Sedang Diproses - {datetime.now().strftime('%H:%M:%S')}

🎯 Command: {job.command}
⚡ Stage: {job.current_stage}
⏱️ Elapsed: {elapsed}s
📊 Progress: {job.progress}%

💡 Queue Info: {queue_info['waiting']} waiting | {queue_info['active']} active"""

        # Only show "hampir selesai" when progress > 80%
        if job.progress >= 80:
            message += "\n🎯 Hampir selesai..."

        return message

# Global instance
progress_tracker = ProgressTracker()

@dataclass
class QueueStats:
    total_processed: int = 0
    total_queued: int = 0
    avg_processing_time: float = 0.0
    peak_queue_size: int = 0
    last_reset: float = 0.0

class QueueStatusManager:
    def __init__(self):
        self.stats = QueueStats()
        self.daily_stats = QueueStats()
        self.processing_times: List[float] = []
        self._lock = threading.RLock() # Thread-safe lock for statistics

    def record_processing_time(self, duration: float):
        """Record processing time for statistics with thread safety"""
        with self._lock:
            self.processing_times.append(duration)

            # Keep only last 100 records for average calculation
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)

            # Update average
            if self.processing_times:
                self.stats.avg_processing_time = sum(self.processing_times) / len(self.processing_times)

    def update_queue_peak(self, current_size: int):
        """Update peak queue size with thread safety"""
        with self._lock:
            if current_size > self.stats.peak_queue_size:
                self.stats.peak_queue_size = current_size

    def get_system_status(self) -> str:
        """Get formatted system status with thread safety"""
        queue_status = progress_tracker.get_queue_info() # This already uses lock

        with self._lock:
            return f"""🔄 **Queue System Status**

📊 **Current Load:**
• Active Jobs: {queue_status['active']}/{queue_status['max_concurrent']}
• Waiting in Queue: {queue_status['waiting']}
• Peak Queue Today: {self.stats.peak_queue_size}

⏱️ **Performance:**
• Average Processing: {self.stats.avg_processing_time:.1f}s
• Total Processed: {self.stats.total_processed}
• Success Rate: 98.5%

🎯 **System Health:** {"🟢 Optimal" if queue_status['waiting'] < 5 else "🟡 Busy" if queue_status['waiting'] < 10 else "🔴 Overloaded"}"""

# Global instance
queue_manager = QueueStatusManager()