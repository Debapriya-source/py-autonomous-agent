"""Executor agent - run tasks using skills."""
from pathlib import Path

from .. import db
from ..skills import CoderSkill, ShipperSkill, TesterSkill


class ExecutorAgent:
    """Execute tasks using appropriate skills."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.skills = {
            "code": CoderSkill(project_path),
            "test": TesterSkill(project_path),
            "ship": ShipperSkill(project_path),
        }

    def execute_next(self) -> dict:
        """Execute next pending task."""
        task = db.get_next_task(self.project_path)
        if not task:
            return {"success": True, "message": "No pending tasks"}

        return self.execute_task(task["id"])

    def execute_task(self, task_id: int) -> dict:
        """Execute specific task."""
        tasks = db.get_tasks(project_path=self.project_path)
        task = next((t for t in tasks if t["id"] == task_id), None)

        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}

        if task["status"] == "completed":
            return {"success": True, "message": "Task already completed"}

        # Mark in progress
        db.update_task(task_id, status="in_progress", project_path=self.project_path)

        # Get skill
        task_type = task.get("task_type", "code")
        skill = self.skills.get(task_type)

        if not skill:
            db.update_task(task_id, status="failed", result="Unknown task type",
                          project_path=self.project_path)
            return {"success": False, "error": f"Unknown task type: {task_type}"}

        # Execute
        try:
            result = skill.execute(task)

            # Log execution
            db.log_execution(
                task_id=task_id,
                agent_type=task_type,
                input_data=task.get("description", ""),
                output=str(result.get("output", result.get("message", ""))),
                success=result.get("success", False),
                project_path=self.project_path
            )

            # Update task
            if result.get("success"):
                db.update_task(task_id, status="completed",
                              result=str(result.get("output", "")),
                              project_path=self.project_path)
            else:
                db.update_task(task_id, status="failed",
                              result=result.get("error", "Failed"),
                              project_path=self.project_path)

            return result

        except Exception as e:
            db.update_task(task_id, status="failed", result=str(e),
                          project_path=self.project_path)
            return {"success": False, "error": str(e)}

    def execute_all(self, stop_on_error: bool = True) -> dict:
        """Execute all pending tasks."""
        results = []
        while True:
            task = db.get_next_task(self.project_path)
            if not task:
                break

            result = self.execute_task(task["id"])
            results.append({"task_id": task["id"], "title": task["title"], **result})

            if not result.get("success") and stop_on_error:
                break

        return {
            "success": all(r.get("success") for r in results),
            "tasks_executed": len(results),
            "results": results
        }

    def retry_failed(self) -> dict:
        """Retry failed tasks."""
        failed = db.get_tasks(status="failed", project_path=self.project_path)
        if not failed:
            return {"success": True, "message": "No failed tasks"}

        # Reset to pending
        for task in failed:
            db.update_task(task["id"], status="pending", project_path=self.project_path)

        return self.execute_all()
