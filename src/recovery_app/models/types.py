from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskAction(str, Enum):
    READ_ONLY_SCAN = "read_only_scan"
    WRITE_PARTITION_TABLE = "write_partition_table"
    REPAIR_BOOT_SECTOR = "repair_boot_sector"
    OVERWRITE_FILE = "overwrite_file"


@dataclass
class ScanRequest:
    source: str
    mode: str = "partition"
    filesystem_hint: str | None = None


@dataclass
class RecoveryFile:
    path: str
    name: str
    ext: str
    size: int


@dataclass
class ScanResult:
    files: list[RecoveryFile] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryRequest:
    task_id: str
    output_dir: str
    file_types: list[str] = field(default_factory=list)
    selected_files: list[str] = field(default_factory=list)
    allow_overwrite: bool = False


@dataclass
class TaskState:
    id: str
    status: TaskStatus
    progress: float = 0
    message: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    logs: list[str] = field(default_factory=list)
    result: ScanResult | None = None
