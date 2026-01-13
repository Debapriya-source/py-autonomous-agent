"""CLI interface."""
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import mcp, skills_config
from .core import Agent

console = Console()

@click.group()
@click.option("--path", "-p", type=click.Path(exists=True), help="Project path")
@click.pass_context
def main(ctx, path):
    """Autonomous coding agent."""
    ctx.ensure_object(dict)
    ctx.obj["agent"] = Agent(Path(path) if path else None)

@main.command()
@click.pass_context
def init(ctx):
    """Initialize agent in project."""
    agent = ctx.obj["agent"]
    console.print("[bold]Initializing agent...[/bold]")

    result = agent.init()

    if result["success"]:
        console.print("[green]Initialized![/green]")
        console.print(f"Languages: {', '.join(result['languages']) or 'none detected'}")
        console.print(f"Frameworks: {', '.join(result['frameworks']) or 'none detected'}")
        console.print(f"Test framework: {result['test_framework'] or 'none detected'}")
        console.print(f"Files: {result['file_count']}")
        console.print(f"Git: {'yes' if result['has_git'] else 'no'}")
        console.print(f"MCP servers: {result.get('mcp_servers', 0)}")
        console.print(f"Skills: {', '.join(result.get('skills', [])) or 'none'}")
    else:
        console.print(f"[red]Error: {result['error']}[/red]")

@main.command()
@click.argument("file", required=False)
@click.option("--interactive", "-i", is_flag=True, help="Create plan interactively")
@click.pass_context
def plan(ctx, file, interactive):
    """Load or create a plan."""
    agent = ctx.obj["agent"]

    if interactive:
        result = agent.plan(interactive=True)
    elif file:
        result = agent.plan(file_path=file)
    else:
        console.print("[red]Provide a plan file or use -i for interactive[/red]")
        return

    if result["success"]:
        console.print(f"[green]Plan created: {result['title']}[/green]")
        console.print(f"Tasks: {result['task_count']}")
    else:
        console.print(f"[red]Error: {result['error']}[/red]")

@main.command()
@click.option("--task", "-t", type=int, help="Run specific task ID")
@click.option("--all", "-a", "all_tasks", is_flag=True, help="Run all pending tasks")
@click.pass_context
def run(ctx, task, all_tasks):
    """Execute tasks."""
    agent = ctx.obj["agent"]

    if task:
        console.print(f"[bold]Running task {task}...[/bold]")
        result = agent.run(task_id=task)
    elif all_tasks:
        console.print("[bold]Running all tasks...[/bold]")
        result = agent.run(all_tasks=True)
    else:
        console.print("[bold]Running next task...[/bold]")
        result = agent.run()

    if result.get("success"):
        msg = result.get("message", "Done")
        console.print(f"[green]{msg}[/green]")
        if "tasks_executed" in result:
            console.print(f"Tasks executed: {result['tasks_executed']}")
    else:
        console.print(f"[red]Error: {result.get('error', 'Failed')}[/red]")

@main.command()
@click.pass_context
def status(ctx):
    """Show current status."""
    agent = ctx.obj["agent"]
    result = agent.status()

    console.print(f"\n[bold]Plans:[/bold] {result['plans']}")

    tasks = result["tasks"]
    console.print("\n[bold]Tasks:[/bold]")
    console.print(f"  Total: {tasks['total']}")
    console.print(f"  Pending: {tasks['pending']}")
    console.print(f"  In Progress: {tasks['in_progress']}")
    console.print(f"  Completed: {tasks['completed']}")
    console.print(f"  Failed: {tasks['failed']}")

    if result["pending_tasks"]:
        console.print("\n[bold]Pending:[/bold]")
        table = Table()
        table.add_column("ID")
        table.add_column("Title")
        table.add_column("Type")
        for t in result["pending_tasks"][:10]:
            table.add_row(str(t["id"]), t["title"][:50], t["task_type"])
        console.print(table)

    if result["failed_tasks"]:
        console.print("\n[bold red]Failed:[/bold red]")
        for t in result["failed_tasks"]:
            console.print(f"  [{t['id']}] {t['title']}: {t.get('result', '')[:50]}")

@main.command("knowledge")
@click.pass_context
def show_knowledge(ctx):
    """Show knowledge base summary."""
    agent = ctx.obj["agent"]
    result = agent.knowledge_summary()

    if not result:
        console.print("[yellow]No knowledge yet. Run 'agent init' first.[/yellow]")
        return

    console.print("\n[bold]Project Knowledge:[/bold]")
    for key, value in result.items():
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value) or "none"
        console.print(f"  {key}: {value}")

@main.command()
@click.confirmation_option(prompt="Clear all tasks and plans?")
@click.pass_context
def reset(ctx):
    """Reset all tasks and plans."""
    agent = ctx.obj["agent"]
    result = agent.reset()
    console.print(f"[green]{result['message']}[/green]")

@main.command()
@click.pass_context
def validate(ctx):
    """Run validation (tests + review)."""
    agent = ctx.obj["agent"]
    console.print("[bold]Running validation...[/bold]")

    result = agent.validate()

    if result.get("tests"):
        test_status = "[green]passed[/green]" if result["tests"]["success"] else "[red]failed[/red]"
        console.print(f"Tests: {test_status}")

    if result.get("review"):
        console.print(f"Review: {result['review'].get('message', 'done')}")

    if result["success"]:
        console.print("\n[green]Validation passed![/green]")
    else:
        console.print("\n[red]Validation failed[/red]")

# MCP commands
@main.group("mcp")
@click.pass_context
def mcp_group(ctx):
    """Manage MCP servers."""
    pass

@mcp_group.command("list")
@click.pass_context
def mcp_list(ctx):
    """List all MCP servers."""
    agent = ctx.obj["agent"]
    servers = mcp.list_mcp_servers(agent.project_path)

    if not servers:
        console.print("[yellow]No MCP servers configured[/yellow]")
        return

    table = Table(title="MCP Servers")
    table.add_column("Name")
    table.add_column("Command")
    table.add_column("Source")

    for name, info in servers.items():
        cmd = info["config"].get("command", "")
        args = " ".join(info["config"].get("args", []))
        source = info["source"]
        source_color = {"agent": "green", "project": "blue", "global": "dim"}.get(source, "white")
        table.add_row(name, f"{cmd} {args}"[:40], f"[{source_color}]{source}[/{source_color}]")

    console.print(table)

@mcp_group.command("add")
@click.argument("name")
@click.argument("package")
@click.option("--env", "-e", multiple=True, help="Environment var (KEY=VALUE)")
@click.pass_context
def mcp_add(ctx, name, package, env):
    """Add MCP server.

    Examples:
        agent mcp add fs @anthropic/mcp-server-filesystem
        agent mcp add github @anthropic/mcp-server-github -e GITHUB_TOKEN=xxx
    """
    agent = ctx.obj["agent"]

    # Parse package to command/args
    command, args = mcp.parse_package_to_command(package)

    # Parse env vars
    env_dict = {}
    for e in env:
        if "=" in e:
            k, v = e.split("=", 1)
            env_dict[k] = v

    mcp.add_mcp_server(name, command, args, env_dict or None, agent.project_path)
    console.print(f"[green]Added MCP server: {name}[/green]")

@mcp_group.command("remove")
@click.argument("name")
@click.pass_context
def mcp_remove(ctx, name):
    """Remove MCP server from agent config."""
    agent = ctx.obj["agent"]

    if mcp.remove_mcp_server(name, agent.project_path):
        console.print(f"[green]Removed: {name}[/green]")
    else:
        console.print(f"[yellow]Not found in agent config: {name}[/yellow]")

@mcp_group.command("test")
@click.argument("name")
@click.pass_context
def mcp_test(ctx, name):
    """Test MCP server connection."""
    agent = ctx.obj["agent"]
    servers = mcp.get_merged_mcp_config(agent.project_path)

    if name not in servers:
        console.print(f"[red]Server not found: {name}[/red]")
        return

    config = servers[name]
    cmd = config.get("command")
    args = config.get("args", [])

    console.print(f"Testing {name}...")
    console.print(f"  Command: {cmd} {' '.join(args)}")

    # Try to run with --help or version
    import subprocess
    try:
        result = subprocess.run(
            [cmd] + args + ["--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            console.print("[green]Server appears valid[/green]")
        else:
            console.print("[yellow]Server responded with error[/yellow]")
    except FileNotFoundError:
        console.print(f"[red]Command not found: {cmd}[/red]")
    except subprocess.TimeoutExpired:
        console.print("[yellow]Server started (timeout waiting for response)[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# Skills commands
@main.group("skills")
@click.pass_context
def skills_group(ctx):
    """Manage Claude Code skills/plugins."""
    pass

@skills_group.command("list")
@click.pass_context
def skills_list(ctx):
    """List all available skills."""
    agent = ctx.obj["agent"]
    skills = skills_config.list_skills(agent.project_path)

    if not skills:
        console.print("[yellow]No skills available[/yellow]")
        return

    table = Table(title="Skills")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Status")

    for name, info in skills.items():
        status = "[green]enabled[/green]" if info["enabled"] else "[dim]disabled[/dim]"
        table.add_row(name, info["description"][:40], status)

    console.print(table)

@skills_group.command("enable")
@click.argument("name")
@click.pass_context
def skills_enable(ctx, name):
    """Enable a skill."""
    agent = ctx.obj["agent"]
    skills_config.enable_skill(name, agent.project_path)
    console.print(f"[green]Enabled: {name}[/green]")

@skills_group.command("disable")
@click.argument("name")
@click.pass_context
def skills_disable(ctx, name):
    """Disable a skill."""
    agent = ctx.obj["agent"]
    skills_config.disable_skill(name, agent.project_path)
    console.print(f"[yellow]Disabled: {name}[/yellow]")

if __name__ == "__main__":
    main()
