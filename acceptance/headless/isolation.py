"""The proof that Jenny's session loaded the Workspace's AGENTS.md and skills,
and none of the maintainer's own settings or memory.

Claude Code records what it loaded in the session's transcript, under the
session's CLAUDE_CONFIG_DIR: an `instructions` entry naming every CLAUDE.md,
AGENTS.md and rules file read, and a `skill_listing` entry naming every skill
offered. The session passes when:

- every instruction file is inside the Workspace, and the Workspace's
  CLAUDE.md and AGENTS.md are among them (an engineer's repo has no
  CLAUDE.md, so none are looked for there);
- every Workspace skill is offered, and no skill from the maintainer's own
  `~/.claude/skills/` is. A skill marked `disable-model-invocation: true`
  (Jenny's own `jenny` skill) is never listed, so it is not looked for.

Skills built into Claude Code itself are offered too, as on an Operator's
install, and are not counted against it.
"""

import json
import os
from pathlib import Path


def transcript(config_dir, session_id):
    found = sorted(Path(config_dir).glob(f"projects/*/{session_id}.jsonl"))
    return found[0] if found else None


def attachments(path, kind):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        a = entry.get("attachment") if isinstance(entry, dict) else None
        if isinstance(a, dict) and a.get("type") == kind:
            out.append(a)
    return out


def skill_names(folder, listed_only=False):
    """The skills in `folder`; with `listed_only`, only those Claude Code puts
    in its skill listing."""
    return {p.parent.name for p in Path(folder).glob("*/SKILL.md")
            if not (listed_only and operator_only(p))}


def operator_only(skill_md):
    """Whether the skill's front matter sets `disable-model-invocation: true`."""
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            return False
        key, _, value = line.partition(":")
        if key.strip() == "disable-model-invocation" and value.strip().lower() == "true":
            return True
    return False


def inside(path, folder):
    return Path(os.path.realpath(path)).is_relative_to(Path(os.path.realpath(folder)))


def problems(config_dir, session_id, ws, home=None, need=("CLAUDE.md", "AGENTS.md")):
    """Each way the session was not kept to the Workspace; empty when it was.
    `need`: the Workspace's instruction files it must have loaded."""
    ws = Path(ws)
    t = transcript(config_dir, session_id)
    if t is None:
        return [f"no transcript for session {session_id} under {config_dir}"]
    out = []
    loaded = [f.get("path", "") for a in attachments(t, "instructions") for f in a.get("files", [])]
    for path in loaded:
        if not inside(path, ws):
            out.append(f"loaded an instruction file from outside the Workspace: {path}")
    for name in need:
        if not any(os.path.realpath(p) == os.path.realpath(ws / name) for p in loaded):
            out.append(f"did not load the Workspace's {name}")
    offered = {n for a in attachments(t, "skill_listing") for n in a.get("names", [])}
    for name in sorted(skill_names(ws / ".claude" / "skills", listed_only=True) - offered):
        out.append(f"did not offer the Workspace skill {name}")
    own = skill_names(Path(home or Path.home()) / ".claude" / "skills") - skill_names(ws / ".claude" / "skills")
    for name in sorted(own & offered):
        out.append(f"offered the maintainer's own skill {name}")
    return out
