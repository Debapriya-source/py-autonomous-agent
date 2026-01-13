"""Planner agent - parse plans into tasks."""
import re
from pathlib import Path

from .. import db
from ..claude_bridge import run_claude


class PlannerAgent:
    """Parse markdown plans into executable tasks."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()

    def parse_plan_file(self, file_path: str) -> dict:
        """Parse plan from markdown file."""
        path = Path(file_path)
        if not path.exists():
            # Check in .agent/plans
            alt_path = db.get_agent_dir(self.project_path) / "plans" / file_path
            if alt_path.exists():
                path = alt_path
            else:
                return {"success": False, "error": f"File not found: {file_path}"}

        content = path.read_text()
        return self.parse_plan(content, str(path))

    def parse_plan(self, content: str, source: str = None) -> dict:
        """Parse plan content into tasks."""
        # Extract title (first h1)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled Plan"

        # Create plan record
        plan_id = db.create_plan(title, content, source, self.project_path)

        # Parse tasks from content
        tasks = self._extract_tasks(content)

        # Create task records
        task_ids = []
        for i, task in enumerate(tasks):
            task_id = db.create_task(
                plan_id=plan_id,
                title=task["title"],
                description=task.get("description", ""),
                task_type=task.get("type", "code"),
                priority=len(tasks) - i,  # Higher priority for earlier tasks
                project_path=self.project_path
            )
            task_ids.append(task_id)

        return {
            "success": True,
            "plan_id": plan_id,
            "title": title,
            "task_count": len(task_ids),
            "task_ids": task_ids
        }

    def _extract_tasks(self, content: str) -> list:
        """Extract tasks from plan content."""
        tasks = []

        # Look for task patterns:
        # - [ ] Task description
        # - Task description
        # 1. Task description
        # ## Task: description

        # Checkbox tasks
        for match in re.finditer(r'^[-*]\s*\[[ x]\]\s*(.+)$', content, re.MULTILINE):
            tasks.append(self._classify_task(match.group(1)))

        # If no checkboxes, try numbered list
        if not tasks:
            for match in re.finditer(r'^\d+\.\s+(.+)$', content, re.MULTILINE):
                tasks.append(self._classify_task(match.group(1)))

        # If still nothing, try bullet points under "Tasks" or "Steps"
        if not tasks:
            section_match = re.search(
                r'(?:^##?\s*(?:Tasks|Steps|TODO|Plan)\s*\n)((?:[-*]\s+.+\n?)+)',
                content, re.MULTILINE | re.IGNORECASE
            )
            if section_match:
                for match in re.finditer(r'^[-*]\s+(.+)$', section_match.group(1), re.MULTILINE):
                    tasks.append(self._classify_task(match.group(1)))

        # Fallback: use Claude to extract tasks
        if not tasks:
            tasks = self._ai_extract_tasks(content)

        return tasks

    def _classify_task(self, text: str) -> dict:
        """Classify task type from text."""
        text_lower = text.lower()

        task_type = "code"
        if any(kw in text_lower for kw in ["test", "spec", "verify"]):
            task_type = "test"
        elif any(kw in text_lower for kw in ["commit", "push", "ship", "deploy", "release"]):
            task_type = "ship"

        return {"title": text.strip(), "type": task_type}

    def _ai_extract_tasks(self, content: str) -> list:
        """Use Claude to extract tasks from free-form plan."""
        prompt = f"""Extract actionable tasks from this plan. Return as JSON array.
Each task: {{"title": "...", "type": "code|test|ship"}}

Plan:
{content}

Return only valid JSON array, no other text."""

        result = run_claude(prompt, self.project_path)
        if result["success"]:
            try:
                import json
                output = result["output"]
                if isinstance(output, str):
                    # Find JSON in output
                    match = re.search(r'\[.*\]', output, re.DOTALL)
                    if match:
                        return json.loads(match.group())
                elif isinstance(output, list):
                    return output
            except Exception:
                pass
        return []

    def create_interactive_plan(self) -> dict:
        """Create plan interactively."""
        from rich.console import Console
        from rich.prompt import Prompt

        console = Console()
        console.print("\n[bold]Create New Plan[/bold]\n")

        title = Prompt.ask("Plan title")
        description = Prompt.ask("Description (what do you want to build?)")

        tasks = []
        console.print("\nEnter tasks (empty to finish):")
        while True:
            task = Prompt.ask(f"Task {len(tasks) + 1}", default="")
            if not task:
                break
            tasks.append(self._classify_task(task))

        if not tasks:
            return {"success": False, "error": "No tasks entered"}

        # Create plan
        plan_id = db.create_plan(title, description, None, self.project_path)

        for i, task in enumerate(tasks):
            db.create_task(
                plan_id=plan_id,
                title=task["title"],
                description="",
                task_type=task["type"],
                priority=len(tasks) - i,
                project_path=self.project_path
            )

        return {
            "success": True,
            "plan_id": plan_id,
            "title": title,
            "task_count": len(tasks)
        }
