"""Tech stack to MCP server mapping and configuration."""
import json
from pathlib import Path

from . import db, mcp

# Default MCP servers - always configured
DEFAULT_SERVERS = {
    "playwright": {
        "description": "Browser automation with Playwright",
        "command": "docker",
        "args": ["run", "-i", "--rm", "--init", "mcr.microsoft.com/playwright/mcp"],
        "env": {},
    },
    "claude-code-sdk": {
        "description": "Claude Code SDK for building agents",
        "command": "npx",
        "args": ["-y", "@anthropic-ai/claude-code-mcp-server"],
        "env": {},
    },
}

# Tech stack definitions with MCP server configurations
# Prefer Docker-based servers where available
TECH_STACK_SERVERS = {
    # Databases
    "postgres": {
        "description": "PostgreSQL database",
        "servers": {
            "postgres": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "POSTGRES_CONNECTION_STRING",
                    "mcp/postgres"
                ],
                "env": {
                    "POSTGRES_CONNECTION_STRING": {
                        "description": "PostgreSQL connection string",
                        "example": "postgresql://user:password@host.docker.internal:5432/dbname",
                        "required": True,
                    }
                },
            }
        },
    },
    "sqlite": {
        "description": "SQLite database",
        "servers": {
            "sqlite": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-v", "{SQLITE_DIR}:/data",
                    "mcp/sqlite",
                    "--db-path", "/data/{SQLITE_FILE}"
                ],
                "env": {
                    "SQLITE_DIR": {
                        "description": "Directory containing SQLite database",
                        "example": "/home/user/project/data",
                        "required": True,
                    },
                    "SQLITE_FILE": {
                        "description": "SQLite database filename",
                        "example": "app.db",
                        "required": True,
                    },
                },
            }
        },
    },
    "mysql": {
        "description": "MySQL/MariaDB database",
        "servers": {
            "mysql": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "MYSQL_HOST",
                    "-e", "MYSQL_USER",
                    "-e", "MYSQL_PASSWORD",
                    "-e", "MYSQL_DATABASE",
                    "mcp/mysql"
                ],
                "env": {
                    "MYSQL_HOST": {
                        "description": "MySQL host (use host.docker.internal for localhost)",
                        "example": "host.docker.internal",
                        "required": True,
                    },
                    "MYSQL_USER": {
                        "description": "MySQL username",
                        "example": "root",
                        "required": True,
                    },
                    "MYSQL_PASSWORD": {
                        "description": "MySQL password",
                        "example": "",
                        "required": True,
                    },
                    "MYSQL_DATABASE": {
                        "description": "MySQL database name",
                        "example": "myapp",
                        "required": True,
                    },
                },
            }
        },
    },
    "mongodb": {
        "description": "MongoDB database",
        "servers": {
            "mongodb": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "MONGODB_URI",
                    "mcp/mongodb"
                ],
                "env": {
                    "MONGODB_URI": {
                        "description": "MongoDB connection URI (use host.docker.internal for localhost)",
                        "example": "mongodb://host.docker.internal:27017/mydb",
                        "required": True,
                    }
                },
            }
        },
    },
    "redis": {
        "description": "Redis cache/database",
        "servers": {
            "redis": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "REDIS_URL",
                    "mcp/redis"
                ],
                "env": {
                    "REDIS_URL": {
                        "description": "Redis connection URL (use host.docker.internal for localhost)",
                        "example": "redis://host.docker.internal:6379",
                        "required": True,
                    }
                },
            }
        },
    },
    # Version Control & DevOps
    "github": {
        "description": "GitHub repositories and issues",
        "servers": {
            "github": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "mcp/github"
                ],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": {
                        "description": "GitHub personal access token",
                        "example": "ghp_xxxxxxxxxxxx",
                        "required": True,
                    }
                },
            }
        },
    },
    "gitlab": {
        "description": "GitLab repositories",
        "servers": {
            "gitlab": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "GITLAB_PERSONAL_ACCESS_TOKEN",
                    "-e", "GITLAB_API_URL",
                    "mcp/gitlab"
                ],
                "env": {
                    "GITLAB_PERSONAL_ACCESS_TOKEN": {
                        "description": "GitLab personal access token",
                        "example": "glpat-xxxxxxxxxxxx",
                        "required": True,
                    },
                    "GITLAB_API_URL": {
                        "description": "GitLab API URL (for self-hosted)",
                        "example": "https://gitlab.com/api/v4",
                        "required": False,
                    },
                },
            }
        },
    },
    # Cloud Providers
    "aws": {
        "description": "Amazon Web Services",
        "servers": {
            "aws-kb-retrieval": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "AWS_ACCESS_KEY_ID",
                    "-e", "AWS_SECRET_ACCESS_KEY",
                    "-e", "AWS_REGION",
                    "mcp/aws-kb-retrieval"
                ],
                "env": {
                    "AWS_ACCESS_KEY_ID": {
                        "description": "AWS access key ID",
                        "example": "AKIAIOSFODNN7EXAMPLE",
                        "required": True,
                    },
                    "AWS_SECRET_ACCESS_KEY": {
                        "description": "AWS secret access key",
                        "example": "",
                        "required": True,
                    },
                    "AWS_REGION": {
                        "description": "AWS region",
                        "example": "us-east-1",
                        "required": True,
                    },
                },
            }
        },
    },
    "gcp": {
        "description": "Google Cloud Platform",
        "servers": {
            "gdrive": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-v", "{GOOGLE_CREDS_DIR}:/creds:ro",
                    "-e", "GOOGLE_APPLICATION_CREDENTIALS=/creds/{GOOGLE_CREDS_FILE}",
                    "mcp/gdrive"
                ],
                "env": {
                    "GOOGLE_CREDS_DIR": {
                        "description": "Directory containing Google credentials JSON",
                        "example": "/home/user/.config/gcloud",
                        "required": True,
                    },
                    "GOOGLE_CREDS_FILE": {
                        "description": "Google credentials filename",
                        "example": "service-account.json",
                        "required": True,
                    },
                },
            }
        },
    },
    # Communication & Productivity
    "slack": {
        "description": "Slack messaging",
        "servers": {
            "slack": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "SLACK_BOT_TOKEN",
                    "-e", "SLACK_TEAM_ID",
                    "mcp/slack"
                ],
                "env": {
                    "SLACK_BOT_TOKEN": {
                        "description": "Slack bot OAuth token",
                        "example": "xoxb-xxxxxxxxxxxx",
                        "required": True,
                    },
                    "SLACK_TEAM_ID": {
                        "description": "Slack workspace/team ID",
                        "example": "T01234567",
                        "required": True,
                    },
                },
            }
        },
    },
    "notion": {
        "description": "Notion workspace",
        "servers": {
            "notion": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "NOTION_API_KEY",
                    "mcp/notion"
                ],
                "env": {
                    "NOTION_API_KEY": {
                        "description": "Notion integration API key",
                        "example": "secret_xxxxxxxxxxxx",
                        "required": True,
                    }
                },
            }
        },
    },
    "linear": {
        "description": "Linear issue tracking",
        "servers": {
            "linear": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "LINEAR_API_KEY",
                    "mcp/linear"
                ],
                "env": {
                    "LINEAR_API_KEY": {
                        "description": "Linear API key",
                        "example": "lin_api_xxxxxxxxxxxx",
                        "required": True,
                    }
                },
            }
        },
    },
    # File Systems & Storage
    "filesystem": {
        "description": "Local filesystem access",
        "servers": {
            "filesystem": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-v", "{HOST_PATH}:{CONTAINER_PATH}",
                    "mcp/filesystem",
                    "{CONTAINER_PATH}"
                ],
                "env": {
                    "HOST_PATH": {
                        "description": "Host path to mount",
                        "example": "/home/user/projects",
                        "required": True,
                    },
                    "CONTAINER_PATH": {
                        "description": "Container mount path",
                        "example": "/workspace",
                        "required": True,
                    },
                },
            }
        },
    },
    "s3": {
        "description": "AWS S3 storage",
        "servers": {
            "s3": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "AWS_ACCESS_KEY_ID",
                    "-e", "AWS_SECRET_ACCESS_KEY",
                    "-e", "AWS_REGION",
                    "mcp/s3"
                ],
                "env": {
                    "AWS_ACCESS_KEY_ID": {
                        "description": "AWS access key ID",
                        "example": "AKIAIOSFODNN7EXAMPLE",
                        "required": True,
                    },
                    "AWS_SECRET_ACCESS_KEY": {
                        "description": "AWS secret access key",
                        "example": "",
                        "required": True,
                    },
                    "AWS_REGION": {
                        "description": "AWS region",
                        "example": "us-east-1",
                        "required": True,
                    },
                },
            }
        },
    },
    # Search & Data
    "brave-search": {
        "description": "Brave Search API",
        "servers": {
            "brave-search": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "BRAVE_API_KEY",
                    "mcp/brave-search"
                ],
                "env": {
                    "BRAVE_API_KEY": {
                        "description": "Brave Search API key",
                        "example": "BSAxxxxxxxxxxxx",
                        "required": True,
                    }
                },
            }
        },
    },
    "google-maps": {
        "description": "Google Maps API",
        "servers": {
            "google-maps": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "GOOGLE_MAPS_API_KEY",
                    "mcp/google-maps"
                ],
                "env": {
                    "GOOGLE_MAPS_API_KEY": {
                        "description": "Google Maps API key",
                        "example": "AIzaxxxxxxxxxxxx",
                        "required": True,
                    }
                },
            }
        },
    },
    # Browser Automation (non-default playwright options)
    "puppeteer": {
        "description": "Browser automation with Puppeteer",
        "servers": {
            "puppeteer": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "--init", "mcp/puppeteer"],
                "env": {},
            }
        },
    },
    "selenium": {
        "description": "Browser automation with Selenium",
        "servers": {
            "selenium": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "SELENIUM_GRID_URL",
                    "mcp/selenium"
                ],
                "env": {
                    "SELENIUM_GRID_URL": {
                        "description": "Selenium Grid URL",
                        "example": "http://host.docker.internal:4444",
                        "required": False,
                    }
                },
            }
        },
    },
    # Container & Orchestration
    "docker": {
        "description": "Docker container management",
        "servers": {
            "docker": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-v", "/var/run/docker.sock:/var/run/docker.sock",
                    "mcp/docker"
                ],
                "env": {},
            }
        },
    },
    "kubernetes": {
        "description": "Kubernetes cluster management",
        "servers": {
            "kubernetes": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-v", "{KUBECONFIG_DIR}:/root/.kube:ro",
                    "mcp/kubernetes"
                ],
                "env": {
                    "KUBECONFIG_DIR": {
                        "description": "Directory containing kubeconfig",
                        "example": "/home/user/.kube",
                        "required": False,
                    }
                },
            }
        },
    },
    # AI & ML
    "openai": {
        "description": "OpenAI API",
        "servers": {
            "openai": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "OPENAI_API_KEY",
                    "mcp/openai"
                ],
                "env": {
                    "OPENAI_API_KEY": {
                        "description": "OpenAI API key",
                        "example": "sk-xxxxxxxxxxxx",
                        "required": True,
                    }
                },
            }
        },
    },
    # Memory & Context
    "memory": {
        "description": "Persistent memory/context storage",
        "servers": {
            "memory": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-v", "{MEMORY_DIR}:/data",
                    "mcp/memory"
                ],
                "env": {
                    "MEMORY_DIR": {
                        "description": "Directory for memory persistence",
                        "example": "/home/user/.agent/memory",
                        "required": False,
                    }
                },
            }
        },
    },
    # Time & Scheduling
    "time": {
        "description": "Time and timezone utilities",
        "servers": {
            "time": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "mcp/time"],
                "env": {},
            }
        },
    },
    # Data Processing
    "fetch": {
        "description": "HTTP fetching and web scraping",
        "servers": {
            "fetch": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "mcp/fetch"],
                "env": {},
            }
        },
    },
    # Monitoring & Observability
    "sentry": {
        "description": "Sentry error tracking",
        "servers": {
            "sentry": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "SENTRY_AUTH_TOKEN",
                    "-e", "SENTRY_ORG",
                    "mcp/sentry"
                ],
                "env": {
                    "SENTRY_AUTH_TOKEN": {
                        "description": "Sentry authentication token",
                        "example": "sntrys_xxxxxxxxxxxx",
                        "required": True,
                    },
                    "SENTRY_ORG": {
                        "description": "Sentry organization slug",
                        "example": "my-org",
                        "required": True,
                    },
                },
            }
        },
    },
    # Email
    "email": {
        "description": "Email sending via SMTP",
        "servers": {
            "email": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "SMTP_HOST",
                    "-e", "SMTP_PORT",
                    "-e", "SMTP_USER",
                    "-e", "SMTP_PASSWORD",
                    "mcp/email"
                ],
                "env": {
                    "SMTP_HOST": {
                        "description": "SMTP server host",
                        "example": "smtp.gmail.com",
                        "required": True,
                    },
                    "SMTP_PORT": {
                        "description": "SMTP server port",
                        "example": "587",
                        "required": True,
                    },
                    "SMTP_USER": {
                        "description": "SMTP username/email",
                        "example": "user@gmail.com",
                        "required": True,
                    },
                    "SMTP_PASSWORD": {
                        "description": "SMTP password or app password",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Vector Databases
    "qdrant": {
        "description": "Qdrant vector database",
        "servers": {
            "qdrant": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "QDRANT_URL",
                    "-e", "QDRANT_API_KEY",
                    "mcp/qdrant"
                ],
                "env": {
                    "QDRANT_URL": {
                        "description": "Qdrant server URL",
                        "example": "http://host.docker.internal:6333",
                        "required": True,
                    },
                    "QDRANT_API_KEY": {
                        "description": "Qdrant API key (if auth enabled)",
                        "example": "",
                        "required": False,
                    },
                },
            }
        },
    },
    "pinecone": {
        "description": "Pinecone vector database",
        "servers": {
            "pinecone": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "PINECONE_API_KEY",
                    "-e", "PINECONE_ENVIRONMENT",
                    "mcp/pinecone"
                ],
                "env": {
                    "PINECONE_API_KEY": {
                        "description": "Pinecone API key",
                        "example": "",
                        "required": True,
                    },
                    "PINECONE_ENVIRONMENT": {
                        "description": "Pinecone environment",
                        "example": "us-west1-gcp",
                        "required": True,
                    },
                },
            }
        },
    },
}

# Common tech stack presets
STACK_PRESETS = {
    "web-basic": {
        "description": "Basic web development (fetch, memory, github)",
        "stacks": ["fetch", "memory", "github"],
    },
    "fullstack-postgres": {
        "description": "Full-stack with PostgreSQL",
        "stacks": ["fetch", "memory", "github", "postgres", "docker"],
    },
    "fullstack-mongo": {
        "description": "Full-stack with MongoDB",
        "stacks": ["fetch", "memory", "github", "mongodb", "docker"],
    },
    "data-science": {
        "description": "Data science workflow",
        "stacks": ["memory", "postgres", "s3", "qdrant"],
    },
    "devops": {
        "description": "DevOps and infrastructure",
        "stacks": ["github", "docker", "kubernetes", "aws", "sentry"],
    },
    "ai-agent": {
        "description": "AI agent development",
        "stacks": ["memory", "fetch", "openai", "qdrant", "github"],
    },
}


def get_stack_config_path(project_path: Path = None) -> Path:
    """Get tech stack config path."""
    return db.get_agent_dir(project_path) / "stack.json"


def load_stack_config(project_path: Path = None) -> dict:
    """Load current tech stack configuration."""
    path = get_stack_config_path(project_path)
    if not path.exists():
        return {"stacks": [], "pending_env": {}, "defaults_configured": False}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"stacks": [], "pending_env": {}, "defaults_configured": False}


def save_stack_config(config: dict, project_path: Path = None):
    """Save tech stack configuration."""
    path = get_stack_config_path(project_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2))


def configure_defaults(project_path: Path = None) -> dict:
    """Configure default MCP servers (playwright, claude-code-sdk).

    These are always configured on init.

    Returns:
        Dict with 'servers_added' list
    """
    servers_added = []

    for server_name, server_config in DEFAULT_SERVERS.items():
        mcp.add_mcp_server(
            server_name,
            server_config["command"],
            server_config["args"],
            server_config.get("env") or None,
            project_path,
        )
        servers_added.append(server_name)

    # Mark defaults as configured
    config = load_stack_config(project_path)
    config["defaults_configured"] = True
    save_stack_config(config, project_path)

    return {"servers_added": servers_added}


def are_defaults_configured(project_path: Path = None) -> bool:
    """Check if default servers have been configured."""
    config = load_stack_config(project_path)
    return config.get("defaults_configured", False)


def list_available_stacks() -> dict:
    """List all available tech stacks."""
    result = {}
    for name, info in TECH_STACK_SERVERS.items():
        servers = list(info.get("servers", {}).keys())
        result[name] = {
            "description": info.get("description", ""),
            "servers": servers,
        }
    return result


def list_presets() -> dict:
    """List all available stack presets."""
    return STACK_PRESETS


def list_defaults() -> dict:
    """List default MCP servers."""
    return {
        name: {"description": config["description"]}
        for name, config in DEFAULT_SERVERS.items()
    }


def get_required_env_vars(stack_name: str) -> dict:
    """Get required environment variables for a tech stack."""
    if stack_name not in TECH_STACK_SERVERS:
        return {}

    stack = TECH_STACK_SERVERS[stack_name]
    env_vars = {}

    for server_name, server_config in stack.get("servers", {}).items():
        for env_name, env_info in server_config.get("env", {}).items():
            env_vars[env_name] = {
                "server": server_name,
                "description": env_info.get("description", ""),
                "example": env_info.get("example", ""),
                "required": env_info.get("required", False),
            }

    return env_vars


def _substitute_env_in_args(args: list, env_values: dict) -> list:
    """Substitute environment variables in args list."""
    result = []
    for arg in args:
        if "{" in arg and "}" in arg:
            # Find all placeholders
            import re
            placeholders = re.findall(r'\{(\w+)\}', arg)
            new_arg = arg
            for placeholder in placeholders:
                if placeholder in env_values:
                    new_arg = new_arg.replace(f"{{{placeholder}}}", env_values[placeholder])
                else:
                    new_arg = new_arg.replace(f"{{{placeholder}}}", f"<{placeholder}>")
            result.append(new_arg)
        else:
            result.append(arg)
    return result


def configure_stack(
    stack_name: str,
    env_values: dict = None,
    project_path: Path = None,
) -> dict:
    """Configure MCP servers for a tech stack.

    Args:
        stack_name: Name of the tech stack to configure
        env_values: Dict of environment variable values
        project_path: Project path

    Returns:
        Dict with 'success', 'servers_added', 'pending_env' keys
    """
    if stack_name not in TECH_STACK_SERVERS:
        return {"success": False, "error": f"Unknown stack: {stack_name}"}

    stack = TECH_STACK_SERVERS[stack_name]
    env_values = env_values or {}
    servers_added = []
    pending_env = {}

    for server_name, server_config in stack.get("servers", {}).items():
        command = server_config.get("command")
        args = server_config.get("args", [])

        # Substitute env values in args
        processed_args = _substitute_env_in_args(args, env_values)

        # Collect environment variables for the server
        server_env = {}
        server_pending = {}

        for env_name, env_info in server_config.get("env", {}).items():
            if env_name in env_values:
                server_env[env_name] = env_values[env_name]
            elif env_info.get("required", False):
                server_pending[env_name] = {
                    "description": env_info.get("description", ""),
                    "example": env_info.get("example", ""),
                }

        # Add server to MCP config
        mcp.add_mcp_server(
            server_name,
            command,
            processed_args,
            server_env if server_env else None,
            project_path,
        )
        servers_added.append(server_name)

        if server_pending:
            pending_env[server_name] = server_pending

    # Update stack config
    config = load_stack_config(project_path)
    if stack_name not in config["stacks"]:
        config["stacks"].append(stack_name)
    if pending_env:
        config["pending_env"].update(pending_env)
    save_stack_config(config, project_path)

    return {
        "success": True,
        "servers_added": servers_added,
        "pending_env": pending_env,
    }


def configure_preset(
    preset_name: str,
    env_values: dict = None,
    project_path: Path = None,
) -> dict:
    """Configure all stacks in a preset.

    Args:
        preset_name: Name of the preset to configure
        env_values: Dict of environment variable values
        project_path: Project path

    Returns:
        Dict with results for each stack
    """
    if preset_name not in STACK_PRESETS:
        return {"success": False, "error": f"Unknown preset: {preset_name}"}

    preset = STACK_PRESETS[preset_name]
    results = {"success": True, "stacks": {}, "all_pending_env": {}}

    for stack_name in preset["stacks"]:
        result = configure_stack(stack_name, env_values, project_path)
        results["stacks"][stack_name] = result
        if result.get("pending_env"):
            results["all_pending_env"].update(result["pending_env"])

    return results


def update_server_env(
    server_name: str,
    env_values: dict,
    project_path: Path = None,
) -> bool:
    """Update environment variables for an existing server.

    Args:
        server_name: Name of the MCP server
        env_values: Dict of environment variable values to update
        project_path: Project path

    Returns:
        True if successful, False otherwise
    """
    mcp_path = mcp.get_agent_mcp_path(project_path)
    if not mcp_path.exists():
        return False

    data = json.loads(mcp_path.read_text())
    servers = data.get("mcpServers", {})

    if server_name not in servers:
        return False

    # Update env vars
    if "env" not in servers[server_name]:
        servers[server_name]["env"] = {}

    servers[server_name]["env"].update(env_values)

    # Remove placeholder values from pending
    config = load_stack_config(project_path)
    if server_name in config.get("pending_env", {}):
        for env_name in env_values:
            if env_name in config["pending_env"][server_name]:
                del config["pending_env"][server_name][env_name]
        if not config["pending_env"][server_name]:
            del config["pending_env"][server_name]
        save_stack_config(config, project_path)

    mcp_path.write_text(json.dumps(data, indent=2))
    return True


def get_pending_env(project_path: Path = None) -> dict:
    """Get all pending environment variables that need to be configured."""
    config = load_stack_config(project_path)
    return config.get("pending_env", {})


def get_configured_stacks(project_path: Path = None) -> list:
    """Get list of configured tech stacks."""
    config = load_stack_config(project_path)
    return config.get("stacks", [])
