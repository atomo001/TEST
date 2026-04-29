from __future__ import annotations

import threading
import uuid
from datetime import datetime

from recovery_app.models.types import ScanResult, TaskState, TaskStatus


class TaskManager:
    def __init__(self):
        self._tasks: dict[str, TaskState] = {}
        self._lock = threading.Lock()

    def create(self, message: str = "") -> TaskState:
        task = TaskState(id=str(uuid.uuid4()), status=TaskStatus.PENDING, message=message)
        with self._lock:
            self._tasks[task.id] = task
        return task

    def update_progress(self, task_id: str, progress: float, message: str = "") -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            task.progress = progress
            task.message = message or task.message
            task.status = TaskStatus.RUNNING if progress < 100 else TaskStatus.COMPLETED
            task.updated_at = datetime.utcnow()
            return task

    def append_log(self, task_id: str, line: str) -> None:
        with self._lock:
            task = self._tasks[task_id]
            task.logs.append(line)
            task.updated_at = datetime.utcnow()

    def finish(self, task_id: str, result: ScanResult) -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.updated_at = datetime.utcnow()
            return task

    def fail(self, task_id: str, reason: str) -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            task.status = TaskStatus.FAILED
            task.message = reason
            task.updated_at = datetime.utcnow()
            return task

    def get(self, task_id: str) -> TaskState:
        return self._tasks[task_id]
