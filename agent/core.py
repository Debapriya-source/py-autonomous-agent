"""Core agent orchestration."""
from pathlib import Path

from . import db, knowledge, mcp, skills_config, tech_stack
from .claude_bridge import check_claude_available
from .subagents import ExecutorAgent, PlannerAgent, ReviewerAgent


class Agent:
    """Main agent orchestrator."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.planner = PlannerAgent(project_path)
        self.executor = ExecutorAgent(project_path)
        self.reviewer = ReviewerAgent(project_path)

    def init(self) -> dict:
        """Initialize agent in project."""
        # Check Claude CLI
        if not check_claude_available():
            return {
                "success": False,
                "error": "Claude CLI not found. Install with: npm install -g @anthropic/claude-code"
            }

        # Scan and store knowledge
        result = knowledge.init_project(self.project_path)

        # Init MCP config
        mcp.init_mcp_config(self.project_path)

        # Configure default MCP servers (playwright, claude-code-sdk)
        default_result = tech_stack.configure_defaults(self.project_path)

        # Init skills config
        skills_config.init_skills_config(self.project_path)

        # Count inherited MCP servers and enabled skills
        mcp_servers = mcp.list_mcp_servers(self.project_path)
        skills = skills_config.list_skills(self.project_path)
        enabled_skills = [s for s, info in skills.items() if info["enabled"]]

        return {
            "success": True,
            "languages": result.get("languages", []),
            "frameworks": result.get("frameworks", []),
            "test_framework": result.get("test_framework"),
            "file_count": len(result.get("files", [])),
            "has_git": result.get("has_git", False),
            "mcp_servers": len(mcp_servers),
            "default_servers": default_result.get("servers_added", []),
            "skills": enabled_skills
        }

    def plan(self, file_path: str = None, interactive: bool = False) -> dict:
        """Create or load a plan."""
        if interactive:
            return self.planner.create_interactive_plan()
        elif file_path:
            return self.planner.parse_plan_file(file_path)
        else:
            return {"success": False, "error": "Provide file path or use --interactive"}

    def run(self, task_id: int = None, all_tasks: bool = False) -> dict:
        """Execute tasks."""
        if task_id:
            return self.executor.execute_task(task_id)
        elif all_tasks:
            return self.executor.execute_all()
        else:
            return self.executor.execute_next()

    def status(self) -> dict:
        """Get current status."""
        plans = db.get_plans(project_path=self.project_path)
        tasks = db.get_tasks(project_path=self.project_path)

        pending = [t for t in tasks if t["status"] == "pending"]
        in_progress = [t for t in tasks if t["status"] == "in_progress"]
        completed = [t for t in tasks if t["status"] == "completed"]
        failed = [t for t in tasks if t["status"] == "failed"]

        return {
            "plans": len(plans),
            "tasks": {
                "total": len(tasks),
                "pending": len(pending),
                "in_progress": len(in_progress),
                "completed": len(completed),
                "failed": len(failed)
            },
            "pending_tasks": pending,
            "failed_tasks": failed
        }

    def reset(self) -> dict:
        """Reset all tasks and plans."""
        db.reset_tasks(self.project_path)
        return {"success": True, "message": "All tasks and plans cleared"}

    def knowledge_summary(self) -> dict:
        """Get knowledge base summary."""
        return knowledge.get_project_summary(self.project_path)

    def validate(self) -> dict:
        """Run full validation."""
        return self.reviewer.full_validation()
