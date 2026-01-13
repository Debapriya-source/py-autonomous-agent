"""Coder skill - code generation via Claude."""
from pathlib import Path
from ..claude_bridge import run_claude

class CoderSkill:
    """Generate/modify code using Claude."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()

    def execute(self, task: dict) -> dict:
        """Execute coding task."""
        title = task.get("title", "")
        description = task.get("description", "")

        prompt = f"""Task: {title}

Details: {description}

Instructions:
- Implement the requested changes
- Follow existing code patterns
- Keep changes minimal and focused
"""

        result = run_claude(prompt, self.project_path)

        if result["success"]:
            return {
                "success": True,
                "output": result.get("output", ""),
                "message": f"Completed: {title}"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "message": f"Failed: {title}"
            }

    def generate_code(self, description: str, target_file: str = None) -> dict:
        """Generate code based on description."""
        prompt = f"Generate code: {description}"
        if target_file:
            prompt += f"\nTarget file: {target_file}"

        return run_claude(prompt, self.project_path)

    def modify_code(self, file_path: str, changes: str) -> dict:
        """Modify existing code."""
        prompt = f"""Modify file: {file_path}

Changes needed:
{changes}

Apply changes carefully, maintaining existing style."""

        return run_claude(prompt, self.project_path)
