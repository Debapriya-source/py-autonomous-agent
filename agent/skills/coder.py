"""Coder skill - code generation via Claude."""
from pathlib import Path

from .. import skills_config
from ..claude_bridge import run_claude


class CoderSkill:
    """Generate/modify code using Claude."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()

    def execute(self, task: dict) -> dict:
        """Execute coding task."""
        title = task.get("title", "")
        description = task.get("description", "")

        # Auto-select skill based on task
        skill = skills_config.select_skill_for_task(title, self.project_path)

        prompt = f"""Task: {title}

Details: {description}

Instructions:
- Implement the requested changes
- Follow existing code patterns
- Keep changes minimal and focused
"""

        result = run_claude(prompt, self.project_path, skill=skill)

        if result["success"]:
            return {
                "success": True,
                "output": result.get("output", ""),
                "message": f"Completed: {title}",
                "skill_used": skill
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "message": f"Failed: {title}"
            }

    def generate_code(self, description: str, target_file: str = None,
                      skill: str = None) -> dict:
        """Generate code based on description."""
        prompt = f"Generate code: {description}"
        if target_file:
            prompt += f"\nTarget file: {target_file}"

        # Auto-select skill if not specified
        if not skill:
            skill = skills_config.select_skill_for_task(description, self.project_path)

        return run_claude(prompt, self.project_path, skill=skill)

    def modify_code(self, file_path: str, changes: str, skill: str = None) -> dict:
        """Modify existing code."""
        prompt = f"""Modify file: {file_path}

Changes needed:
{changes}

Apply changes carefully, maintaining existing style."""

        return run_claude(prompt, self.project_path, skill=skill)
