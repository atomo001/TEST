from __future__ import annotations

import re
from pathlib import Path

from recovery_app.models.types import RecoveryFile, ScanResult

_PROGRESS_RE = re.compile(r"Pass\s+\d+\s+-\s+(\d+)%")
_FOUND_RE = re.compile(r"Recovered:\s+(.+?)\s+\((\d+) bytes\)")


def parse_progress(line: str) -> float | None:
    match = _PROGRESS_RE.search(line)
    if not match:
        return None
    return min(100.0, max(0.0, float(match.group(1))))


def parse_recovered_files(output: str) -> ScanResult:
    files: list[RecoveryFile] = []
    for line in output.splitlines():
        match = _FOUND_RE.search(line)
        if not match:
            continue
        full_path = match.group(1).strip()
        size = int(match.group(2))
        name = Path(full_path).name
        ext = Path(full_path).suffix.lstrip(".").lower()
        files.append(RecoveryFile(path=full_path, name=name, ext=ext, size=size))

    summary = {
        "file_count": len(files),
        "by_extension": _count_by_extension(files),
    }
    return ScanResult(files=files, summary=summary)


def _count_by_extension(files: list[RecoveryFile]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in files:
        key = item.ext or "unknown"
        counts[key] = counts.get(key, 0) + 1
    return counts
