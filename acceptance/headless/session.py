"""One headless Claude Code session, driven a turn at a time.

The first `send` starts the session with `claude -p`; each later one goes to
the same session through `--resume`, always with JSON output. Every call's raw
output is saved in `log`.

The session is kept apart from the maintainer's own Claude Code:

- CLAUDE_CONFIG_DIR is a fresh folder in the run, so none of the maintainer's
  settings, memory, skills, plugins or sessions are read;
- the environment holds only what a shell needs, the config folder and the
  auth token, so nothing of the session that starts the run leaks in;
- auth comes only from CLAUDE_CODE_OAUTH_TOKEN (`claude setup-token`) or
  ANTHROPIC_API_KEY, never from the maintainer's stored login;
- `--strict-mcp-config` with no MCP config, so no MCP server is reached, the
  Workspace's own Atlassian entry included: a Check reads Jira and Confluence
  only through its stand-ins (ADR-0003), which `system` names.

Anything that spoils a turn from outside Jenny (Claude Code exiting with an
error, timing out, printing no JSON, an API error such as a usage, rate or
context limit, or running on another model) raises DriverError: the Check run
is Void.
"""

import json
import os
import subprocess
from pathlib import Path

KEEP = ("PATH", "HOME", "USER", "LOGNAME", "SHELL", "LANG", "LC_ALL", "LC_CTYPE", "TERM", "TMPDIR", "TZ")
AUTH = ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY")


class DriverError(Exception):
    pass


def auth_present():
    return any(os.environ.get(k) for k in AUTH)


def clean_env(config_dir):
    env = {k: os.environ[k] for k in KEEP + AUTH if os.environ.get(k)}
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    return env


class Session:
    def __init__(self, cwd, config_dir, model, *, log, claude="claude", add_dirs=(), timeout=1800, system=None):
        self.cwd, self.config_dir, self.model = Path(cwd), Path(config_dir), model
        self.log, self.claude, self.add_dirs, self.timeout = Path(log), claude, tuple(add_dirs), timeout
        self.system = system  # appended to the system prompt on every turn
        self.id = None
        self.calls = 0

    def command(self, text):
        cmd = [self.claude, "-p", text, "--output-format", "json", "--model", self.model,
               "--permission-mode", "bypassPermissions", "--strict-mcp-config"]
        if self.system:
            cmd += ["--append-system-prompt", self.system]
        for d in self.add_dirs:
            cmd += ["--add-dir", str(d)]
        if self.id:
            cmd += ["--resume", self.id]
        return cmd

    def send(self, text):
        """Jenny's reply to `text`, word for word."""
        self.calls += 1
        self.log.mkdir(parents=True, exist_ok=True)
        try:
            p = subprocess.run(self.command(text), cwd=str(self.cwd), env=clean_env(self.config_dir),
                               capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            raise DriverError(f"Claude Code gave no reply in {self.timeout}s")
        except OSError as e:
            raise DriverError(f"Claude Code did not start: {e}")
        (self.log / f"{self.calls}.json").write_text(p.stdout, encoding="utf-8")
        (self.log / f"{self.calls}.stderr").write_text(p.stderr, encoding="utf-8")
        try:
            out = json.loads(p.stdout)
        except ValueError:
            out = None
        if not isinstance(out, dict):
            raise DriverError(f"Claude Code exited {p.returncode} with no JSON result: "
                              f"{(p.stderr or p.stdout).strip()[:300]}")
        if out.get("is_error") or p.returncode != 0 or out.get("subtype") != "success":
            raise DriverError(f"Claude Code reported an error ({out.get('subtype')}, exit {p.returncode}): "
                              f"{str(out.get('result', ''))[:300]}")
        if self.id and out.get("session_id") != self.id:
            raise DriverError(f"--resume {self.id} answered as session {out.get('session_id')}")
        if self.model not in (out.get("modelUsage") or {}):
            raise DriverError(f"the turn ran on {sorted(out.get('modelUsage') or {})}, not {self.model}")
        self.id = out["session_id"]
        return turn_text(self.config_dir, self.id) or out.get("result", "")


def turn_text(config_dir, session_id):
    """Everything Jenny wrote in the session's latest turn, as the Operator
    reads it: each text block of her messages since the last prompt, in order,
    not only the final one that JSON output's `result` holds. Empty when the
    transcript has none."""
    found = sorted(Path(config_dir).glob(f"projects/*/{session_id}.jsonl"))
    if not found:
        return ""
    blocks = []
    for line in found[0].read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if not isinstance(e, dict) or e.get("isSidechain"):
            continue
        content = (e.get("message") or {}).get("content")
        if e.get("type") == "user" and isinstance(content, str):
            blocks = []
        elif e.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                    if not blocks or blocks[-1] != b["text"]:
                        blocks.append(b["text"])
    return "\n\n".join(blocks)
