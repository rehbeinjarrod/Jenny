"""Laying a Check run's Workspace from the Check's Start: everything before
Jenny's first turn. With the Check's Start (check.py), the one place that
knows the three Start kinds.

lay() takes the Check, the Workspace folder, the Check run's folder and a way
to open a session, and returns what it laid (Laid):

- the folder: the sample copied in and committed (`$SAMPLE`), or an empty
  folder for an **Engineer repo** Check;
- for an install Start: the install session, told to follow the clone's setup
  then "Yes, go ahead.", its two replies saved to `install/<n>.md` in the
  Check run's folder, and the Install key graded;
- the Start's `sh` block, run in the Workspace: the change after install, or
  what lays the Workspace in place of an install. HEAD after it is `$BASE`;
- each MCP stand-in copied to `fixtures/` in the Check run's folder;
- the parts of Jenny's system prompt: the Jenny mode for a Check whose
  `skills` list names `jenny`, the Engineer prompt for an Engineer repo, and
  the stand-in sentence for each stand-in;
- the instruction files the isolation proof must find after turn 1;
- the notes the results file records: Install, Prompt and MCP stand-in.

It reports facts and makes no verdicts. A failed Install key comes back as
its results (Laid.install_failed), with nothing laid after it. A Start block that does not run
cleanly raises StartFailed. Driver errors (session.DriverError) and a git
slip laying the sample (subprocess.CalledProcessError) pass through.

run_block() runs a Check's Start `sh` block alone, in a Workspace made some
other way (grading's saved runs lay theirs by hand).
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple, Optional

import grade
from check import ENGINEER_REPO, install_key

INSTALL_TURNS = ("Follow `{repo}/skills/setup/SKILL.md` to install Jenny in this folder. I use Claude Code.",
                 "Yes, go ahead.")

# The Jenny mode's instructions (skills/jenny/mode.md), pointed at the Claude
# Code skills folder. A Check whose `skills` list names `jenny` runs in it.
MODE = "You are Jenny. At the start of every turn, before anything else, read `.claude/skills/jenny/SKILL.md` whole and follow it."

# The Engineer prompt (acceptance/runner/claude-code.md), with `{ws}` the repo:
# an engineer's own coding agent, whose only instructions are the repo's
# AGENTS.md. Its relay and end-of-turn sentences, and turn 1, are a subagent's
# framing; here the engineer's turns go to the session word for word.
ENGINEER = ("You are a coding agent working for an engineer in the repo folder `{ws}`. Read `{ws}/AGENTS.md` "
            "now and follow it as your project instructions. Run every shell command from that folder "
            "(`cd {ws} && …`) and change nothing outside it.")

STAND_IN = ("The Atlassian MCP is not connected in this session. When you would read `{url}` through it, "
            "read `{path}` instead: the MCP returned this file.")

JENNY_MODE, ENGINEER_PROMPT = "the Jenny mode", "the Engineer prompt"


class StartFailed(Exception):
    pass


class Laid(NamedTuple):
    env: grade.Env            # the runner's variables, `$BASE` HEAD once laid; `$TURNS` made, empty
    install: Optional[tuple]  # the Install key's Results, or None: no install session
    system: Optional[str]     # appended to Jenny's system prompt on every turn
    need: tuple               # the instruction files the isolation proof must find
    notes: dict               # Install, Prompt and MCP stand-in, in that order

    @property
    def install_failed(self):
        """An Install key line failed, and nothing was laid after it."""
        return self.install is not None and not all(r.ok for r in self.install)


def sample_version(repo):
    m = re.search(r"^Sample version: (.+)$", (Path(repo) / "acceptance/sample/workspace.md").read_text(), re.M)
    return m.group(1).strip() if m else "?"


def git(ws, *args):
    return subprocess.run(["git", "-C", str(ws), *args], capture_output=True, text=True, check=True).stdout.strip()


def prompts(check):
    """The prompts the Check's session runs under, as the results file names
    them: the Jenny mode, the Engineer prompt, both or neither."""
    return tuple(name for name, on in ((JENNY_MODE, "jenny" in check.skills),
                                       (ENGINEER_PROMPT, check.start.kind == ENGINEER_REPO)) if on)


def run_block(check, env):
    """Run the Check's Start `sh` block, if it has one, in the Workspace;
    StartFailed with its output when it does not run cleanly."""
    if not check.start.block:
        return
    what = "the change after install" if check.start.installs else "laying the Workspace"
    p = subprocess.run(["bash", "-e", "-c", check.start.block], capture_output=True, text=True,
                       env={**os.environ, **env.vars()}, cwd=str(env.ws))
    if p.returncode != 0:
        raise StartFailed(f"{what} exited {p.returncode}: {(p.stdout + p.stderr).strip()}")


def lay(check, ws, run_dir, open_session):
    """Lay the Workspace `ws` for one Check run of `check`, whose folder is
    `run_dir`. `open_session(name, cwd, add_dirs=(), system=None)` opens a session
    with a `send(text)` that returns its reply. Returns a Laid."""
    repo, start = Path(check.root), check.start
    ws, d = Path(ws), Path(run_dir)
    sample = ""
    if start.sample:
        shutil.copytree(repo / "acceptance" / "sample", ws)
        git(ws, "init", "-q")
        git(ws, "add", "-A")
        git(ws, "commit", "-qm", f"Sample v{sample_version(repo)}")
        sample = git(ws, "rev-parse", "HEAD")
    else:
        ws.mkdir()
    env = grade.Env(repo, ws, sample, d / "turns", sample)
    env.turns.mkdir()
    notes, install = {}, None

    if start.installs:
        session = open_session("install", ws, add_dirs=[repo])
        (d / "install").mkdir()
        for i, text in enumerate(INSTALL_TURNS, 1):
            (d / "install" / f"{i}.md").write_text(session.send(text.format(repo=repo)), encoding="utf-8")
        install = tuple(grade.run(install_key(repo), env))
        notes["Install"] = grade.summary(install)
        if not all(r.ok for r in install):  # a fact for the Check run to judge
            return Laid(env, install, None, (), notes)
    else:
        notes["Install"] = f"none ({'No install' if start.sample else 'Engineer repo'})"
    run_block(check, env)
    env = env._replace(base=git(ws, "rev-parse", "HEAD"))

    names = prompts(check)
    system = [{JENNY_MODE: MODE, ENGINEER_PROMPT: ENGINEER.format(ws=ws)}[n] for n in names]
    if names:
        notes["Prompt"] = names[-1]
    stand_ins = []
    for url, rel in start.stand_ins:
        path = d / "fixtures" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(repo / "acceptance" / "fixtures" / rel, path)
        system.append(STAND_IN.format(url=url, path=path))
        stand_ins.append(f"{url} → fixtures/{rel}")
    if stand_ins:
        notes["MCP stand-in"] = "; ".join(stand_ins)
    # An engineer's repo has no CLAUDE.md: the Engineer prompt has the agent read AGENTS.md.
    need = () if start.kind == ENGINEER_REPO else ("CLAUDE.md", "AGENTS.md")
    return Laid(env, install, "\n\n".join(system) or None, need, notes)
