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
    "supabase": {
        "description": "Supabase (PostgreSQL, Auth, Storage, Edge Functions)",
        "servers": {
            "supabase": {
                "command": "npx",
                "args": ["-y", "@supabase/mcp-server-supabase@latest"],
                "env": {
                    "SUPABASE_ACCESS_TOKEN": {
                        "description": "Supabase personal access token (from supabase.com/dashboard/account/tokens)",
                        "example": "sbp_xxxxxxxxxxxx",
                        "required": True,
                    },
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
    "weaviate": {
        "description": "Weaviate vector database",
        "servers": {
            "weaviate": {
                "command": "npx",
                "args": ["-y", "weaviate-mcp-server"],
                "env": {
                    "WEAVIATE_URL": {
                        "description": "Weaviate instance URL",
                        "example": "http://localhost:8080",
                        "required": True,
                    },
                    "WEAVIATE_API_KEY": {
                        "description": "Weaviate API key (if auth enabled)",
                        "example": "",
                        "required": False,
                    },
                },
            }
        },
    },
    "chroma": {
        "description": "Chroma vector database",
        "servers": {
            "chroma": {
                "command": "npx",
                "args": ["-y", "chroma-mcp-server"],
                "env": {
                    "CHROMA_URL": {
                        "description": "Chroma server URL",
                        "example": "http://localhost:8000",
                        "required": True,
                    },
                },
            }
        },
    },
    "milvus": {
        "description": "Milvus vector database",
        "servers": {
            "milvus": {
                "command": "npx",
                "args": ["-y", "milvus-mcp-server"],
                "env": {
                    "MILVUS_URI": {
                        "description": "Milvus connection URI",
                        "example": "http://localhost:19530",
                        "required": True,
                    },
                },
            }
        },
    },
    # Serverless Databases
    "neon": {
        "description": "Neon serverless PostgreSQL",
        "servers": {
            "neon": {
                "command": "npx",
                "args": ["-y", "@neondatabase/mcp-server-neon@latest"],
                "env": {
                    "NEON_API_KEY": {
                        "description": "Neon API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "planetscale": {
        "description": "PlanetScale serverless MySQL",
        "servers": {
            "planetscale": {
                "command": "npx",
                "args": ["-y", "planetscale-mcp-server"],
                "env": {
                    "PLANETSCALE_TOKEN": {
                        "description": "PlanetScale service token",
                        "example": "",
                        "required": True,
                    },
                    "PLANETSCALE_ORG": {
                        "description": "PlanetScale organization",
                        "example": "my-org",
                        "required": True,
                    },
                },
            }
        },
    },
    "turso": {
        "description": "Turso edge SQLite database",
        "servers": {
            "turso": {
                "command": "npx",
                "args": ["-y", "turso-mcp-server"],
                "env": {
                    "TURSO_DATABASE_URL": {
                        "description": "Turso database URL",
                        "example": "libsql://db-org.turso.io",
                        "required": True,
                    },
                    "TURSO_AUTH_TOKEN": {
                        "description": "Turso auth token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "upstash": {
        "description": "Upstash serverless Redis & Kafka",
        "servers": {
            "upstash": {
                "command": "npx",
                "args": ["-y", "@upstash/mcp-server"],
                "env": {
                    "UPSTASH_EMAIL": {
                        "description": "Upstash account email",
                        "example": "user@example.com",
                        "required": True,
                    },
                    "UPSTASH_API_KEY": {
                        "description": "Upstash API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Payments
    "stripe": {
        "description": "Stripe payments",
        "servers": {
            "stripe": {
                "command": "npx",
                "args": ["-y", "@stripe/mcp-server"],
                "env": {
                    "STRIPE_SECRET_KEY": {
                        "description": "Stripe secret API key",
                        "example": "sk_test_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "paypal": {
        "description": "PayPal payments",
        "servers": {
            "paypal": {
                "command": "npx",
                "args": ["-y", "paypal-mcp-server"],
                "env": {
                    "PAYPAL_CLIENT_ID": {
                        "description": "PayPal client ID",
                        "example": "",
                        "required": True,
                    },
                    "PAYPAL_CLIENT_SECRET": {
                        "description": "PayPal client secret",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Authentication
    "auth0": {
        "description": "Auth0 authentication",
        "servers": {
            "auth0": {
                "command": "npx",
                "args": ["-y", "auth0-mcp-server"],
                "env": {
                    "AUTH0_DOMAIN": {
                        "description": "Auth0 domain",
                        "example": "myapp.auth0.com",
                        "required": True,
                    },
                    "AUTH0_CLIENT_ID": {
                        "description": "Auth0 client ID",
                        "example": "",
                        "required": True,
                    },
                    "AUTH0_CLIENT_SECRET": {
                        "description": "Auth0 client secret",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "clerk": {
        "description": "Clerk authentication",
        "servers": {
            "clerk": {
                "command": "npx",
                "args": ["-y", "clerk-mcp-server"],
                "env": {
                    "CLERK_SECRET_KEY": {
                        "description": "Clerk secret key",
                        "example": "sk_test_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "firebase": {
        "description": "Firebase (Auth, Firestore, Storage)",
        "servers": {
            "firebase": {
                "command": "npx",
                "args": ["-y", "firebase-mcp-server"],
                "env": {
                    "FIREBASE_SERVICE_ACCOUNT": {
                        "description": "Firebase service account JSON (base64 or path)",
                        "example": "/path/to/service-account.json",
                        "required": True,
                    },
                },
            }
        },
    },
    # Email Services
    "sendgrid": {
        "description": "SendGrid email service",
        "servers": {
            "sendgrid": {
                "command": "npx",
                "args": ["-y", "sendgrid-mcp-server"],
                "env": {
                    "SENDGRID_API_KEY": {
                        "description": "SendGrid API key",
                        "example": "SG.xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "resend": {
        "description": "Resend email service",
        "servers": {
            "resend": {
                "command": "npx",
                "args": ["-y", "resend-mcp-server"],
                "env": {
                    "RESEND_API_KEY": {
                        "description": "Resend API key",
                        "example": "re_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "mailgun": {
        "description": "Mailgun email service",
        "servers": {
            "mailgun": {
                "command": "npx",
                "args": ["-y", "mailgun-mcp-server"],
                "env": {
                    "MAILGUN_API_KEY": {
                        "description": "Mailgun API key",
                        "example": "",
                        "required": True,
                    },
                    "MAILGUN_DOMAIN": {
                        "description": "Mailgun domain",
                        "example": "mg.example.com",
                        "required": True,
                    },
                },
            }
        },
    },
    "postmark": {
        "description": "Postmark email service",
        "servers": {
            "postmark": {
                "command": "npx",
                "args": ["-y", "postmark-mcp-server"],
                "env": {
                    "POSTMARK_SERVER_TOKEN": {
                        "description": "Postmark server token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # SMS & Communications
    "twilio": {
        "description": "Twilio SMS, Voice, Video",
        "servers": {
            "twilio": {
                "command": "npx",
                "args": ["-y", "@anthropics/twilio-mcp-server"],
                "env": {
                    "TWILIO_ACCOUNT_SID": {
                        "description": "Twilio account SID",
                        "example": "ACxxxxxxxxxxxx",
                        "required": True,
                    },
                    "TWILIO_AUTH_TOKEN": {
                        "description": "Twilio auth token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "discord": {
        "description": "Discord messaging",
        "servers": {
            "discord": {
                "command": "npx",
                "args": ["-y", "discord-mcp-server"],
                "env": {
                    "DISCORD_BOT_TOKEN": {
                        "description": "Discord bot token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "telegram": {
        "description": "Telegram messaging",
        "servers": {
            "telegram": {
                "command": "npx",
                "args": ["-y", "telegram-mcp-server"],
                "env": {
                    "TELEGRAM_BOT_TOKEN": {
                        "description": "Telegram bot token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "teams": {
        "description": "Microsoft Teams",
        "servers": {
            "teams": {
                "command": "npx",
                "args": ["-y", "teams-mcp-server"],
                "env": {
                    "TEAMS_WEBHOOK_URL": {
                        "description": "Teams webhook URL",
                        "example": "https://outlook.office.com/webhook/...",
                        "required": True,
                    },
                },
            }
        },
    },
    # Deployment & Hosting
    "vercel": {
        "description": "Vercel deployment",
        "servers": {
            "vercel": {
                "command": "npx",
                "args": ["-y", "vercel-mcp-server"],
                "env": {
                    "VERCEL_TOKEN": {
                        "description": "Vercel API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "netlify": {
        "description": "Netlify deployment",
        "servers": {
            "netlify": {
                "command": "npx",
                "args": ["-y", "netlify-mcp-server"],
                "env": {
                    "NETLIFY_AUTH_TOKEN": {
                        "description": "Netlify personal access token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "cloudflare": {
        "description": "Cloudflare (Workers, Pages, R2, D1)",
        "servers": {
            "cloudflare": {
                "command": "npx",
                "args": ["-y", "@cloudflare/mcp-server-cloudflare"],
                "env": {
                    "CLOUDFLARE_API_TOKEN": {
                        "description": "Cloudflare API token",
                        "example": "",
                        "required": True,
                    },
                    "CLOUDFLARE_ACCOUNT_ID": {
                        "description": "Cloudflare account ID",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "fly": {
        "description": "Fly.io deployment",
        "servers": {
            "fly": {
                "command": "npx",
                "args": ["-y", "fly-mcp-server"],
                "env": {
                    "FLY_API_TOKEN": {
                        "description": "Fly.io API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "railway": {
        "description": "Railway deployment",
        "servers": {
            "railway": {
                "command": "npx",
                "args": ["-y", "railway-mcp-server"],
                "env": {
                    "RAILWAY_TOKEN": {
                        "description": "Railway API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "render": {
        "description": "Render deployment",
        "servers": {
            "render": {
                "command": "npx",
                "args": ["-y", "render-mcp-server"],
                "env": {
                    "RENDER_API_KEY": {
                        "description": "Render API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Project Management
    "jira": {
        "description": "Jira issue tracking",
        "servers": {
            "jira": {
                "command": "npx",
                "args": ["-y", "jira-mcp-server"],
                "env": {
                    "JIRA_URL": {
                        "description": "Jira instance URL",
                        "example": "https://mycompany.atlassian.net",
                        "required": True,
                    },
                    "JIRA_EMAIL": {
                        "description": "Jira account email",
                        "example": "user@example.com",
                        "required": True,
                    },
                    "JIRA_API_TOKEN": {
                        "description": "Jira API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "asana": {
        "description": "Asana project management",
        "servers": {
            "asana": {
                "command": "npx",
                "args": ["-y", "asana-mcp-server"],
                "env": {
                    "ASANA_ACCESS_TOKEN": {
                        "description": "Asana personal access token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "trello": {
        "description": "Trello boards",
        "servers": {
            "trello": {
                "command": "npx",
                "args": ["-y", "trello-mcp-server"],
                "env": {
                    "TRELLO_API_KEY": {
                        "description": "Trello API key",
                        "example": "",
                        "required": True,
                    },
                    "TRELLO_TOKEN": {
                        "description": "Trello token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "monday": {
        "description": "Monday.com work management",
        "servers": {
            "monday": {
                "command": "npx",
                "args": ["-y", "monday-mcp-server"],
                "env": {
                    "MONDAY_API_TOKEN": {
                        "description": "Monday.com API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "clickup": {
        "description": "ClickUp project management",
        "servers": {
            "clickup": {
                "command": "npx",
                "args": ["-y", "clickup-mcp-server"],
                "env": {
                    "CLICKUP_API_TOKEN": {
                        "description": "ClickUp API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "todoist": {
        "description": "Todoist task management",
        "servers": {
            "todoist": {
                "command": "npx",
                "args": ["-y", "@anthropics/todoist-mcp-server"],
                "env": {
                    "TODOIST_API_TOKEN": {
                        "description": "Todoist API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # CMS & Content
    "contentful": {
        "description": "Contentful headless CMS",
        "servers": {
            "contentful": {
                "command": "npx",
                "args": ["-y", "contentful-mcp-server"],
                "env": {
                    "CONTENTFUL_SPACE_ID": {
                        "description": "Contentful space ID",
                        "example": "",
                        "required": True,
                    },
                    "CONTENTFUL_ACCESS_TOKEN": {
                        "description": "Contentful access token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "sanity": {
        "description": "Sanity headless CMS",
        "servers": {
            "sanity": {
                "command": "npx",
                "args": ["-y", "sanity-mcp-server"],
                "env": {
                    "SANITY_PROJECT_ID": {
                        "description": "Sanity project ID",
                        "example": "",
                        "required": True,
                    },
                    "SANITY_TOKEN": {
                        "description": "Sanity API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "strapi": {
        "description": "Strapi headless CMS",
        "servers": {
            "strapi": {
                "command": "npx",
                "args": ["-y", "strapi-mcp-server"],
                "env": {
                    "STRAPI_URL": {
                        "description": "Strapi instance URL",
                        "example": "http://localhost:1337",
                        "required": True,
                    },
                    "STRAPI_API_TOKEN": {
                        "description": "Strapi API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Search Engines
    "algolia": {
        "description": "Algolia search",
        "servers": {
            "algolia": {
                "command": "npx",
                "args": ["-y", "algolia-mcp-server"],
                "env": {
                    "ALGOLIA_APP_ID": {
                        "description": "Algolia application ID",
                        "example": "",
                        "required": True,
                    },
                    "ALGOLIA_API_KEY": {
                        "description": "Algolia admin API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "typesense": {
        "description": "Typesense search",
        "servers": {
            "typesense": {
                "command": "npx",
                "args": ["-y", "typesense-mcp-server"],
                "env": {
                    "TYPESENSE_HOST": {
                        "description": "Typesense host",
                        "example": "localhost",
                        "required": True,
                    },
                    "TYPESENSE_API_KEY": {
                        "description": "Typesense API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "meilisearch": {
        "description": "Meilisearch search",
        "servers": {
            "meilisearch": {
                "command": "npx",
                "args": ["-y", "meilisearch-mcp-server"],
                "env": {
                    "MEILISEARCH_HOST": {
                        "description": "Meilisearch host URL",
                        "example": "http://localhost:7700",
                        "required": True,
                    },
                    "MEILISEARCH_API_KEY": {
                        "description": "Meilisearch master key",
                        "example": "",
                        "required": False,
                    },
                },
            }
        },
    },
    "elasticsearch": {
        "description": "Elasticsearch search",
        "servers": {
            "elasticsearch": {
                "command": "npx",
                "args": ["-y", "elasticsearch-mcp-server"],
                "env": {
                    "ELASTICSEARCH_URL": {
                        "description": "Elasticsearch URL",
                        "example": "http://localhost:9200",
                        "required": True,
                    },
                    "ELASTICSEARCH_API_KEY": {
                        "description": "Elasticsearch API key",
                        "example": "",
                        "required": False,
                    },
                },
            }
        },
    },
    # Analytics & Monitoring
    "segment": {
        "description": "Segment analytics",
        "servers": {
            "segment": {
                "command": "npx",
                "args": ["-y", "segment-mcp-server"],
                "env": {
                    "SEGMENT_WRITE_KEY": {
                        "description": "Segment write key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "mixpanel": {
        "description": "Mixpanel analytics",
        "servers": {
            "mixpanel": {
                "command": "npx",
                "args": ["-y", "mixpanel-mcp-server"],
                "env": {
                    "MIXPANEL_TOKEN": {
                        "description": "Mixpanel project token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "amplitude": {
        "description": "Amplitude analytics",
        "servers": {
            "amplitude": {
                "command": "npx",
                "args": ["-y", "amplitude-mcp-server"],
                "env": {
                    "AMPLITUDE_API_KEY": {
                        "description": "Amplitude API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "posthog": {
        "description": "PostHog product analytics",
        "servers": {
            "posthog": {
                "command": "npx",
                "args": ["-y", "posthog-mcp-server"],
                "env": {
                    "POSTHOG_API_KEY": {
                        "description": "PostHog API key",
                        "example": "phx_xxxxxxxxxxxx",
                        "required": True,
                    },
                    "POSTHOG_HOST": {
                        "description": "PostHog host URL",
                        "example": "https://app.posthog.com",
                        "required": False,
                    },
                },
            }
        },
    },
    "datadog": {
        "description": "Datadog monitoring",
        "servers": {
            "datadog": {
                "command": "npx",
                "args": ["-y", "datadog-mcp-server"],
                "env": {
                    "DATADOG_API_KEY": {
                        "description": "Datadog API key",
                        "example": "",
                        "required": True,
                    },
                    "DATADOG_APP_KEY": {
                        "description": "Datadog application key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "newrelic": {
        "description": "New Relic observability",
        "servers": {
            "newrelic": {
                "command": "npx",
                "args": ["-y", "newrelic-mcp-server"],
                "env": {
                    "NEW_RELIC_API_KEY": {
                        "description": "New Relic API key",
                        "example": "",
                        "required": True,
                    },
                    "NEW_RELIC_ACCOUNT_ID": {
                        "description": "New Relic account ID",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "grafana": {
        "description": "Grafana dashboards",
        "servers": {
            "grafana": {
                "command": "npx",
                "args": ["-y", "grafana-mcp-server"],
                "env": {
                    "GRAFANA_URL": {
                        "description": "Grafana URL",
                        "example": "http://localhost:3000",
                        "required": True,
                    },
                    "GRAFANA_API_KEY": {
                        "description": "Grafana API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "prometheus": {
        "description": "Prometheus metrics",
        "servers": {
            "prometheus": {
                "command": "npx",
                "args": ["-y", "prometheus-mcp-server"],
                "env": {
                    "PROMETHEUS_URL": {
                        "description": "Prometheus server URL",
                        "example": "http://localhost:9090",
                        "required": True,
                    },
                },
            }
        },
    },
    # E-commerce
    "shopify": {
        "description": "Shopify e-commerce",
        "servers": {
            "shopify": {
                "command": "npx",
                "args": ["-y", "@anthropics/shopify-mcp-server"],
                "env": {
                    "SHOPIFY_STORE_URL": {
                        "description": "Shopify store URL",
                        "example": "mystore.myshopify.com",
                        "required": True,
                    },
                    "SHOPIFY_ACCESS_TOKEN": {
                        "description": "Shopify admin API access token",
                        "example": "shpat_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    # AI Models & Services
    "anthropic": {
        "description": "Anthropic Claude API",
        "servers": {
            "anthropic": {
                "command": "npx",
                "args": ["-y", "anthropic-mcp-server"],
                "env": {
                    "ANTHROPIC_API_KEY": {
                        "description": "Anthropic API key",
                        "example": "sk-ant-xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "groq": {
        "description": "Groq fast inference",
        "servers": {
            "groq": {
                "command": "npx",
                "args": ["-y", "groq-mcp-server"],
                "env": {
                    "GROQ_API_KEY": {
                        "description": "Groq API key",
                        "example": "gsk_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "mistral": {
        "description": "Mistral AI",
        "servers": {
            "mistral": {
                "command": "npx",
                "args": ["-y", "mistral-mcp-server"],
                "env": {
                    "MISTRAL_API_KEY": {
                        "description": "Mistral API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "cohere": {
        "description": "Cohere AI",
        "servers": {
            "cohere": {
                "command": "npx",
                "args": ["-y", "cohere-mcp-server"],
                "env": {
                    "COHERE_API_KEY": {
                        "description": "Cohere API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "replicate": {
        "description": "Replicate ML models",
        "servers": {
            "replicate": {
                "command": "npx",
                "args": ["-y", "replicate-mcp-server"],
                "env": {
                    "REPLICATE_API_TOKEN": {
                        "description": "Replicate API token",
                        "example": "r8_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "huggingface": {
        "description": "Hugging Face models",
        "servers": {
            "huggingface": {
                "command": "npx",
                "args": ["-y", "huggingface-mcp-server"],
                "env": {
                    "HUGGINGFACE_TOKEN": {
                        "description": "Hugging Face access token",
                        "example": "hf_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "together": {
        "description": "Together AI inference",
        "servers": {
            "together": {
                "command": "npx",
                "args": ["-y", "together-mcp-server"],
                "env": {
                    "TOGETHER_API_KEY": {
                        "description": "Together AI API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "perplexity": {
        "description": "Perplexity AI search",
        "servers": {
            "perplexity": {
                "command": "npx",
                "args": ["-y", "perplexity-mcp-server"],
                "env": {
                    "PERPLEXITY_API_KEY": {
                        "description": "Perplexity API key",
                        "example": "pplx-xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    # AI Search & Scraping
    "tavily": {
        "description": "Tavily AI search",
        "servers": {
            "tavily": {
                "command": "npx",
                "args": ["-y", "tavily-mcp-server"],
                "env": {
                    "TAVILY_API_KEY": {
                        "description": "Tavily API key",
                        "example": "tvly-xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "exa": {
        "description": "Exa AI search",
        "servers": {
            "exa": {
                "command": "npx",
                "args": ["-y", "@anthropics/exa-mcp-server"],
                "env": {
                    "EXA_API_KEY": {
                        "description": "Exa API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "serper": {
        "description": "Serper Google search API",
        "servers": {
            "serper": {
                "command": "npx",
                "args": ["-y", "serper-mcp-server"],
                "env": {
                    "SERPER_API_KEY": {
                        "description": "Serper API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "firecrawl": {
        "description": "Firecrawl web scraping",
        "servers": {
            "firecrawl": {
                "command": "npx",
                "args": ["-y", "firecrawl-mcp-server"],
                "env": {
                    "FIRECRAWL_API_KEY": {
                        "description": "Firecrawl API key",
                        "example": "fc-xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "browserbase": {
        "description": "Browserbase cloud browsers",
        "servers": {
            "browserbase": {
                "command": "npx",
                "args": ["-y", "@anthropics/browserbase-mcp-server"],
                "env": {
                    "BROWSERBASE_API_KEY": {
                        "description": "Browserbase API key",
                        "example": "",
                        "required": True,
                    },
                    "BROWSERBASE_PROJECT_ID": {
                        "description": "Browserbase project ID",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "apify": {
        "description": "Apify web scraping & automation",
        "servers": {
            "apify": {
                "command": "npx",
                "args": ["-y", "apify-mcp-server"],
                "env": {
                    "APIFY_TOKEN": {
                        "description": "Apify API token",
                        "example": "apify_api_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    # Code Execution
    "e2b": {
        "description": "E2B code sandbox",
        "servers": {
            "e2b": {
                "command": "npx",
                "args": ["-y", "e2b-mcp-server"],
                "env": {
                    "E2B_API_KEY": {
                        "description": "E2B API key",
                        "example": "e2b_xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "modal": {
        "description": "Modal serverless compute",
        "servers": {
            "modal": {
                "command": "npx",
                "args": ["-y", "modal-mcp-server"],
                "env": {
                    "MODAL_TOKEN_ID": {
                        "description": "Modal token ID",
                        "example": "",
                        "required": True,
                    },
                    "MODAL_TOKEN_SECRET": {
                        "description": "Modal token secret",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Data Warehouses
    "snowflake": {
        "description": "Snowflake data warehouse",
        "servers": {
            "snowflake": {
                "command": "npx",
                "args": ["-y", "snowflake-mcp-server"],
                "env": {
                    "SNOWFLAKE_ACCOUNT": {
                        "description": "Snowflake account identifier",
                        "example": "abc12345.us-east-1",
                        "required": True,
                    },
                    "SNOWFLAKE_USER": {
                        "description": "Snowflake username",
                        "example": "",
                        "required": True,
                    },
                    "SNOWFLAKE_PASSWORD": {
                        "description": "Snowflake password",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "bigquery": {
        "description": "Google BigQuery",
        "servers": {
            "bigquery": {
                "command": "npx",
                "args": ["-y", "bigquery-mcp-server"],
                "env": {
                    "GOOGLE_PROJECT_ID": {
                        "description": "Google Cloud project ID",
                        "example": "",
                        "required": True,
                    },
                    "GOOGLE_APPLICATION_CREDENTIALS": {
                        "description": "Path to service account JSON",
                        "example": "/path/to/credentials.json",
                        "required": True,
                    },
                },
            }
        },
    },
    "databricks": {
        "description": "Databricks data platform",
        "servers": {
            "databricks": {
                "command": "npx",
                "args": ["-y", "databricks-mcp-server"],
                "env": {
                    "DATABRICKS_HOST": {
                        "description": "Databricks workspace URL",
                        "example": "https://xxx.cloud.databricks.com",
                        "required": True,
                    },
                    "DATABRICKS_TOKEN": {
                        "description": "Databricks access token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # CI/CD
    "circleci": {
        "description": "CircleCI pipelines",
        "servers": {
            "circleci": {
                "command": "npx",
                "args": ["-y", "circleci-mcp-server"],
                "env": {
                    "CIRCLECI_TOKEN": {
                        "description": "CircleCI personal API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "buildkite": {
        "description": "Buildkite CI/CD",
        "servers": {
            "buildkite": {
                "command": "npx",
                "args": ["-y", "buildkite-mcp-server"],
                "env": {
                    "BUILDKITE_TOKEN": {
                        "description": "Buildkite API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Infrastructure as Code
    "terraform": {
        "description": "Terraform infrastructure",
        "servers": {
            "terraform": {
                "command": "npx",
                "args": ["-y", "terraform-mcp-server"],
                "env": {
                    "TF_CLOUD_TOKEN": {
                        "description": "Terraform Cloud token (optional)",
                        "example": "",
                        "required": False,
                    },
                },
            }
        },
    },
    "pulumi": {
        "description": "Pulumi infrastructure",
        "servers": {
            "pulumi": {
                "command": "npx",
                "args": ["-y", "pulumi-mcp-server"],
                "env": {
                    "PULUMI_ACCESS_TOKEN": {
                        "description": "Pulumi access token",
                        "example": "pul-xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    # Secrets Management
    "vault": {
        "description": "HashiCorp Vault secrets",
        "servers": {
            "vault": {
                "command": "npx",
                "args": ["-y", "vault-mcp-server"],
                "env": {
                    "VAULT_ADDR": {
                        "description": "Vault server address",
                        "example": "http://localhost:8200",
                        "required": True,
                    },
                    "VAULT_TOKEN": {
                        "description": "Vault token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "doppler": {
        "description": "Doppler secrets management",
        "servers": {
            "doppler": {
                "command": "npx",
                "args": ["-y", "doppler-mcp-server"],
                "env": {
                    "DOPPLER_TOKEN": {
                        "description": "Doppler service token",
                        "example": "dp.st.xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    # Spreadsheets & Databases
    "airtable": {
        "description": "Airtable spreadsheet database",
        "servers": {
            "airtable": {
                "command": "npx",
                "args": ["-y", "airtable-mcp-server"],
                "env": {
                    "AIRTABLE_API_KEY": {
                        "description": "Airtable API key or personal access token",
                        "example": "pat.xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "google-sheets": {
        "description": "Google Sheets",
        "servers": {
            "google-sheets": {
                "command": "npx",
                "args": ["-y", "google-sheets-mcp-server"],
                "env": {
                    "GOOGLE_SERVICE_ACCOUNT": {
                        "description": "Google service account JSON (base64)",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Calendar
    "google-calendar": {
        "description": "Google Calendar",
        "servers": {
            "google-calendar": {
                "command": "npx",
                "args": ["-y", "google-calendar-mcp-server"],
                "env": {
                    "GOOGLE_CALENDAR_CREDENTIALS": {
                        "description": "Google OAuth credentials JSON",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # CRM
    "hubspot": {
        "description": "HubSpot CRM",
        "servers": {
            "hubspot": {
                "command": "npx",
                "args": ["-y", "hubspot-mcp-server"],
                "env": {
                    "HUBSPOT_ACCESS_TOKEN": {
                        "description": "HubSpot private app access token",
                        "example": "pat-xxxxxxxxxxxx",
                        "required": True,
                    },
                },
            }
        },
    },
    "salesforce": {
        "description": "Salesforce CRM",
        "servers": {
            "salesforce": {
                "command": "npx",
                "args": ["-y", "salesforce-mcp-server"],
                "env": {
                    "SALESFORCE_INSTANCE_URL": {
                        "description": "Salesforce instance URL",
                        "example": "https://mycompany.salesforce.com",
                        "required": True,
                    },
                    "SALESFORCE_ACCESS_TOKEN": {
                        "description": "Salesforce access token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Documentation
    "confluence": {
        "description": "Atlassian Confluence",
        "servers": {
            "confluence": {
                "command": "npx",
                "args": ["-y", "confluence-mcp-server"],
                "env": {
                    "CONFLUENCE_URL": {
                        "description": "Confluence instance URL",
                        "example": "https://mycompany.atlassian.net/wiki",
                        "required": True,
                    },
                    "CONFLUENCE_EMAIL": {
                        "description": "Confluence account email",
                        "example": "user@example.com",
                        "required": True,
                    },
                    "CONFLUENCE_API_TOKEN": {
                        "description": "Confluence API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Git Hosting
    "bitbucket": {
        "description": "Bitbucket repositories",
        "servers": {
            "bitbucket": {
                "command": "npx",
                "args": ["-y", "bitbucket-mcp-server"],
                "env": {
                    "BITBUCKET_USERNAME": {
                        "description": "Bitbucket username",
                        "example": "",
                        "required": True,
                    },
                    "BITBUCKET_APP_PASSWORD": {
                        "description": "Bitbucket app password",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Azure
    "azure": {
        "description": "Microsoft Azure",
        "servers": {
            "azure": {
                "command": "npx",
                "args": ["-y", "azure-mcp-server"],
                "env": {
                    "AZURE_SUBSCRIPTION_ID": {
                        "description": "Azure subscription ID",
                        "example": "",
                        "required": True,
                    },
                    "AZURE_TENANT_ID": {
                        "description": "Azure tenant ID",
                        "example": "",
                        "required": True,
                    },
                    "AZURE_CLIENT_ID": {
                        "description": "Azure client/app ID",
                        "example": "",
                        "required": True,
                    },
                    "AZURE_CLIENT_SECRET": {
                        "description": "Azure client secret",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Storage
    "dropbox": {
        "description": "Dropbox storage",
        "servers": {
            "dropbox": {
                "command": "npx",
                "args": ["-y", "dropbox-mcp-server"],
                "env": {
                    "DROPBOX_ACCESS_TOKEN": {
                        "description": "Dropbox access token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Message Queues
    "rabbitmq": {
        "description": "RabbitMQ message broker",
        "servers": {
            "rabbitmq": {
                "command": "npx",
                "args": ["-y", "rabbitmq-mcp-server"],
                "env": {
                    "RABBITMQ_URL": {
                        "description": "RabbitMQ connection URL",
                        "example": "amqp://guest:guest@localhost:5672",
                        "required": True,
                    },
                },
            }
        },
    },
    "kafka": {
        "description": "Apache Kafka streaming",
        "servers": {
            "kafka": {
                "command": "npx",
                "args": ["-y", "kafka-mcp-server"],
                "env": {
                    "KAFKA_BROKERS": {
                        "description": "Kafka broker addresses",
                        "example": "localhost:9092",
                        "required": True,
                    },
                },
            }
        },
    },
    # Graph Databases
    "neo4j": {
        "description": "Neo4j graph database",
        "servers": {
            "neo4j": {
                "command": "npx",
                "args": ["-y", "neo4j-mcp-server"],
                "env": {
                    "NEO4J_URI": {
                        "description": "Neo4j connection URI",
                        "example": "bolt://localhost:7687",
                        "required": True,
                    },
                    "NEO4J_USER": {
                        "description": "Neo4j username",
                        "example": "neo4j",
                        "required": True,
                    },
                    "NEO4J_PASSWORD": {
                        "description": "Neo4j password",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Automation & Integration
    "zapier": {
        "description": "Zapier automation",
        "servers": {
            "zapier": {
                "command": "npx",
                "args": ["-y", "zapier-mcp-server"],
                "env": {
                    "ZAPIER_NLA_API_KEY": {
                        "description": "Zapier NLA API key",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    "make": {
        "description": "Make (Integromat) automation",
        "servers": {
            "make": {
                "command": "npx",
                "args": ["-y", "make-mcp-server"],
                "env": {
                    "MAKE_API_TOKEN": {
                        "description": "Make API token",
                        "example": "",
                        "required": True,
                    },
                },
            }
        },
    },
    # Sequential Thinking (MCP official)
    "sequential-thinking": {
        "description": "Sequential thinking for complex reasoning",
        "servers": {
            "sequential-thinking": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
                "env": {},
            }
        },
    },
    # Everything (Windows file search)
    "everything": {
        "description": "Everything file search (Windows)",
        "servers": {
            "everything": {
                "command": "npx",
                "args": ["-y", "@anthropics/everything-mcp-server"],
                "env": {},
            }
        },
    },
    # Git
    "git": {
        "description": "Git repository operations",
        "servers": {
            "git": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-git"],
                "env": {},
            }
        },
    },
}

# Common tech stack presets
STACK_PRESETS = {
    "web-basic": {
        "description": "Basic web development",
        "stacks": ["fetch", "memory", "github", "git"],
    },
    "fullstack-postgres": {
        "description": "Full-stack with PostgreSQL",
        "stacks": ["fetch", "memory", "github", "postgres", "docker", "git"],
    },
    "fullstack-mongo": {
        "description": "Full-stack with MongoDB",
        "stacks": ["fetch", "memory", "github", "mongodb", "docker", "git"],
    },
    "fullstack-supabase": {
        "description": "Full-stack with Supabase",
        "stacks": ["fetch", "memory", "github", "supabase", "git"],
    },
    "serverless": {
        "description": "Serverless stack (Vercel, Neon, Upstash)",
        "stacks": ["fetch", "memory", "github", "vercel", "neon", "upstash", "git"],
    },
    "data-science": {
        "description": "Data science workflow",
        "stacks": ["memory", "postgres", "s3", "qdrant", "bigquery"],
    },
    "devops": {
        "description": "DevOps and infrastructure",
        "stacks": ["github", "docker", "kubernetes", "aws", "sentry", "terraform"],
    },
    "ai-agent": {
        "description": "AI agent development",
        "stacks": ["memory", "fetch", "openai", "qdrant", "github", "e2b", "firecrawl"],
    },
    "ai-search": {
        "description": "AI-powered search applications",
        "stacks": ["memory", "fetch", "tavily", "exa", "qdrant", "openai"],
    },
    "saas": {
        "description": "SaaS application stack",
        "stacks": ["github", "supabase", "stripe", "resend", "posthog", "sentry"],
    },
    "startup": {
        "description": "Startup essentials",
        "stacks": ["github", "vercel", "supabase", "stripe", "resend", "slack", "linear"],
    },
    "enterprise": {
        "description": "Enterprise integrations",
        "stacks": ["github", "jira", "confluence", "slack", "datadog", "vault"],
    },
    "ecommerce": {
        "description": "E-commerce stack",
        "stacks": ["github", "shopify", "stripe", "sendgrid", "algolia", "segment"],
    },
    "marketing": {
        "description": "Marketing & analytics",
        "stacks": ["hubspot", "segment", "mixpanel", "posthog", "mailgun", "slack"],
    },
    "ml-ops": {
        "description": "ML operations pipeline",
        "stacks": ["github", "aws", "s3", "snowflake", "databricks", "huggingface"],
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
    # Check built-in stacks first, then custom
    all_stacks = get_all_available_stacks(project_path)

    if stack_name not in all_stacks:
        return {"success": False, "error": f"Unknown stack: {stack_name}"}

    stack = all_stacks[stack_name]
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


def add_custom_stack(
    name: str,
    description: str,
    command: str,
    args: list = None,
    env_vars: dict = None,
    project_path: Path = None,
) -> dict:
    """Add a custom MCP server/stack.

    Args:
        name: Name for the custom stack/server
        description: Description of what it does
        command: Command to run (e.g., "npx", "docker", "python")
        args: Command arguments
        env_vars: Dict of env var definitions with description, example, required
        project_path: Project path

    Returns:
        Dict with 'success' and info
    """
    config = load_stack_config(project_path)

    if "custom_stacks" not in config:
        config["custom_stacks"] = {}

    # Build env var config
    env_config = {}
    if env_vars:
        for var_name, var_info in env_vars.items():
            if isinstance(var_info, str):
                # Simple format: just description
                env_config[var_name] = {
                    "description": var_info,
                    "example": "",
                    "required": True,
                }
            else:
                # Full format
                env_config[var_name] = var_info

    config["custom_stacks"][name] = {
        "description": description,
        "servers": {
            name: {
                "command": command,
                "args": args or [],
                "env": env_config,
            }
        },
    }

    save_stack_config(config, project_path)

    return {"success": True, "name": name}


def remove_custom_stack(name: str, project_path: Path = None) -> bool:
    """Remove a custom MCP stack.

    Args:
        name: Name of the custom stack to remove
        project_path: Project path

    Returns:
        True if removed, False if not found
    """
    config = load_stack_config(project_path)

    if "custom_stacks" not in config:
        return False

    if name not in config["custom_stacks"]:
        return False

    del config["custom_stacks"][name]
    save_stack_config(config, project_path)

    # Also remove from MCP config if present
    mcp.remove_mcp_server(name, project_path)

    return True


def list_custom_stacks(project_path: Path = None) -> dict:
    """List all custom MCP stacks.

    Returns:
        Dict of custom stack name -> info
    """
    config = load_stack_config(project_path)
    return config.get("custom_stacks", {})


def get_all_available_stacks(project_path: Path = None) -> dict:
    """Get all available stacks (built-in + custom).

    Returns:
        Dict combining TECH_STACK_SERVERS and custom stacks
    """
    # Start with built-in stacks
    all_stacks = dict(TECH_STACK_SERVERS)

    # Add custom stacks
    custom = list_custom_stacks(project_path)
    all_stacks.update(custom)

    return all_stacks
