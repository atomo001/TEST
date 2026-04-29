from recovery_app.core.command_runner import CommandRunner
from recovery_app.models.types import ScanResult
from recovery_app.services.task_manager import TaskManager


def test_command_runner_success():
    runner = CommandRunner()
    result = runner.run(["python", "-c", "print('ok')"], timeout_sec=5)
    assert result.returncode == 0
    assert "ok" in result.stdout


def test_task_manager_lifecycle():
    manager = TaskManager()
    task = manager.create("init")
    manager.update_progress(task.id, 10, "running")
    manager.finish(task.id, ScanResult())
    loaded = manager.get(task.id)
    assert loaded.progress == 100
    assert loaded.status.value == "completed"
