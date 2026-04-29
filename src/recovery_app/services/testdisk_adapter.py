from __future__ import annotations

from pathlib import Path

from recovery_app.core.command_runner import CommandRunner
from recovery_app.models.types import RecoveryRequest, RiskAction, ScanRequest


class TestDiskAdapter:
    def __init__(self, runner: CommandRunner | None = None):
        self.runner = runner or CommandRunner()

    def list_disks(self) -> list[str]:
        result = self.runner.run(["testdisk", "/list"], timeout_sec=90)
        if result.returncode != 0:
            return []
        disks = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("Disk "):
                disks.append(line)
        return disks

    def start_scan(self, req: ScanRequest, output_dir: Path) -> list[str]:
        # PhotoRec read-only style command generation
        cmd = [
            "photorec",
            "/log",
            "/d",
            str(output_dir),
            "/cmd",
            req.source,
            "search",
        ]
        return cmd

    def start_recovery(self, req: RecoveryRequest, recovered_root: Path) -> list[str]:
        cmd = ["photorec", "/log", "/d", str(recovered_root), "/cmd", req.task_id, "recover"]
        return cmd

    @staticmethod
    def requires_confirmation(action: RiskAction) -> bool:
        return action in {
            RiskAction.WRITE_PARTITION_TABLE,
            RiskAction.REPAIR_BOOT_SECTOR,
            RiskAction.OVERWRITE_FILE,
        }
