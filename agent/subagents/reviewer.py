"""Reviewer agent - validate changes."""
from pathlib import Path

from ..claude_bridge import run_claude
from ..skills import TesterSkill


class ReviewerAgent:
    """Review and validate code changes."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.tester = TesterSkill(project_path)

    def review_changes(self) -> dict:
        """Review recent changes."""
        # Get git diff
        import subprocess
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD~1"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            diff = result.stdout
        except Exception:
            diff = ""

        if not diff:
            return {"success": True, "message": "No changes to review"}

        # Ask Claude to review
        prompt = f"""Review this code diff for issues:

{diff[:5000]}

Check for:
- Bugs or logic errors
- Security issues
- Code style problems
- Missing error handling

Provide brief feedback."""

        result = run_claude(prompt, self.project_path)
        return {
            "success": True,
            "review": result.get("output", "Review complete"),
            "diff_lines": len(diff.split('\n'))
        }

    def validate_task(self, task_id: int) -> dict:
        """Validate task completion."""
        from .. import db

        tasks = db.get_tasks(project_path=self.project_path)
        task = next((t for t in tasks if t["id"] == task_id), None)

        if not task:
            return {"success": False, "error": "Task not found"}

        # Run tests if test task
        if task.get("task_type") == "test":
            return self.tester.run_tests()

        # For code tasks, run tests if available
        if self.tester.test_framework:
            test_result = self.tester.run_tests()
            if not test_result.get("success"):
                return {
                    "success": False,
                    "error": "Tests failed after code changes",
                    "test_output": test_result.get("output", "")
                }

        return {"success": True, "message": "Validation passed"}

    def full_validation(self) -> dict:
        """Run full project validation."""
        results = {
            "tests": None,
            "review": None,
            "success": True
        }

        # Run tests
        if self.tester.test_framework:
            test_result = self.tester.run_tests()
            results["tests"] = test_result
            if not test_result.get("success"):
                results["success"] = False

        # Review changes
        review_result = self.review_changes()
        results["review"] = review_result

        return results
