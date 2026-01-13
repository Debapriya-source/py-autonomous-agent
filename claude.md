# Test Agent

Autonomous coding agent. Code, test, ship from plans.

## Structure

- `agent/` - main package
  - `cli.py` - click commands
  - `db.py` - sqlite ops
  - `knowledge.py` - project scanning
  - `core.py` - orchestration
  - `claude_bridge.py` - claude code wrapper
  - `mcp.py` - MCP config management
  - `skills/` - coder, tester, shipper
  - `subagents/` - planner, executor, reviewer

## Usage

```bash
agent init          # scan project, init mcp
agent plan file.md  # load plan
agent plan -i       # interactive
agent run           # execute
agent status        # show state
```

## MCP Servers

```bash
agent mcp list                # show all servers (merged)
agent mcp add <name> <pkg>    # add server
agent mcp remove <name>       # remove server
agent mcp test <name>         # test connection
```

Config inheritance (highest priority first):
1. `.agent/mcp.json` - agent-specific
2. `.claude/settings.json` - project Claude config
3. `~/.claude/settings.json` - global Claude config

Example:
```bash
agent mcp add fs @anthropic/mcp-server-filesystem
agent mcp add github @anthropic/mcp-server-github -e GITHUB_TOKEN=xxx
```

## Data

All in `.agent/` dir: agent.db, mcp.json, plans/

## Code Quality

```bash
uv run ruff check agent/      # lint
uv run ruff check agent/ --fix  # auto-fix
```

## Design

- Sequential task execution
- Ship ops prompt user
- Claude Code CLI for AI
- MCP config auto-merged from all sources
- Ruff linter for code quality
