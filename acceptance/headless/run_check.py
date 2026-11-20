#!/usr/bin/env python3
"""Run Checks headless, unattended, and write a fingerprinted results file.

    export CLAUDE_CODE_OAUTH_TOKEN=...     # once: `claude setup-token`
    python3 acceptance/headless/run_check.py <scope> --model <exact model ID> [--runs 3]
    python3 acceptance/headless/run_check.py gate --model <exact model ID> [--published latest|none|<tag>]

The scope is one or more Check IDs or skill names (a skill stands for every
Check whose `skills` list names it), as a Scoped run. Or it is `gate` alone, a Gate run: the gate planner (plan.py), over
the results files in `--results`, decides which Checks run and how often, and
a Check with a fail gets 3 more runs after its first 3, until the planner needs none for it
or it blocks. Check runs go in Check-ID order, each Check's repeats back to
back, and a fail never stops the run. A Gate run's results file ends its table
with the gate report: each Check's verdict and pooled pass rate, its flakes,
and the gate's verdict.

Each Check run, following acceptance/runner/claude-code.md with the headless
driver in place of the two subagents (steps 1 and 2, and the prompt and
stand-ins of step 3, are lay.py's: it lays the Workspace from the Check's
Start):

1. The sample is copied into a fresh Workspace in a temporary folder outside
   the clone (so no CLAUDE.md above it is read), and committed.
2. Install: a headless Claude Code session in the Workspace is told to follow
   the clone's setup, then "Yes, go ahead."; the Install key is graded. The
   Check's change after install, its Start's `sh` block, is made and
   committed, and HEAD is `$BASE`. A Check whose Start says **No install**
   has no install session: its Start's `sh` block lays the frozen install over the
   committed sample instead, and its commit is `$BASE`. One whose Start says
   **Engineer repo** has no sample either: that block makes the engineer's repo in
   the empty folder.
3. Jenny: a second, fresh session in the Workspace, so she loads AGENTS.md and
   her skills as an Operator's install does. Turn 1 starts it, word for word
   from the Check (`<REPO>` in a turn is the clone's path); each later turn
   goes word for word through `--resume`.
   A Check whose `skills` list names `jenny` runs in the Jenny mode: the
   mode's instructions (MODE) are appended to her system prompt on every
   turn. An Engineer repo Check's session is the engineer's own coding
   agent, with no Jenny skills: the Engineer prompt (ENGINEER) is appended
   instead. Each MCP stand-in in the Check's Start is copied to `fixtures/` in
   the Check run's folder, and the runner's stand-in sentence naming it is
   appended too; no session reaches an MCP server.
   Each reply is saved to `turns/<n>.md`, and its Veneer scan line records
   what the scan found without grading it (grade.veneer_scan); Key at
   proposal is graded after the turns it names, Key at write after the last.
   The isolation proof (isolation.py) is read after turn 1.
4. Its section goes to `sections/`; the Workspace moves into the run folder.

Driver errors, usage, rate and context limits, and a leak into the session
make the Check run Void: it is rerun once, and a fourth Void ends the run
with no verdict (a hard stop), as does a change to the clone. The results
file is `<run folder>/results.md`, copied into `--results` (default
acceptance/results/), where the gate planner reads it.

Exit 0: every Check run passed (a Gate run: the gate passed, flakes and all).
1: one failed (a Gate run: the gate blocks). 2: a hard stop, no verdict.
"""

import argparse
import datetime
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "acceptance" / "gate"))

from check import CheckError, install_key, load_all  # noqa: E402
import fingerprint  # noqa: E402
import grade  # noqa: E402
import isolation  # noqa: E402
import lay  # noqa: E402
import plan  # noqa: E402
from session import DriverError, Session, auth_present  # noqa: E402

DRIVER = "headless"
VOIDS = 4  # the fourth Void is a hard stop
CLONE_STATE = ("{ git rev-parse HEAD; git status --porcelain --untracked-files=all; git diff HEAD --binary; "
               "git ls-files -z -o --exclude-standard | xargs -0r sha1sum; } | sha1sum")


class Void(Exception):
    pass


# ------------------------------------------------------------ the Check

def scope(repo, words):
    """The Checks a scope names, in Check-ID order: each word a Check ID, or a
    skill standing for every Check whose `skills` list names it. KeyError
    for a word that names none."""
    every = load_all(repo)
    out = set()
    for w in words:
        found = [c for c in every.values() if c.id == w or w in c.skills]
        if not found:
            raise KeyError(w)
        out.update(c.id for c in found)
    return [every[i] for i in sorted(out)]


# ------------------------------------------------------------ one Check run

def graded(results):
    return grade.summary(results, "every line pass")


class CheckRun:
    def __init__(self, ctx, check, n, k):
        self.ctx, self.check, self.n, self.k = ctx, check, n, k
        self.d = ctx.run_dir / (f"{check.id}-{n}" + (f"-r{k}" if k else ""))
        self.notes = {}
        self.failed = False

    def session(self, name, cwd, add_dirs=(), system=None):
        """A session with a config folder of its own, so not even the install
        session's state reaches Jenny's."""
        config = self.d / "claude-config" / name
        config.mkdir(parents=True)
        return Session(cwd, config, self.ctx.model, log=self.d / "sessions" / name,
                       claude=self.ctx.claude, add_dirs=add_dirs, timeout=self.ctx.timeout, system=system)

    def run(self):
        """'pass' or 'fail'; raises Void."""
        self.d.mkdir(parents=True)
        tmp = Path(tempfile.mkdtemp(prefix="jenny-acceptance-"))
        ws = tmp / "ws"
        try:
            return self.in_workspace(ws)
        except DriverError as e:
            raise Void(str(e))
        except subprocess.CalledProcessError as e:  # laying the sample, the driver's own slip
            raise Void(f"{' '.join(e.cmd)} exited {e.returncode}: {(e.stderr or '').strip()}")
        finally:
            if ws.exists():
                shutil.move(str(ws), str(self.d / "ws"))
            shutil.rmtree(tmp, ignore_errors=True)

    def in_workspace(self, ws):
        try:
            laid = lay.lay(self.check, ws, self.d, self.session)
        except lay.StartFailed as e:
            raise Void(str(e))
        self.notes.update(laid.notes)
        if laid.install_failed:
            return "fail"
        env = laid.env
        jenny = self.session("jenny", ws, system=laid.system)
        turns = self.check.turns
        proposal, scans = [], []
        for i, text in enumerate(turns, 1):
            (env.turns / f"{i}.md").write_text(jenny.send(text), encoding="utf-8")
            if i == 1:
                leaks = isolation.problems(jenny.config_dir, jenny.id, ws, need=laid.need)
                if leaks:
                    raise Void("Jenny's session was not kept to the Workspace: " + "; ".join(leaks))
                self.notes["Isolation"] = f"pass (session {jenny.id})"
            scan = grade.veneer_scan(env, i)
            if scan is not None:
                scans.append(f"turn {i} {scan}")
            if i in self.check.key.proposal_turns:
                results = grade.grade(self.check, "proposal", env, turn=i)
                proposal.append(f"turn {i}: {graded(results)}")
                self.failed |= not all(r.ok for r in results)
        results = grade.grade(self.check, "write", env)
        self.failed |= not all(r.ok for r in results)
        self.notes["Key at proposal"] = "; ".join(proposal)
        self.notes["Key at write"] = graded(results)
        self.notes["Veneer scan"] = "; ".join(scans) if scans else "no veneer.md"
        return "fail" if self.failed else "pass"

    def heading(self):
        return f"## {self.check.id} run {self.n}" + (f", rerun {self.k}" if self.k else "")


# ------------------------------------------------------------ the run

class Ctx:
    def __init__(self, a):
        self.repo = Path(a.root).resolve()
        self.model, self.claude, self.timeout = a.model, a.claude, a.timeout
        self.run_dir = Path(a.run_dir).resolve()

    def clone_state(self):
        return subprocess.run(["bash", "-c", CLONE_STATE], cwd=str(self.repo), capture_output=True,
                              text=True, check=True).stdout


def prompt(run_checks):
    """The header's Prompt: none, since turn 1 goes as the Operator typed it,
    with the Checks run in the Jenny mode, and under the Engineer prompt, named."""
    out = "Prompt: none"
    for name in (lay.JENNY_MODE, lay.ENGINEER_PROMPT):
        ids = [c.id for c in run_checks if name in lay.prompts(c)]
        if ids:
            out += f", {name} for {' '.join(ids)}"
    return out


def row(check, n, fp, result):
    return f"| {check.id} | {check.version} | {n} | {fp} | {result} |"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run Checks headless and write a results file.")
    ap.add_argument("scope", nargs="+", help="Check IDs or skill names, or `gate` alone for a Gate run")
    ap.add_argument("--model", required=True, help="the exact model ID, never an alias")
    ap.add_argument("--runs", type=int, help="Check runs to make of each Check (default 1; never in a Gate run)")
    ap.add_argument("--published", default="latest",
                    help="Gate run: the last published Tool version's tag, `latest` (default) or `none`")
    ap.add_argument("--claude", default="claude", help="the Claude Code executable")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds to wait for one turn")
    ap.add_argument("--run-dir", help="default: acceptance/runs/<YYYY-MM-DD-HHMM>-<scope>-headless")
    ap.add_argument("--results", help="folder to copy results.md into, and a Gate run's evidence "
                                      "(default acceptance/results; `none`: no copy, and no earlier evidence)")
    ap.add_argument("--root", default=str(REPO))
    a = ap.parse_args(argv)
    is_gate = "gate" in a.scope
    if is_gate and (a.scope != ["gate"] or a.runs is not None):
        ap.exit(2, "run_check: a Gate run takes no other scope and no --runs: the gate planner decides its runs\n")
    now = datetime.datetime.now()
    name = f"{now:%Y-%m-%d-%H%M}-{'-'.join(a.scope)}-headless"
    a.run_dir = a.run_dir or str(Path(a.root) / "acceptance" / "runs" / name)
    if not auth_present():
        ap.exit(2, "run_check: set CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`) or ANTHROPIC_API_KEY: "
                   "the session never reads your own login.\n")
    ctx = Ctx(a)
    results_dir = None if a.results == "none" else Path(a.results) if a.results else ctx.repo / "acceptance" / "results"
    with plan.published_tree(ctx.repo, a.published if is_gate else "none") as (tag, published):
        gate_plan = {}
        if is_gate:
            gate_plan = {r.check: r for r in plan.plan(ctx.repo, results_dir, model=ctx.model, driver=DRIVER,
                                                        published_root=published)}
            every = load_all(ctx.repo)
            checks = [every[cid] for cid, r in sorted(gate_plan.items()) if r.needed and r.verdict != "block"]
        else:
            try:
                checks = scope(ctx.repo, a.scope)
            except KeyError as e:
                ap.exit(2, f"run_check: no Check or skill {e.args[0]}\n")
        try:  # an unreadable key line stops the run before any Check run
            for check in checks:
                check.key
            if any(check.start.installs for check in checks):
                install_key(ctx.repo)
        except CheckError as e:
            ap.exit(2, f"run_check: {e}\n")
        if Path(ctx.run_dir).exists():
            ap.exit(2, f"run_check: {ctx.run_dir} already exists\n")
        code, out = run(ctx, a, checks, gate_plan, now)
        # Copied before the report is made, so a flake names the file it is kept as.
        kept = results_dir / f"{ctx.run_dir.name}.md" if results_dir is not None else None
        if kept:
            shutil.copy(out, kept)
        if is_gate and code != 2:
            rows = plan.plan(ctx.repo, results_dir, model=ctx.model, driver=DRIVER, published_root=published,
                             extra=[] if kept else [out])
            report(out, plan.render(rows, tag))
            code = 1 if plan.gate(rows) == "block" else 0
            if kept:
                shutil.copy(out, kept)
    print(out)
    return code


def remaining(check, made, a, gate_plan):
    """Check runs `check` still needs, with `made` its results in this run so far.
    In a Gate run the planner decides, over the earlier evidence and `made`;
    a Check that blocks needs none, since more runs can't lift the block."""
    if check.id not in gate_plan:
        return (a.runs or 1) - len(made)
    r = gate_plan[check.id]
    needed, verdict = plan.weigh(list(r.results) + made, r.base, check.promise)
    return 0 if verdict == "block" else needed


def run(ctx, a, checks, gate_plan, now):
    """Make the Check runs and write results.md: (exit code, its path)."""
    fps = {c.id: fingerprint.fingerprint(ctx.repo, c.id, model=ctx.model, driver=DRIVER) for c in checks}
    (ctx.run_dir / "sections").mkdir(parents=True)
    state = ctx.clone_state()
    (ctx.run_dir / "clone-state").write_text(state)
    header = [f"# Acceptance run {ctx.run_dir.name}", "",
              f"Date: {now:%Y-%m-%d} · Runtime: claude-code · Driver: {DRIVER} · Model: {ctx.model} · {prompt(checks)}",
              f"Tool version: {(ctx.repo / 'VERSION').read_text().strip()} · Sample version: {lay.sample_version(ctx.repo)}"
              f" · Scope: {'gate' if gate_plan else ' '.join(c.id for c in checks)}"]
    sections, voids, stop, results = [], 0, None, []  # sections: (row, body, file name)
    for check in checks:
        made = []
        while stop is None and remaining(check, made, a, gate_plan) > 0:
            n, k = len(made) + 1, 0
            while stop is None:
                if ctx.clone_state() != state:
                    stop = "clone changed"
                    break
                cr = CheckRun(ctx, check, n, k)
                try:
                    result = cr.run()
                    body = "\n".join(f"{key}: {v}" for key, v in cr.notes.items())
                    body += f"\nBy eye: not read in a headless run; the replies are in `{cr.d.name}/turns/`."
                except Void as e:
                    result, body = "void", f"Void: {e}"
                sections.append((row(check, n, fps[check.id], result), f"{cr.heading()}\n\n{body}\n", cr.d.name))
                print(f"{check.id} run {n}" + (f" rerun {k}" if k else "") + f": {result}", file=sys.stderr)
                if result != "void":
                    made.append(result)
                    break
                voids += 1
                k += 1
                if voids >= VOIDS:
                    stop = "fourth void"
        if stop:
            # Every Check run still to make, a Void left without its rerun included.
            later = checks[checks.index(check) + 1:]
            sections += not_run(check, made, a, gate_plan, fps)
            sections += [s for c in later for s in not_run(c, [], a, gate_plan, fps)]
            break
        results += made
    if stop is None and ctx.clone_state() != state:
        stop = "clone changed"
    if stop:
        header.append(f"Verdict: none · Hard stop: {stop}")

    for i, (r, body, name) in enumerate(sections, 1):
        (ctx.run_dir / "sections" / f"{i:03d}-{name}.md").write_text(r + "\n\n" + (body or ""), encoding="utf-8")
    text = "\n".join(header) + "\n\n| Check | Version | Run | Fingerprint | Result |\n| --- | --- | --- | --- | --- |\n"
    text += "".join(r + "\n" for r, _, _ in sections)
    text += "".join("\n" + body for _, body, _ in sections if body)
    out = ctx.run_dir / "results.md"
    out.write_text(text, encoding="utf-8")
    return (2 if stop else 1 if "fail" in results else 0), out


def not_run(check, made, a, gate_plan, fps):
    """A `not run` section for each run `check` still needs, after the `made` ones."""
    first = len(made) + 1
    return [(row(check, m, fps[check.id], "not run"), None, f"{check.id}-{m}")
            for m in range(first, first + remaining(check, made, a, gate_plan))]


def report(out, text):
    """Put the gate report into the results file, after its table."""
    lines = out.read_text(encoding="utf-8").split("\n")
    first = next(i for i, l in enumerate(lines) if l.startswith("|"))
    end = next((i for i in range(first, len(lines)) if not lines[i].startswith("|")), len(lines))
    lines[end:end] = ["", "## Gate report", "", text]
    out.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
