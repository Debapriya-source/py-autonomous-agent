# Py Autonomous Agent

Autonomous coding agent. Code, test, ship from plans.

## Structure

- `agent/` - main package
  - `cli.py` - click commands
  - `db.py` - sqlite ops
  - `knowledge.py` - project scanning
  - `core.py` - orchestration
  - `claude_bridge.py` - claude code wrapper
  - `mcp.py` - MCP config management
  - `tech_stack.py` - tech stack to MCP mapping
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

## Tech Stack

Configure MCP servers based on your tech stack. Docker-based servers preferred.

```bash
agent stack list              # show available stacks
agent stack presets           # show preset collections
agent stack add <stack...>    # add tech stacks
agent stack preset <name>     # add preset collection
agent stack configure <srv>   # configure server auth
agent stack pending           # show pending config
agent stack show              # show current config
agent stack info <stack>      # details about a stack
```

Default servers (always configured on init):
- `playwright` - Browser automation (Docker)
- `claude-code-sdk` - Claude Code SDK for agents

Available stacks: postgres, mysql, mongodb, redis, sqlite, github, gitlab, aws, gcp, slack, notion, linear, filesystem, s3, docker, kubernetes, openai, memory, fetch, sentry, etc.

Presets:
- `web-basic` - fetch, memory, github
- `fullstack-postgres` - fetch, memory, github, postgres, docker
- `fullstack-mongo` - fetch, memory, github, mongodb, docker
- `data-science` - memory, postgres, s3, qdrant
- `devops` - github, docker, kubernetes, aws, sentry
- `ai-agent` - memory, fetch, openai, qdrant, github

Example:
```bash
agent stack add postgres github
agent stack configure postgres -i  # interactive auth setup
agent stack preset devops -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx
```

Config in `.agent/stack.json`.

## Data

All in `.agent/` dir: agent.db, mcp.json, stack.json, skills.json, plans/

## Skills/Plugins

```bash
agent skills list           # show skills
agent skills enable <name>  # enable skill
agent skills disable <name> # disable skill
```

Known skills:
- `feature-dev` - Guided feature development
- `agent-sdk-dev:new-sdk-app` - Create Agent SDK app

Auto-selects skill based on task keywords (feature, implement, add, create, build).

Config in `.agent/skills.json`.

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
