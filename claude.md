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

Available stacks (90+):
- **Databases**: postgres, mysql, mongodb, redis, sqlite, supabase, neon, planetscale, turso, upstash, neo4j
- **Vector DBs**: qdrant, pinecone, weaviate, chroma, milvus
- **Git/DevOps**: github, gitlab, bitbucket, docker, kubernetes, terraform, pulumi
- **Cloud**: aws, gcp, azure, cloudflare, vercel, netlify, fly, railway, render
- **AI/ML**: openai, anthropic, groq, mistral, cohere, replicate, huggingface, together, perplexity
- **Search**: algolia, typesense, meilisearch, elasticsearch, tavily, exa, serper, brave-search
- **Comms**: slack, discord, telegram, teams, twilio
- **Productivity**: notion, linear, jira, asana, trello, monday, clickup, todoist, confluence
- **Email**: sendgrid, resend, mailgun, postmark
- **Payments**: stripe, paypal, shopify
- **Auth**: auth0, clerk, firebase
- **Analytics**: segment, mixpanel, amplitude, posthog, datadog, newrelic, grafana, sentry
- **CMS**: contentful, sanity, strapi
- **CRM**: hubspot, salesforce
- **Data**: snowflake, bigquery, databricks, airtable, google-sheets
- **Scraping**: firecrawl, browserbase, apify
- **Code**: e2b, modal
- **Secrets**: vault, doppler
- **Queues**: rabbitmq, kafka
- **Misc**: memory, fetch, time, git, sequential-thinking, zapier, make

Presets:
- `web-basic` - fetch, memory, github, git
- `fullstack-postgres` - fetch, memory, github, postgres, docker, git
- `fullstack-supabase` - fetch, memory, github, supabase, git
- `serverless` - fetch, memory, github, vercel, neon, upstash, git
- `ai-agent` - memory, fetch, openai, qdrant, github, e2b, firecrawl
- `ai-search` - memory, fetch, tavily, exa, qdrant, openai
- `saas` - github, supabase, stripe, resend, posthog, sentry
- `startup` - github, vercel, supabase, stripe, resend, slack, linear
- `enterprise` - github, jira, confluence, slack, datadog, vault
- `devops` - github, docker, kubernetes, aws, sentry, terraform
- `ecommerce` - github, shopify, stripe, sendgrid, algolia, segment
- `ml-ops` - github, aws, s3, snowflake, databricks, huggingface

Example:
```bash
agent stack add postgres github
agent stack configure postgres -i  # interactive auth setup
agent stack preset devops -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx
```

### Custom MCP Servers

Add your own MCP servers not in the built-in list:

```bash
agent stack custom                    # list custom MCPs
agent stack custom-add <name> <cmd>   # add custom MCP
agent stack custom-remove <name>      # remove custom MCP
```

Examples:
```bash
# Add npm package MCP
agent stack custom-add my-mcp @org/my-mcp-server -p -d "My custom server"

# Add with custom command and args
agent stack custom-add db-tool docker -a run -a -i -a --rm -a mcp/db-tool

# Add with environment variables
agent stack custom-add api-mcp npx -a @company/api-mcp -e "API_KEY:API key" -e "API_URL:API endpoint"

# Then use it like any other stack
agent stack add my-mcp
agent stack configure my-mcp -i
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
