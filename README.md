# UAT Agent

An AI-powered User Acceptance Testing (UAT) automation project that uses Playwright MCP and AI agents to execute test scenarios against a sample Issue Tracker application.

The project demonstrates how AI agents can interpret UAT instructions, interact with a web application through browser automation, validate expected outcomes, and identify potential defects.

## 1. Project Overview

The project consists of two main components:

### Issue Tracker Application

A sample web application built with FastAPI, SQLite, and server-rendered HTML templates.

It provides functionality for:

- User registration and authentication.
- Creating and managing issues.
- Viewing issue details.
- Updating issue status and priority.
- Searching and listing issues.
- Exposing REST API endpoints.

### UAT Automation Agent

The UAT automation implementation is located in `app/agents/`.

It uses AI agents and Playwright MCP to interpret UAT instructions, execute browser interactions, verify expected outcomes, and identify potential defects.

## 2. Project Structure

```text
.
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py
│   ├── routes.py
│   ├── templates/
│   ├── static/
│   │
│   └── agents/                 # UAT automation implementation
│       ├── instructions/       # Sample UAT instruction files
│       ├── prompts/            # AI agent prompts
│       ├── values.yaml         # Test values supplied to instructions
│       ├── runs/               # Generated execution results and evidence
│       └── main.py             # UAT agent entry point
│
├── .env                        # Environment variables and credentials
├── .env.example                # Example environment configuration
├── pyproject.toml
├── uv.lock
└── README.md
```

### Important Directories and Files

- **`app/agents/instructions/`** – Contains sample UAT instruction files defining business scenarios, test procedures, and expected outcomes.
- **`app/agents/prompts/`** – Contains prompts defining the responsibilities and behaviour of the AI agents.
- **`app/agents/values.yaml`** – Contains test values used to populate placeholders in the instruction files.
- **`app/agents/runs/`** – Stores generated UAT execution results and supporting evidence.
- **`app/agents/main.py`** – Entry point for executing the UAT automation workflow.

## 3. Requirements

- Python 3.12 or a compatible version supported by the project dependencies.
- [uv](https://docs.astral.sh/uv/) installed.
- An OpenAI API key.
- The Issue Tracker application running and accessible.
- The required Playwright MCP server configured for the agent.

## 4. Installation

Clone the repository:

```bash
git clone <repository-url>
cd <project-directory>
```

Install dependencies:

```bash
uv sync
```

Start the Issue Tracker application and ensure it is accessible before executing UAT tests.

For a locally running application, the default address may be:

```text
http://localhost:8000
```

## 5. Environment Configuration

Create a `.env` file in the project root.

```env
SESSION_SECRET=your-session-secret
DEFAULT_TIMEOUT_SECONDS=30

OPENAI_API_KEY=your-openai-api-key

ORCHESTRATOR_MODEL=your-orchestrator-model
EXECUTOR_MODEL=your-executor-model

APP_EMAIL=your-application-login-email
APP_PASSWORD=your-application-login-password
```

### Environment Variables

| Variable                  | Description                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| `SESSION_SECRET`          | Secret used to sign application session cookies.                                           |
| `DEFAULT_TIMEOUT_SECONDS` | Default timeout for browser automation operations, in seconds.                             |
| `OPENAI_API_KEY`          | API key used to access OpenAI models.                                                      |
| `ORCHESTRATOR_MODEL`      | Model used by the orchestrator agent to coordinate UAT execution.                          |
| `EXECUTOR_MODEL`          | Model used by the executor agent to perform browser interactions.                          |
| `APP_EMAIL`               | Email address of the account used by the agent to log in to the Issue Tracker application. |
| `APP_PASSWORD`            | Password of the account used by the agent to log in to the Issue Tracker application.      |

**Important:**

- `APP_EMAIL` and `APP_PASSWORD` are the Issue Tracker application login credentials, not OpenAI credentials.
- Register an account in the Issue Tracker application and configure its credentials here.
- Never commit `.env` to version control.
- Keep `.env.example` updated with variable names but without actual credentials.

## 6. Running UAT Tests

UAT execution is initiated through `app/agents/main.py`.

The command accepts two arguments:

- `--instructions`: Path to the UAT instruction file.
- `--values`: Path to the YAML file containing values used to populate instruction placeholders.

Run the command from the project root:

```bash
uv run app/agents/main.py \
  --instructions app/agents/instructions/issues/create_issue.md \
  --values app/agents/values.yaml
```

Adjust the instruction path to execute a different UAT scenario.

### Execution Process

1. Environment variables are loaded from `.env`.
2. The specified UAT instruction file is loaded.
3. The supplied YAML values file is read.
4. Values are used to populate the relevant instruction placeholders.
5. The orchestrator agent interprets the instructions and coordinates execution.
6. The executor agent interacts with the Issue Tracker through Playwright MCP.
7. The agent verifies the application's behaviour against the expected outcomes.
8. Execution results and supporting evidence are generated under `app/agents/runs/`.

## 7. Creating New UAT Scenarios

To introduce a new UAT scenario:

1. Create an instruction file under `app/agents/instructions/`.
2. Define the business scenario, preconditions, test steps, and expected results.
3. Identify values that should be supplied dynamically.
4. Add the corresponding values to `app/agents/values.yaml`.
5. Execute the agent using the relevant instruction file and values file.

Example:

```text
app/agents/
├── instructions/
│   └── issues/
│       ├── create_issue.md
│       ├── update_issue.md
│       └── search_issues.md
├── prompts/
├── values.yaml
├── runs/
└── main.py
```

Keeping instructions separate from test values makes scenarios easier to maintain and reuse.

## 8. Test Results and Evidence

Each execution generates output under `app/agents/runs/`.

Depending on the configured agents and evidence collection implementation, this may include:

- Test execution summaries.
- Individual test case results.
- Pass/fail status.
- Actual versus expected outcomes.
- Screenshots and browser evidence.
- Error details and identified defects.

## 9. Security Considerations

- Never commit API keys, passwords, or session secrets.
- Keep `.env` out of version control.
- Use dedicated test accounts rather than personal or production accounts.
- Avoid running destructive UAT scenarios against production systems.
- Restrict access to generated execution evidence if it contains sensitive application data.

## 10. Project Purpose

This project demonstrates the practical application of Model Context Protocol (MCP), browser automation, and AI agents in software testing.

It explores how AI agents can move beyond generating test cases to executing user workflows, validating application behaviour, and producing evidence-based UAT results.

The Issue Tracker is intentionally a sample application, allowing the automation architecture and agent behaviour to be demonstrated without depending on a complex production system.
