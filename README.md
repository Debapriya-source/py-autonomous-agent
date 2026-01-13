# Test Agent

Simple autonomous coding agent. Code, test, and ship based on plans. Uses SQLite for task tracking and Claude Code CLI for AI.

## Features

- **Plan-based execution** - Markdown files or interactive
- **SQLite task tracking** - Persistent state
- **Auto-detect test frameworks** - pytest, jest, vitest, go test, cargo test
- **MCP server support** - Inherits existing Claude configs
- **User-controlled shipping** - Git ops always prompt

## Requirements

- Python 3.10+
- [Claude Code CLI](https://github.com/anthropics/claude-code) installed

## Installation

```bash
pip install git+https://github.com/Debapriya-source/test-agent.git

# or with uv
uv add git+https://github.com/Debapriya-source/test-agent.git
```

## Quick Start

```bash
cd /path/to/your-project

# Initialize
agent init

# Create plan (interactive)
agent plan -i

# Or from file
agent plan my-plan.md

# Execute
agent run -a

# Check status
agent status
```

## Plan Format

```markdown
# Feature Name

- [ ] First task
- [ ] Second task
- [ ] Write tests
- [ ] Ship changes
```

Or numbered:
```markdown
# Bug Fix

1. Investigate issue
2. Fix root cause
3. Add test
4. Ship
```

## Commands

| Command | Description |
|---------|-------------|
| `agent init` | Initialize in project |
| `agent plan <file>` | Load plan from markdown |
| `agent plan -i` | Interactive plan creation |
| `agent run` | Execute next task |
| `agent run -a` | Execute all tasks |
| `agent run -t <id>` | Execute specific task |
| `agent status` | Show task status |
| `agent knowledge` | Show project info |
| `agent validate` | Run tests + review |
| `agent reset` | Clear all tasks |

## MCP Servers

```bash
agent mcp list                 # show servers
agent mcp add <name> <pkg>     # add server
agent mcp remove <name>        # remove server
agent mcp test <name>          # test connection
```

Config priority: `.agent/mcp.json` > `.claude/settings.json` > `~/.claude/settings.json`

Example:
```bash
agent mcp add fs @anthropic/mcp-server-filesystem
agent mcp add github @anthropic/mcp-server-github -e GITHUB_TOKEN=xxx
```

## Project Data

Created in `.agent/`:
```
.agent/
├── agent.db    # SQLite database
├── mcp.json    # MCP config
└── plans/      # Plan files
```

## Example Workflow

```bash
cd ~/projects/my-api
agent init

# Create plan
cat > auth.md << 'EOF'
# Add Authentication

- [ ] Create auth middleware
- [ ] Add login endpoint
- [ ] Write tests
- [ ] Ship
EOF

agent plan auth.md
agent run -a
agent status
```

## Development

```bash
git clone https://github.com/Debapriya-source/test-agent.git
cd test-agent
uv sync
uv run ruff check agent/
uv run agent --help
```

## License

MIT
