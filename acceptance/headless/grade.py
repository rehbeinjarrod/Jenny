#!/usr/bin/env python3
"""Key lines graded: run against a Check run's Workspace. Also the Veneer scan
line, which is not a key line: it records what the scan found on each reply
and never grades.

The lines are read by the Check value (check.py): a Check's own from its
Markdown (`check.key`), the Install key every headless Check run shares from
the Claude Code runner doc (check.install_key()). Each is a check.Line: a
label (what it proves, as the Check words it) and one or more shell
commands, each with the output it expects: exact text (its spaces at either
end not counted, as the output's are not), empty (""), or at_least(n) (a
count of n or more). Commands run in bash with the runner's variables set:
$REPO, $WS, $SK, $BASE, $TURNS, $SAMPLE. `<n>` in a command is the turn being
graded. A line passes when every command's output meets its expectation.
A Key's preludes are set before each of its commands.

The Workspace graded is laid from the Check's Start by lay.py.

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

from check import CheckError, load as load_check

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


class Env(NamedTuple):
    repo: Path
    ws: Path
    base: str
    turns: Path
    sample: str = ""  # the sample commit, which the Install key reads as $SAMPLE

    def vars(self):
        return {"REPO": str(self.repo), "WS": str(self.ws), "SK": str(Path(self.ws) / ".claude" / "skills"),
                "BASE": self.base, "TURNS": str(self.turns), "SAMPLE": self.sample}


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
    """The expectation with each `$NAME` (`$BASE`, a prelude's `$A`) filled
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


def summary(results, passed="pass"):
    """Results in a note: `passed`, or each failed line with what it got."""
    bad = [f"fail: {r.label} (got {r.output!r}, want {r.expected})" for r in results if not r.ok]
    return "; ".join(bad) if bad else passed


def grade(check, stage, env, turn=None):
    """The Results of one stage of the Check value `check`: `proposal` (with
    its turn) or `write`."""
    key = check.key
    if stage == "proposal":
        return run(key.proposal(turn), env, turn, prelude=key.proposal_prelude)
    if stage == "write":
        return run(key.write, env, prelude=key.write_prelude)
    raise ValueError(f"unknown stage {stage}")


# ------------------------------------------------------------ the Veneer scan line

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
        results = grade(load_check(a.check, a.repo), a.stage, env, a.turn)
    except (CheckError, KeyError) as e:  # an unreadable key line, or no such Check
        print(e.args[0] if e.args else e, file=sys.stderr)
        return 2
    for r in results:
        print(f"{'pass' if r.ok else 'fail'} {r.label}" + ("" if r.ok else f" (got {r.output!r}, want {r.expected})"))
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
