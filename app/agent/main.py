"""
UAT QA agent runner (LangChain Deep Agents + Playwright MCP).

Usage:
  uv run main.py --instructions instructions/create_issue/create_issue.md 
  --values instructions/create_issue/values.yaml

The instruction file can be .md/.txt (used as is) or .docx/.pdf/.xlsx/.pptx
(converted to markdown with markitdown).
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlparse
import uuid
from dotenv import load_dotenv
from langchain_core.tools import tool
import yaml
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from deepagents.backends import FilesystemBackend
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

ROOT = Path(__file__).parent
load_dotenv()

DEFAULT_TIMEOUT_SECONDS = os.environ.get("DEFAULT_TIMEOUT_SECONDS", 900)
SECRET_WORDS = ("PASSWORD", "PIN", "SECRET", "TOKEN", "KEY")
MAX_FIELD_ATTEMPTS = 3
RECURSION_LIMIT = 150
ORCHESTRATOR_PROMPT = (
    "You coordinate one UAT test run. Your only job is to delegate the test to "
    "the 'browser-executor' subagent using the task tool. The full instructions "
    "are saved in the file /instructions.md. Give the subagent exactly this task: "
    "'Read /instructions.md completely and follow it exactly.' Do not summarize, "
    "edit or add to the instructions. When the subagent finishes, reply with its "
    "report unchanged."
)

def make_tools(run_dir: Path):
    attempts: dict[str, int] = {}

    @tool
    def record_field_attempt(field: str, value_tried: str, error_message: str) -> str:
        """Call BEFORE every adjustment of a field after a validation error.
        Returns whether another attempt is allowed."""
        attempts[field] = attempts.get(field, 0) + 1
        n = attempts[field]
        with open(run_dir / "attempts.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"field": field, "attempt": n,
                                "value": value_tried, "error": error_message}) + "\n")
        if n > MAX_FIELD_ATTEMPTS:
            return ("LIMIT REACHED. Do not adjust this field again. "
                    "Record the test as BLOCKED and finish.")
        return f"OK. Attempt {n} of {MAX_FIELD_ATTEMPTS} recorded."

    @tool
    def save_report(report_markdown: str) -> str:
        """Save the final test report (full text)."""
        (run_dir / "report.md").write_text(report_markdown, encoding="utf-8")
        return "Report saved."

    return [record_field_attempt, save_report]

def build_values(values_path: Path, run_id: str) -> dict:
    values = {}
    if values_path.exists():
        values = yaml.safe_load(values_path.read_text(encoding="utf-8")) or {}
    values = {k: str(v) for k, v in values.items()}

    values.setdefault("RUN_ID", run_id)
    values.setdefault("LOGIN_URL", os.environ.get("LOGIN_URL"))
    values.setdefault("API_URL", os.environ.get("API_URL"))

    # Fresh, unique emails on every run (only if not set by hand)
    local = values.get("EMAIL_BASE_LOCAL") or os.environ.get("EMAIL_BASE_LOCAL")
    domain = values.get("EMAIL_DOMAIN") or os.environ.get("EMAIL_DOMAIN")
    if local and domain:
        rid = values["RUN_ID"]
        values.setdefault("EMAIL_DUPLICATE", f"{local}+dup{rid}@{domain}")
        values.setdefault("EMAIL_UNIQUE_1", f"{local}+a{rid}@{domain}")
        values.setdefault("EMAIL_UNIQUE_2", f"{local}+b{rid}@{domain}")
    return values

def render(doc: str, values: dict) -> tuple[str, set[str]]:
    """Replace {{KEY}} using values.yaml first, then environment/.env."""
    missing: set[str] = set()
    secrets: set[str] = set()

    def sub(match):
        key = match.group(1)
        val = values.get(key, os.environ.get(key))
        if val is None or val == "":
            missing.add(key)
            return match.group(0)
        if any(w in key.upper() for w in SECRET_WORDS):
            secrets.add(val)
        return val

    out = re.sub(r"\{\{(\w+)\}\}", sub, doc)
    if missing:
        sys.exit(f"No value found for: {sorted(missing)}. "
                 "Add them to values.yaml (or .env for secrets).")
    return out, secrets

def to_markdown(path: Path) -> str:
    if path.suffix.lower() in (".md", ".txt"):
        return path.read_text(encoding="utf-8")
    from markitdown import MarkItDown
    return MarkItDown().convert(str(path)).text_content

def extract_assertions(doc: str) -> list[str]:
    return re.findall(r"<!--\s*assert-contains:\s*(.*?)\s*-->", doc)

def get_model_name(env_var: str) -> str:
    name = os.environ.get(env_var)
    if not name:
        sys.exit(f"{env_var} is not set in .env (example: openai:gpt-4.1-mini)")
    return name

def allowed_origins(values: dict) -> str:
    origins = set()
    for key, val in values.items():
        if key.endswith("_URL"):
            p = urlparse(val)
            if p.scheme and p.netloc:
                origins.add(f"{p.scheme}://{p.netloc}")
    return ";".join(sorted(origins))

def mask(text: str, secrets: set[str]) -> str:
    for s in secrets:
        text = text.replace(s, "****")
    return text

def text_of(content) -> str:
    """Gemini and others may return a list of content parts."""
    if isinstance(content, str):
        return content
    parts = []
    for part in content or []:
        parts.append(part.get("text", "") if isinstance(part, dict) else str(part))
    return "".join(parts)

def build_agent(no_orchestrator: bool, tools: list, run_dir: Path, qa_prompt: str):
    backend = FilesystemBackend(root_dir=str(run_dir), virtual_mode=True)
    executor_model = init_chat_model(get_model_name("EXECUTOR_MODEL"), temperature=0)

    if no_orchestrator:
        return create_deep_agent(
            model=executor_model, tools=tools,
            system_prompt=qa_prompt, backend=backend)

    orchestrator_model = init_chat_model(get_model_name("ORCHESTRATOR_MODEL"), temperature=0)
    executor = {
        "name": "browser-executor",
        "description": "Runs the UAT instructions in the browser and returns a report.",
        "system_prompt": qa_prompt,
        "tools": tools,
        "model": executor_model,
    }
    return create_deep_agent(
        model=orchestrator_model, tools=[],
        system_prompt=ORCHESTRATOR_PROMPT,
        subagents=[executor], backend=backend)

async def run(args) -> None:
    doc_path = Path(args.instructions)
    id = uuid.uuid4().hex[:8]
    values = build_values(Path(args.values), run_id=id)
    doc, secrets = render(to_markdown(doc_path), values)
    assertions = extract_assertions(doc)
    qa_prompt = (ROOT / "prompts" / "qa_agent.md").read_text(encoding="utf-8")
    models = [get_model_name("EXECUTOR_MODEL")]
    run_dir = ROOT / "runs" / id
    shots = run_dir / "evidence"
    shots.mkdir(parents=True, exist_ok=True)
    instructions_file = run_dir / "instructions.md"
    instructions_file.write_text(doc, encoding="utf-8")

    pw_args = ["@playwright/mcp@latest", "--output-dir", str(shots)]
    origins = allowed_origins(values)
    if origins:
        pw_args += ["--allowed-origins", origins]

    client = MultiServerMCPClient({
        "playwright": {"transport": "stdio", "command": "npx", "args": pw_args}
    })

    started = time.time()
    final_state = None
    print(f"Run folder: {run_dir}")
    print(f"Models: {', '.join(models)} | allowed origins: {origins}")

    async with client.session("playwright") as session:
        browser_tools = await load_mcp_tools(session)
        tools = browser_tools + make_tools(run_dir)
        agent = build_agent(args.no_orchestrator, tools, run_dir, qa_prompt)

        if args.no_orchestrator:
            user_msg = "Execute this UAT test exactly as written.\n\n" + doc
        else:
            user_msg = ("Run the test. Delegate to 'browser-executor' with the task: "
                        "'Read /instructions.md completely and follow it exactly.'")

        async def stream():
            nonlocal final_state
            async for state in agent.astream(
                {"messages": [{"role": "user", "content": user_msg}]},
                config={"recursion_limit": RECURSION_LIMIT},
                stream_mode="values",
            ):
                final_state = state
                last = state["messages"][-1]
                for call in getattr(last, "tool_calls", None) or []:
                    print(f"  tool: {call['name']}")

        try:
            await asyncio.wait_for(stream(), timeout=args.timeout)
        except asyncio.TimeoutError:
            print(f"TIMEOUT after {args.timeout}s")
        except Exception as e:  # keep partial evidence
            print(f"ERROR: {type(e).__name__}: {e}")

    instructions_file.write_text(mask(doc, secrets), encoding="utf-8")

    final_text = ""
    if final_state:
        final_text = mask(text_of(final_state["messages"][-1].content), secrets)
    (run_dir / "final_answer.md").write_text(final_text, encoding="utf-8")

    report_file = run_dir / "report.md"
    report_text = report_file.read_text(encoding="utf-8") if report_file.exists() else ""
    haystack = report_text + "\n" + final_text
    results = {
        "id": id,
        "instructions": str(doc_path),
        "models": models,
        "duration_seconds": round(time.time() - started),
        "report_saved": report_file.exists(),
        "screenshots": len([p for p in shots.iterdir()
                            if p.suffix.lower() in (".png", ".jpg", ".jpeg")]),
        "exact_text_checks": [{"text": a, "found": a in haystack} for a in assertions],
    }
    (run_dir / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\n=== Result ===")
    print(json.dumps(results, indent=2))
    print(f"\nReport: {report_file if report_file.exists() else 'NOT SAVED (see final_answer.md)'}")

def main():
    ap = argparse.ArgumentParser(description="Run a UAT instruction file with a QA agent")
    ap.add_argument("--instructions", help="Path to .md/.txt/.docx/.pdf/.xlsx instruction file")
    ap.add_argument("--values", help="Path to values.yaml for the instruction file passed in the args")
    ap.add_argument("--no-orchestrator", action="store_true",
                    help="Run the executor model directly, with no orchestrator")
    ap.add_argument("--show-browser", action="store_true", help="Show the browser window")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    asyncio.run(run(ap.parse_args()))

main()