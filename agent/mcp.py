"""MCP config management."""
import json
import tempfile
from pathlib import Path

from . import db


def get_claude_config_paths() -> list[Path]:
    """Get Claude config paths in priority order (highest first)."""
    paths = []

    # Global config
    home = Path.home()
    global_config = home / ".claude" / "settings.json"
    if global_config.exists():
        paths.append(global_config)

    return paths

def get_project_claude_config(project_path: Path = None) -> Path | None:
    """Get project-level Claude config."""
    root = project_path or Path.cwd()
    project_config = root / ".claude" / "settings.json"
    if project_config.exists():
        return project_config
    return None

def get_agent_mcp_path(project_path: Path = None) -> Path:
    """Get agent MCP config path."""
    return db.get_agent_dir(project_path) / "mcp.json"

def load_mcp_config(path: Path) -> dict:
    """Load MCP servers from config file."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return data.get("mcpServers", {})
    except (json.JSONDecodeError, KeyError):
        return {}

def get_merged_mcp_config(project_path: Path = None) -> dict:
    """Get merged MCP config from all sources.

    Priority: agent > project > global
    """
    merged = {}

    # Load global config (lowest priority)
    for global_path in get_claude_config_paths():
        servers = load_mcp_config(global_path)
        merged.update(servers)

    # Load project Claude config
    project_config = get_project_claude_config(project_path)
    if project_config:
        servers = load_mcp_config(project_config)
        merged.update(servers)

    # Load agent config (highest priority)
    agent_path = get_agent_mcp_path(project_path)
    servers = load_mcp_config(agent_path)
    merged.update(servers)

    return merged

def init_mcp_config(project_path: Path = None):
    """Initialize empty MCP config if not exists."""
    path = get_agent_mcp_path(project_path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"mcpServers": {}}, indent=2))

def add_mcp_server(name: str, command: str, args: list = None,
                   env: dict = None, project_path: Path = None):
    """Add MCP server to agent config."""
    path = get_agent_mcp_path(project_path)

    # Load existing
    if path.exists():
        data = json.loads(path.read_text())
    else:
        data = {"mcpServers": {}}

    # Add server
    server_config = {"command": command}
    if args:
        server_config["args"] = args
    if env:
        server_config["env"] = env

    data["mcpServers"][name] = server_config

    # Save
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))

def remove_mcp_server(name: str, project_path: Path = None) -> bool:
    """Remove MCP server from agent config."""
    path = get_agent_mcp_path(project_path)

    if not path.exists():
        return False

    data = json.loads(path.read_text())
    if name in data.get("mcpServers", {}):
        del data["mcpServers"][name]
        path.write_text(json.dumps(data, indent=2))
        return True
    return False

def list_mcp_servers(project_path: Path = None) -> dict:
    """List all MCP servers with source info."""
    result = {}

    # Track sources
    sources = {}

    # Global
    for global_path in get_claude_config_paths():
        for name in load_mcp_config(global_path):
            sources[name] = "global"

    # Project
    project_config = get_project_claude_config(project_path)
    if project_config:
        for name in load_mcp_config(project_config):
            sources[name] = "project"

    # Agent
    agent_path = get_agent_mcp_path(project_path)
    for name in load_mcp_config(agent_path):
        sources[name] = "agent"

    # Build result with merged config
    merged = get_merged_mcp_config(project_path)
    for name, config in merged.items():
        result[name] = {
            "config": config,
            "source": sources.get(name, "unknown")
        }

    return result

def write_merged_config_temp(project_path: Path = None) -> Path:
    """Write merged MCP config to temp file for Claude CLI."""
    merged = get_merged_mcp_config(project_path)

    # Create temp file
    fd, temp_path = tempfile.mkstemp(suffix=".json", prefix="agent_mcp_")
    with open(fd, 'w') as f:
        json.dump({"mcpServers": merged}, f)

    return Path(temp_path)

def parse_package_to_command(package: str) -> tuple[str, list]:
    """Parse npm package to command and args.

    Examples:
        @anthropic/mcp-server-filesystem -> npx, [-y, @anthropic/mcp-server-filesystem]
        python -m mcp_server -> python, [-m, mcp_server]
    """
    if package.startswith("@") or "/" not in package.split()[0]:
        # NPM package
        return "npx", ["-y", package]
    else:
        # Assume direct command
        parts = package.split()
        return parts[0], parts[1:] if len(parts) > 1 else []
