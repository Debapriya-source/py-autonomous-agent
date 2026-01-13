"""Claude Code skills/plugins configuration."""
import json
from pathlib import Path

from . import db

# Known Claude Code skills
KNOWN_SKILLS = {
    "feature-dev": {
        "description": "Guided feature development with codebase understanding",
        "use_for": ["feature", "implement", "add", "create", "build"],
    },
    "agent-sdk-dev:new-sdk-app": {
        "description": "Create new Claude Agent SDK application",
        "use_for": ["agent", "sdk", "new-agent"],
    },
}

def get_skills_config_path(project_path: Path = None) -> Path:
    """Get skills config path."""
    return db.get_agent_dir(project_path) / "skills.json"

def init_skills_config(project_path: Path = None):
    """Initialize skills config."""
    path = get_skills_config_path(project_path)
    if not path.exists():
        default = {
            "enabled_skills": ["feature-dev"],
            "auto_select": True,
            "custom_skills": {}
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(default, indent=2))

def get_skills_config(project_path: Path = None) -> dict:
    """Get skills configuration."""
    path = get_skills_config_path(project_path)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {"enabled_skills": [], "auto_select": True, "custom_skills": {}}

def save_skills_config(config: dict, project_path: Path = None):
    """Save skills configuration."""
    path = get_skills_config_path(project_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2))

def enable_skill(skill_name: str, project_path: Path = None):
    """Enable a skill."""
    config = get_skills_config(project_path)
    if skill_name not in config.get("enabled_skills", []):
        config.setdefault("enabled_skills", []).append(skill_name)
        save_skills_config(config, project_path)

def disable_skill(skill_name: str, project_path: Path = None):
    """Disable a skill."""
    config = get_skills_config(project_path)
    if skill_name in config.get("enabled_skills", []):
        config["enabled_skills"].remove(skill_name)
        save_skills_config(config, project_path)

def list_skills(project_path: Path = None) -> dict:
    """List all skills with status."""
    config = get_skills_config(project_path)
    enabled = set(config.get("enabled_skills", []))

    result = {}
    for name, info in KNOWN_SKILLS.items():
        result[name] = {
            "description": info["description"],
            "enabled": name in enabled,
            "source": "builtin"
        }

    # Add custom skills
    for name, info in config.get("custom_skills", {}).items():
        result[name] = {
            "description": info.get("description", "Custom skill"),
            "enabled": name in enabled,
            "source": "custom"
        }

    return result

def select_skill_for_task(task_title: str, project_path: Path = None) -> str | None:
    """Auto-select appropriate skill for task."""
    config = get_skills_config(project_path)

    if not config.get("auto_select", True):
        return None

    enabled = set(config.get("enabled_skills", []))
    title_lower = task_title.lower()

    for skill_name, info in KNOWN_SKILLS.items():
        if skill_name not in enabled:
            continue
        for keyword in info.get("use_for", []):
            if keyword in title_lower:
                return skill_name

    return None

def add_custom_skill(name: str, description: str, keywords: list = None,
                     project_path: Path = None):
    """Add custom skill."""
    config = get_skills_config(project_path)
    config.setdefault("custom_skills", {})[name] = {
        "description": description,
        "use_for": keywords or []
    }
    save_skills_config(config, project_path)
