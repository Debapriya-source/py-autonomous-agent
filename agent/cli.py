"""CLI interface."""
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import mcp, skills_config, tech_stack
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
        if result.get('default_servers'):
            console.print(f"Default MCPs: {', '.join(result['default_servers'])}")
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


# Stack commands
@main.group("stack")
@click.pass_context
def stack_group(ctx):
    """Configure tech stack and MCP servers."""
    pass


@stack_group.command("list")
@click.pass_context
def stack_list(ctx):
    """List available tech stacks."""
    stacks = tech_stack.list_available_stacks()

    # Show defaults first
    console.print("\n[bold]Default Servers (always configured):[/bold]")
    defaults = tech_stack.list_defaults()
    for name, info in defaults.items():
        console.print(f"  [green]{name}[/green] - {info['description']}")

    console.print("\n[bold]Available Tech Stacks:[/bold]")
    table = Table()
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Servers")

    for name, info in sorted(stacks.items()):
        servers = ", ".join(info["servers"])
        table.add_row(name, info["description"], servers)

    console.print(table)


@stack_group.command("presets")
@click.pass_context
def stack_presets(ctx):
    """List available stack presets."""
    presets = tech_stack.list_presets()

    console.print("\n[bold]Stack Presets:[/bold]")
    table = Table()
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Includes")

    for name, info in presets.items():
        includes = ", ".join(info["stacks"])
        table.add_row(name, info["description"], includes)

    console.print(table)


@stack_group.command("add")
@click.argument("stacks", nargs=-1, required=True)
@click.option("--env", "-e", multiple=True, help="Environment var (KEY=VALUE)")
@click.pass_context
def stack_add(ctx, stacks, env):
    """Add tech stacks to configure MCP servers.

    Examples:
        agent stack add postgres github
        agent stack add github -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx
        agent stack add postgres -e POSTGRES_CONNECTION_STRING=postgresql://...
    """
    agent = ctx.obj["agent"]

    # Parse env vars
    env_values = {}
    for e in env:
        if "=" in e:
            k, v = e.split("=", 1)
            env_values[k] = v

    all_pending = {}

    for stack_name in stacks:
        result = tech_stack.configure_stack(stack_name, env_values, agent.project_path)

        if result.get("success"):
            servers = ", ".join(result["servers_added"])
            console.print(f"[green]Added stack '{stack_name}': {servers}[/green]")

            if result.get("pending_env"):
                all_pending.update(result["pending_env"])
        else:
            console.print(f"[red]Error: {result.get('error')}[/red]")

    # Show pending env vars that need configuration
    if all_pending:
        console.print("\n[yellow]Pending configuration required:[/yellow]")
        for server_name, vars in all_pending.items():
            console.print(f"\n  [bold]{server_name}:[/bold]")
            for var_name, var_info in vars.items():
                console.print(f"    {var_name}: {var_info['description']}")
                if var_info.get("example"):
                    console.print(f"      [dim]Example: {var_info['example']}[/dim]")

        console.print("\n[dim]Use 'agent stack configure <server>' to set values[/dim]")


@stack_group.command("preset")
@click.argument("name")
@click.option("--env", "-e", multiple=True, help="Environment var (KEY=VALUE)")
@click.pass_context
def stack_preset(ctx, name, env):
    """Configure a preset stack collection.

    Examples:
        agent stack preset web-basic
        agent stack preset fullstack-postgres -e POSTGRES_CONNECTION_STRING=...
    """
    agent = ctx.obj["agent"]

    # Parse env vars
    env_values = {}
    for e in env:
        if "=" in e:
            k, v = e.split("=", 1)
            env_values[k] = v

    result = tech_stack.configure_preset(name, env_values, agent.project_path)

    if not result.get("success"):
        console.print(f"[red]Error: {result.get('error')}[/red]")
        return

    console.print(f"[green]Configured preset '{name}'[/green]")

    for stack_name, stack_result in result["stacks"].items():
        if stack_result.get("success"):
            servers = ", ".join(stack_result["servers_added"])
            console.print(f"  {stack_name}: {servers}")

    # Show pending env vars
    if result.get("all_pending_env"):
        console.print("\n[yellow]Pending configuration required:[/yellow]")
        for server_name, vars in result["all_pending_env"].items():
            console.print(f"\n  [bold]{server_name}:[/bold]")
            for var_name, var_info in vars.items():
                console.print(f"    {var_name}: {var_info['description']}")

        console.print("\n[dim]Use 'agent stack configure <server>' to set values[/dim]")


@stack_group.command("configure")
@click.argument("server")
@click.option("--env", "-e", multiple=True, help="Environment var (KEY=VALUE)")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
@click.pass_context
def stack_configure(ctx, server, env, interactive):
    """Configure environment variables for a server.

    Examples:
        agent stack configure github -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx
        agent stack configure postgres -i  # interactive mode
    """
    agent = ctx.obj["agent"]

    if interactive:
        # Get pending env vars for this server
        pending = tech_stack.get_pending_env(agent.project_path)
        server_pending = pending.get(server, {})

        if not server_pending:
            # Try to get required vars from stack definition
            for stack_name, stack_info in tech_stack.TECH_STACK_SERVERS.items():
                for srv_name, srv_config in stack_info.get("servers", {}).items():
                    if srv_name == server:
                        for env_name, env_info in srv_config.get("env", {}).items():
                            if env_info.get("required"):
                                server_pending[env_name] = env_info

        if not server_pending:
            console.print(f"[yellow]No configuration needed for {server}[/yellow]")
            return

        env_values = {}
        console.print(f"\n[bold]Configure {server}:[/bold]")

        for var_name, var_info in server_pending.items():
            desc = var_info.get("description", "")
            example = var_info.get("example", "")

            if desc:
                console.print(f"  [dim]{desc}[/dim]")
            if example:
                console.print(f"  [dim]Example: {example}[/dim]")

            value = click.prompt(f"  {var_name}", default="", show_default=False)
            if value:
                env_values[var_name] = value

        if env_values:
            if tech_stack.update_server_env(server, env_values, agent.project_path):
                console.print(f"[green]Updated {server} configuration[/green]")
            else:
                console.print(f"[red]Failed to update {server}[/red]")
    else:
        # Parse env vars from command line
        env_values = {}
        for e in env:
            if "=" in e:
                k, v = e.split("=", 1)
                env_values[k] = v

        if not env_values:
            console.print("[red]No environment variables provided. Use -e KEY=VALUE or -i for interactive[/red]")
            return

        if tech_stack.update_server_env(server, env_values, agent.project_path):
            console.print(f"[green]Updated {server} configuration[/green]")
        else:
            console.print(f"[red]Server '{server}' not found in config[/red]")


@stack_group.command("pending")
@click.pass_context
def stack_pending(ctx):
    """Show pending environment variables that need configuration."""
    agent = ctx.obj["agent"]
    pending = tech_stack.get_pending_env(agent.project_path)

    if not pending:
        console.print("[green]No pending configuration[/green]")
        return

    console.print("\n[yellow]Pending configuration:[/yellow]")
    for server_name, vars in pending.items():
        console.print(f"\n[bold]{server_name}:[/bold]")
        for var_name, var_info in vars.items():
            console.print(f"  {var_name}: {var_info['description']}")
            if var_info.get("example"):
                console.print(f"    [dim]Example: {var_info['example']}[/dim]")

    console.print("\n[dim]Use 'agent stack configure <server> -i' to set values interactively[/dim]")


@stack_group.command("show")
@click.pass_context
def stack_show(ctx):
    """Show current tech stack configuration."""
    agent = ctx.obj["agent"]

    configured = tech_stack.get_configured_stacks(agent.project_path)
    defaults_ok = tech_stack.are_defaults_configured(agent.project_path)

    console.print("\n[bold]Current Configuration:[/bold]")

    # Default servers
    console.print("\n[bold]Default Servers:[/bold]")
    if defaults_ok:
        for name, info in tech_stack.list_defaults().items():
            console.print(f"  [green]{name}[/green] - {info['description']}")
    else:
        console.print("  [yellow]Not yet configured. Run 'agent init' first.[/yellow]")

    # Configured stacks
    console.print("\n[bold]Configured Stacks:[/bold]")
    if configured:
        for stack_name in configured:
            console.print(f"  [green]{stack_name}[/green]")
    else:
        console.print("  [dim]None[/dim]")

    # Pending env vars
    pending = tech_stack.get_pending_env(agent.project_path)
    if pending:
        console.print("\n[yellow]Pending Configuration:[/yellow]")
        for server_name, vars in pending.items():
            var_names = ", ".join(vars.keys())
            console.print(f"  {server_name}: {var_names}")


@stack_group.command("info")
@click.argument("stack_name")
@click.pass_context
def stack_info(ctx, stack_name):
    """Show details about a specific tech stack."""
    if stack_name not in tech_stack.TECH_STACK_SERVERS:
        console.print(f"[red]Unknown stack: {stack_name}[/red]")
        return

    stack = tech_stack.TECH_STACK_SERVERS[stack_name]

    console.print(f"\n[bold]{stack_name}[/bold]")
    console.print(f"  {stack.get('description', '')}")

    for server_name, server_config in stack.get("servers", {}).items():
        console.print(f"\n  [bold]Server: {server_name}[/bold]")
        console.print(f"    Command: {server_config.get('command')}")
        args = " ".join(server_config.get("args", []))
        console.print(f"    Args: {args[:60]}...")

        env_vars = server_config.get("env", {})
        if env_vars:
            console.print("    [bold]Environment Variables:[/bold]")
            for env_name, env_info in env_vars.items():
                required = "[required]" if env_info.get("required") else "[optional]"
                console.print(f"      {env_name} {required}")
                console.print(f"        {env_info.get('description', '')}")
                if env_info.get("example"):
                    console.print(f"        [dim]Example: {env_info['example']}[/dim]")


if __name__ == "__main__":
    main()
