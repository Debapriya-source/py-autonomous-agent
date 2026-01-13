"""Shipper skill - git operations with user prompts."""
import subprocess
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

class ShipperSkill:
    """Git operations - always prompts user."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()

    def execute(self, task: dict) -> dict:
        """Execute ship task - interactive."""
        return self.interactive_ship()

    def interactive_ship(self) -> dict:
        """Interactive shipping flow."""
        # Check git status
        status = self.git_status()
        if not status["success"]:
            return status

        if not status["has_changes"]:
            console.print("[yellow]No changes to commit[/yellow]")
            return {"success": True, "message": "Nothing to commit"}

        # Show status
        console.print("\n[bold]Current git status:[/bold]")
        console.print(status["output"])

        # Ask what to do
        action = Prompt.ask(
            "\nWhat would you like to do?",
            choices=["commit", "commit-push", "skip"],
            default="commit"
        )

        if action == "skip":
            return {"success": True, "message": "Skipped"}

        # Get commit message
        message = Prompt.ask("Commit message")
        if not message:
            return {"success": False, "error": "No commit message"}

        # Stage and commit
        stage_result = self.git_add()
        if not stage_result["success"]:
            return stage_result

        commit_result = self.git_commit(message)
        if not commit_result["success"]:
            return commit_result

        console.print(f"[green]Committed: {message}[/green]")

        # Push if requested
        if action == "commit-push":
            if Confirm.ask("Push to remote?", default=True):
                push_result = self.git_push()
                if push_result["success"]:
                    console.print("[green]Pushed to remote[/green]")
                return push_result

        return {"success": True, "message": f"Committed: {message}"}

    def git_status(self) -> dict:
        """Get git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            output = result.stdout.strip()
            return {
                "success": True,
                "output": output,
                "has_changes": bool(output)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def git_add(self, files: list = None) -> dict:
        """Stage files."""
        cmd = ["git", "add"] + (files or ["."])
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            return {"success": result.returncode == 0, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def git_commit(self, message: str) -> dict:
        """Commit staged changes."""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def git_push(self, remote: str = "origin", branch: str = None) -> dict:
        """Push to remote."""
        cmd = ["git", "push", remote]
        if branch:
            cmd.append(branch)

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_pr(self, title: str, body: str = "") -> dict:
        """Create PR using gh CLI."""
        try:
            result = subprocess.run(
                ["gh", "pr", "create", "--title", title, "--body", body],
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except FileNotFoundError:
            return {"success": False, "error": "gh CLI not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
