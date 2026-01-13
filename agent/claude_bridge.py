"""Claude Code CLI bridge."""
import json
import os
import subprocess
from pathlib import Path

from . import mcp


def run_claude(prompt: str, cwd: Path = None, timeout: int = 300,
               use_mcp: bool = True, skill: str = None) -> dict:
    """Run Claude Code CLI with prompt.

    Args:
        prompt: The prompt to send
        cwd: Working directory
        timeout: Timeout in seconds
        use_mcp: Whether to include MCP config
        skill: Optional skill/plugin to invoke (e.g., "feature-dev")
    """
    cwd = cwd or Path.cwd()
    temp_config = None

    try:
        # If skill specified, prepend skill invocation to prompt
        if skill:
            prompt = f"/{skill} {prompt}"

        cmd = ["claude", "-p", prompt, "--output-format", "json"]

        # Add MCP config if available
        if use_mcp:
            merged = mcp.get_merged_mcp_config(cwd)
            if merged:
                temp_config = mcp.write_merged_config_temp(cwd)
                cmd.extend(["--mcp-config", str(temp_config)])

        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            try:
                return {"success": True, "output": json.loads(result.stdout)}
            except json.JSONDecodeError:
                return {"success": True, "output": result.stdout}
        else:
            return {"success": False, "error": result.stderr or result.stdout}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout"}
    except FileNotFoundError:
        return {"success": False, "error": "Claude CLI not found. Install with: npm install -g @anthropic/claude-code"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        # Cleanup temp file
        if temp_config and temp_config.exists():
            try:
                os.unlink(temp_config)
            except Exception:
                pass

def run_claude_interactive(prompt: str, cwd: Path = None,
                           use_mcp: bool = True) -> dict:
    """Run Claude Code in interactive mode."""
    cwd = cwd or Path.cwd()
    temp_config = None

    try:
        cmd = ["claude", prompt]

        # Add MCP config if available
        if use_mcp:
            merged = mcp.get_merged_mcp_config(cwd)
            if merged:
                temp_config = mcp.write_merged_config_temp(cwd)
                cmd.extend(["--mcp-config", str(temp_config)])

        result = subprocess.run(cmd, cwd=str(cwd))
        return {"success": result.returncode == 0}
    except FileNotFoundError:
        return {"success": False, "error": "Claude CLI not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if temp_config and temp_config.exists():
            try:
                os.unlink(temp_config)
            except Exception:
                pass

def check_claude_available() -> bool:
    """Check if Claude CLI is available."""
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

def get_mcp_status(cwd: Path = None) -> dict:
    """Get MCP configuration status."""
    servers = mcp.list_mcp_servers(cwd)
    return {
        "server_count": len(servers),
        "servers": servers
    }
