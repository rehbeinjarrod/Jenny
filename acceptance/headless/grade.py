#!/usr/bin/env python3
"""Key lines graded: each Check's own, read from its Markdown by keys.py, and
the Install key every headless Check run shares, read by keys.py from the
Claude Code runner doc. Also the Veneer scan line, which is not a key line:
it records what the scan found on each reply and never grades.

A key line is a label (what it proves, as the Check words it) and one or more
shell commands, each with the output it expects: exact text (its spaces at
either end not counted, as the output's are not), empty (""), or at_least(n)
(a count of n or more; AT_LEAST_ONE is at_least(1)). Commands run in bash with the runner's
variables set: $REPO, $WS, $SK, $BASE, $TURNS. `<n>` in a command is the turn
being graded. A line passes when every command's output meets its expectation.

A Check's key (grader(), a keys.Key) holds:

- PROPOSAL_TURNS: the turns whose replies Key at proposal grades, after each;
- proposal(turn): the Key at proposal lines for that turn;
- write(): the Key at write lines, graded after the last turn;
- PRELUDE: the variables and shell functions the Check's Key at write sets
  (`H=…`), run before each of its commands; PROPOSAL_PRELUDE the same for
  Key at proposal;
- AFTER_INSTALL: the `sh` block of the Check's Start, the change made and
  committed after install, before `$BASE`;
- LAY, for a Check whose Start says **No install** or **Engineer repo**
  (start()): the `sh` block of its Start, which lays and commits the
  Workspace in place of an install, over the committed sample or in an empty
  folder; its commit is `$BASE`.

Usage: grade.py <check ID> --stage proposal|write [--turn <n>]
                --ws <dir> --base <commit> --turns <dir> [--repo <dir>]
Prints `pass|fail <label>` per line (with the output on a fail); exit 0 when
every line passes, 1 otherwise.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def at_least(n):
    return f"{n} or more"


AT_LEAST_ONE = at_least(1)


class NoGrader(LookupError):
    pass


class Env(NamedTuple):
    repo: Path
    ws: Path
    base: str
    turns: Path
    sample: str = ""  # the sample commit, which the Install key reads as $SAMPLE

    def vars(self):
        return {"REPO": str(self.repo), "WS": str(self.ws), "SK": str(Path(self.ws) / ".claude" / "skills"),
                "BASE": self.base, "TURNS": str(self.turns), "SAMPLE": self.sample}


class Line:
    def __init__(self, label, cmd, expect=None):
        self.label = label
        self.parts = list(cmd) if isinstance(cmd, list) else [(cmd, expect)]


class Result(NamedTuple):
    label: str
    ok: bool
    output: str     # the first unmet command's output, or the last one's
    expected: str


def minimum(expect):
    """n for an at_least(n) expectation, else None."""
    m = re.fullmatch(r"(\d+) or more", expect or "")
    return int(m.group(1)) if m else None


def meets(output, expect):
    n = minimum(expect)
    if n is not None:
        return output.isdigit() and int(output) >= n
    return output == expect.strip()


def expanded(expect, env, prelude):
    """The expectation with each `$NAME` (`$BASE`, a PRELUDE's `$A`) filled
    in from the shell; any other text, `$20` or a backtick included, as it is."""
    if minimum(expect) is not None or not expect:
        return expect or ""
    return re.sub(r"\$([A-Za-z_][A-Za-z0-9_]*)",
                  lambda m: sh("\n".join([*prelude, f'printf %s "${m.group(1)}"']), env), expect)


def sh(cmd, env):
    p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True,
                       env={**os.environ, **env.vars()}, cwd=str(env.ws))
    return (p.stdout + p.stderr).strip()


def run(lines, env, turn=None, prelude=()):
    out = []
    for line in lines:
        result = None
        for cmd, expect in line.parts:
            if turn is not None:
                cmd = cmd.replace("<n>", str(turn))
            output = sh("\n".join([*prelude, cmd]), env)
            want = expanded(expect, env, prelude)
            result = Result(line.label, meets(output, want), output, want or "empty")
            if not result.ok:
                break
        out.append(result)
    return out


def grader(check_id):
    """The Check's key, read from its Markdown; NoGrader when there is no
    such Check or a key line can't be read."""
    import keys  # here, not at the top: keys.py builds its Lines from this module
    try:
        return keys.load(check_id, REPO)
    except (keys.KeyLineError, LookupError) as e:  # LookupError: run as a script, keys has its own grade
        raise NoGrader(str(e)) from e


def grade(check_id, stage, env, turn=None):
    """The Results of one stage: `proposal` (with its turn) or `write`."""
    g = grader(check_id)
    if stage == "proposal":
        return run(g.proposal(turn), env, turn, prelude=g.PROPOSAL_PRELUDE)
    if stage == "write":
        return run(g.write(), env, prelude=g.PRELUDE)
    raise ValueError(f"unknown stage {stage}")


# ------------------------------------------------------------ the Start

def start(check_id, repo=REPO):
    """How the Check's Workspace is made, from its Start: `install` (the
    sample, then an install), `no install` (the sample with a frozen install
    laid over it) or `engineer repo` (no sample: an engineer's repo)."""
    found = sorted((Path(repo) / "acceptance" / "checks").glob(f"{check_id}-*.md"))
    if not found:
        raise NoGrader(f"no Check {check_id} in {Path(repo) / 'acceptance' / 'checks'}")
    text = found[0].read_text(encoding="utf-8")
    m = re.search(r"^## Start\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    body = m.group(1) if m else ""
    if "**Engineer repo.**" in body:
        return "engineer repo"
    if "**No install.**" in body:
        return "no install"
    return "install"


class StartFailed(Exception):
    pass


def run_start_block(check_id, name, what, env):
    """Run the Check's Start `sh` block, `name` (AFTER_INSTALL or LAY), if it
    has one, in the Workspace;
    raises StartFailed with the output when it does not run cleanly."""
    text = getattr(grader(check_id), name)
    if not text:
        return
    p = subprocess.run(["bash", "-e", "-c", text], capture_output=True, text=True,
                       env={**os.environ, **env.vars()}, cwd=str(env.ws))
    if p.returncode != 0:
        raise StartFailed(f"{what} exited {p.returncode}: {(p.stdout + p.stderr).strip()}")


def after_install(check_id, env):
    """Make the Check's change after install, if it has one."""
    run_start_block(check_id, "AFTER_INSTALL", "the change after install", env)


def lay(check_id, env):
    """Lay a **No install** or **Engineer repo** Check's Workspace, its LAY."""
    run_start_block(check_id, "LAY", "laying the Workspace", env)


# ------------------------------------------------------------ shared lines

def install_key():
    """The Install key, graded after install: the lines of its section in the
    Claude Code runner doc (acceptance/runner/claude-code.md), read by keys.py.
    `$SAMPLE` is the Env's sample commit."""
    import keys  # here, not at the top: keys.py builds its Lines from this module
    return keys.install_key(REPO)


def veneer_scan(env, turn):
    """The Veneer scan line on one saved reply, run from the Workspace with the
    Tool's own scan: `clean`, `hits: <line>: <word>, …`, `unreadable` (the
    Veneer can't be read, exit 2) or `not run` (any other exit). It records,
    never grades: no result fails or voids a Check run. None when the
    Workspace has no veneer.md."""
    if not (Path(env.ws) / "veneer.md").is_file():
        return None
    scan = Path(env.repo) / "skills/jenny/scripts/veneer_scan.py"
    if not scan.is_file():  # python3 exits 2 on a missing script too, which would read as unreadable
        return "not run"
    reply = Path(env.turns) / f"{turn}.md"
    with reply.open(encoding="utf-8") as f:
        p = subprocess.run([sys.executable, str(scan)],
                           stdin=f, capture_output=True, text=True, cwd=str(env.ws))
    if p.returncode == 0:
        return "clean"
    if p.returncode == 1:
        return "hits: " + ", ".join(p.stdout.splitlines())
    if p.returncode == 2:
        return "unreadable"
    return "not run"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade one stage of a Check run.")
    ap.add_argument("check")
    ap.add_argument("--stage", required=True, choices=("proposal", "write"))
    ap.add_argument("--turn", type=int)
    ap.add_argument("--ws", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--turns", required=True)
    ap.add_argument("--repo", default=str(REPO))
    a = ap.parse_args(argv)
    if a.stage == "proposal" and a.turn is None:
        ap.error("--stage proposal needs --turn")
    env = Env(Path(a.repo), Path(a.ws), a.base, Path(a.turns))
    try:
        results = grade(a.check, a.stage, env, a.turn)
    except NoGrader as e:
        print(e, file=sys.stderr)
        return 2
    for r in results:
        print(f"{'pass' if r.ok else 'fail'} {r.label}" + ("" if r.ok else f" (got {r.output!r}, want {r.expected})"))
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
