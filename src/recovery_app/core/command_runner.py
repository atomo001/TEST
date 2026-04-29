from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass


class CommandError(RuntimeError):
    pass


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    duration: float


class CommandRunner:
    def run(self, cmd: list[str], timeout_sec: int = 600) -> CommandResult:
        start = time.time()
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise CommandError(f"Command timeout after {timeout_sec}s: {' '.join(cmd)}") from exc
        except OSError as exc:
            raise CommandError(f"Failed to execute command: {' '.join(cmd)}") from exc

        duration = time.time() - start
        return CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration=duration,
        )
