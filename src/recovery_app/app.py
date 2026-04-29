from __future__ import annotations

import threading
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from recovery_app.core.command_runner import CommandError
from recovery_app.models.types import RecoveryRequest, RiskAction, ScanRequest
from recovery_app.parsers.photorec_parser import parse_progress, parse_recovered_files
from recovery_app.services.task_manager import TaskManager
from recovery_app.services.testdisk_adapter import TestDiskAdapter

app = FastAPI(title="Recovery Assistant MVP")
base_dir = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=base_dir / "ui" / "static"), name="static")
templates = Jinja2Templates(directory=str(base_dir / "ui" / "templates"))

manager = TaskManager()
adapter = TestDiskAdapter()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/disks")
def list_disks():
    disks = adapter.list_disks()
    return {"items": disks}


@app.post("/api/scan")
def start_scan(req: ScanRequest):
    task = manager.create(message="scan queued")
    threading.Thread(target=_run_scan, args=(task.id, req), daemon=True).start()
    return {"task_id": task.id}


@app.get("/api/task/{task_id}")
def task_detail(task_id: str):
    try:
        return manager.get(task_id)
    except KeyError as exc:
        raise HTTPException(404, "task not found") from exc


@app.post("/api/recover")
def recover(req: RecoveryRequest):
    if not req.output_dir:
        raise HTTPException(400, "output_dir required")
    overwrite_risk = adapter.requires_confirmation(RiskAction.OVERWRITE_FILE)
    return {"accepted": True, "need_confirmation": overwrite_risk, "request": req}


def _run_scan(task_id: str, req: ScanRequest) -> None:
    scan_dir = Path("./artifacts") / task_id
    scan_dir.mkdir(parents=True, exist_ok=True)
    cmd = adapter.start_scan(req, scan_dir)
    manager.append_log(task_id, f"CMD: {' '.join(cmd)}")

    try:
        for pct in range(0, 101, 10):
            line = f"Pass 1 - {pct}%"
            progress = parse_progress(line) or float(pct)
            manager.update_progress(task_id, progress, message="scanning")
            manager.append_log(task_id, line)
            time.sleep(0.1)

        sample_output = "\n".join(
            [
                "Recovered: /recup_dir.1/f000001.jpg (23552 bytes)",
                "Recovered: /recup_dir.1/f000002.pdf (88200 bytes)",
                "Recovered: /recup_dir.1/f000003.mp4 (123456 bytes)",
            ]
        )
        result = parse_recovered_files(sample_output)
        manager.finish(task_id, result)
        manager.append_log(task_id, "Scan completed")
    except CommandError as exc:
        manager.fail(task_id, str(exc))
