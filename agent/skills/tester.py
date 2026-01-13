"""Tester skill - test detection, running, generation."""
import subprocess
from pathlib import Path
from ..claude_bridge import run_claude
from .. import knowledge

class TesterSkill:
    """Test detection, running, and generation."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self._test_framework = None

    @property
    def test_framework(self) -> str:
        """Get detected test framework."""
        if self._test_framework is None:
            summary = knowledge.get_project_summary(self.project_path)
            self._test_framework = summary.get("test_framework", "")
        return self._test_framework

    def execute(self, task: dict) -> dict:
        """Execute test task."""
        if "generate" in task.get("title", "").lower():
            return self.generate_tests(task.get("description", ""))
        else:
            return self.run_tests()

    def run_tests(self, specific_test: str = None) -> dict:
        """Run tests using detected framework."""
        framework = self.test_framework

        if not framework:
            return {"success": False, "error": "No test framework detected"}

        cmd = self._get_test_command(framework, specific_test)
        if not cmd:
            return {"success": False, "error": f"Unknown framework: {framework}"}

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Test timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_test_command(self, framework: str, specific: str = None) -> list:
        """Get test command for framework."""
        commands = {
            "pytest": ["pytest", "-v"],
            "jest": ["npm", "test"],
            "mocha": ["npm", "test"],
            "vitest": ["npm", "test"],
            "go-test": ["go", "test", "./..."],
            "cargo-test": ["cargo", "test"],
        }
        cmd = commands.get(framework)
        if cmd and specific:
            cmd = cmd + [specific]
        return cmd

    def generate_tests(self, description: str) -> dict:
        """Generate tests using Claude."""
        framework = self.test_framework or "appropriate"

        prompt = f"""Generate tests for: {description}

Use {framework} test framework.
Follow existing test patterns in the project.
Create comprehensive but focused tests."""

        return run_claude(prompt, self.project_path)

    def check_coverage(self) -> dict:
        """Check test coverage (if available)."""
        framework = self.test_framework

        if framework == "pytest":
            cmd = ["pytest", "--cov", "--cov-report=term-missing"]
        elif framework in ("jest", "vitest"):
            cmd = ["npm", "test", "--", "--coverage"]
        else:
            return {"success": False, "error": "Coverage not supported"}

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            return {"success": True, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
