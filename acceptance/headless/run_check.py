#!/usr/bin/env python3
"""Run Checks headless, unattended, and write a fingerprinted results file.

    export CLAUDE_CODE_OAUTH_TOKEN=...     # once: `claude setup-token`
    python3 acceptance/headless/run_check.py <scope> --model <exact model ID> [--runs 3]
    python3 acceptance/headless/run_check.py gate --model <exact model ID> [--published latest|none|<tag>]

The scope is one or more Check IDs or skill names (a skill stands for every
Check whose `skills` list names it), as a Scoped run. Or it is `gate` alone, a Gate run: the gate planner (plan.py), over
the results files in `--results`, decides which Checks run and how often, and
a fail asks for 3 more runs of its Check, until the planner needs none for it
or it blocks. Check runs go in Check-ID order, each Check's repeats back to
back, and a fail never stops the run. A Gate run's results file ends its table
with the gate report: each Check's verdict and pooled pass rate, its flakes,
and the gate's verdict.

Each Check run, following acceptance/runner/claude-code.md with the headless
driver in place of the two subagents:

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
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "acceptance" / "gate"))

import fingerprint  # noqa: E402
import grade  # noqa: E402
import isolation  # noqa: E402
import plan  # noqa: E402
from session import DriverError, Session, auth_present  # noqa: E402

DRIVER = "headless"
VOIDS = 4  # the fourth Void is a hard stop
INSTALL_TURNS = ("Follow `{repo}/skills/setup/SKILL.md` to install Jenny in this folder. I use Claude Code.",
                 "Yes, go ahead.")
CLONE_STATE = ("{ git rev-parse HEAD; git status --porcelain --untracked-files=all; git diff HEAD --binary; "
               "git ls-files -z -o --exclude-standard | xargs -0r sha1sum; } | sha1sum")


class Void(Exception):
    pass


# ------------------------------------------------------------ the Check

def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def operator_turns(repo, check):
    """The Operator script's turns, word for word, each `<paste: <file>>` replaced
    by that fixture's whole text."""
    text = (Path(repo) / check.path).read_text(encoding="utf-8")
    turns = []
    for line in section(text, "Operator script").splitlines():
        m = re.match(r"^\d+\. (.*)$", line)
        if m:
            turns.append(m.group(1))
        elif turns and line.strip():
            turns[-1] += "\n" + line

    def paste(m):
        return (Path(repo) / "acceptance" / "fixtures" / m.group(1)).read_text(encoding="utf-8").rstrip("\n")
    return [re.sub(r"<paste: ([^>]+)>", paste, t).replace("<REPO>", str(repo)) for t in turns]


# The Jenny mode's instructions (skills/jenny/mode.md), pointed at the Claude
# Code skills folder. A Check whose `skills` list names `jenny` runs in it.
MODE = "You are Jenny. At the start of every turn, before anything else, read `.claude/skills/jenny/SKILL.md` whole and follow it."


def in_mode(check):
    return "jenny" in check.skills


# The Engineer prompt (acceptance/runner/claude-code.md), with `{ws}` the repo:
# an engineer's own coding agent, whose only instructions are the repo's
# AGENTS.md. Its relay and end-of-turn sentences, and turn 1, are a subagent's
# framing; here the engineer's turns go to the session word for word.
ENGINEER = ("You are a coding agent working for an engineer in the repo folder `{ws}`. Read `{ws}/AGENTS.md` "
            "now and follow it as your project instructions. Run every shell command from that folder "
            "(`cd {ws} && …`) and change nothing outside it.")


STAND_IN = ("The Atlassian MCP is not connected in this session. When you would read `{url}` through it, "
            "read `{path}` instead: the MCP returned this file.")


def stand_ins(repo, check):
    """The (URL, fixture) of each `MCP stand-in:` in the Check's Start."""
    text = (Path(repo) / check.path).read_text(encoding="utf-8")
    return re.findall(r"MCP stand-in: `([^`]+)` → `([^`]+)`", section(text, "Start"))


def scope(repo, words):
    """The Checks a scope names, in Check-ID order: each word a Check ID, or a
    skill standing for every Check whose `skills` list names it. KeyError
    for a word that names none."""
    checks = fingerprint.load_checks(repo)
    out = set()
    for w in words:
        found = [c for c in checks.values() if c.id == w or w in c.skills]
        if not found:
            raise KeyError(w)
        out.update(c.id for c in found)
    return [checks[i] for i in sorted(out)]


def sample_version(repo):
    m = re.search(r"^Sample version: (.+)$", (Path(repo) / "acceptance/sample/workspace.md").read_text(), re.M)
    return m.group(1).strip() if m else "?"


# ------------------------------------------------------------ one Check run

def git(ws, *args):
    return subprocess.run(["git", "-C", str(ws), *args], capture_output=True, text=True, check=True).stdout.strip()


def graded(results):
    bad = [f"fail: {r.label} (got {r.output!r}, want {r.expected})" for r in results if not r.ok]
    return "; ".join(bad) if bad else "every line pass"


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
        repo = self.ctx.repo
        turns_dir = self.d / "turns"
        turns_dir.mkdir()
        start = grade.start(self.check.id, repo)
        sample = ""
        if start == "engineer repo":
            ws.mkdir()
        else:
            shutil.copytree(repo / "acceptance" / "sample", ws)
            git(ws, "init", "-q")
            git(ws, "add", "-A")
            git(ws, "commit", "-qm", f"Sample v{sample_version(repo)}")
            sample = git(ws, "rev-parse", "HEAD")
        env = grade.Env(repo, ws, sample, turns_dir, sample)

        try:
            if start == "install":
                install = self.session("install", ws, add_dirs=[repo])
                (self.d / "install").mkdir()
                for i, text in enumerate(INSTALL_TURNS, 1):
                    (self.d / "install" / f"{i}.md").write_text(install.send(text.format(repo=repo)), encoding="utf-8")
                results = grade.run(grade.install_key(), env)
                self.notes["Install"] = "pass" if all(r.ok for r in results) else graded(results)
                if not all(r.ok for r in results):
                    return "fail"
                grade.after_install(self.check.id, env)
            else:
                self.notes["Install"] = f"none ({'No install' if start == 'no install' else 'Engineer repo'})"
                grade.lay(self.check.id, env)
        except grade.StartFailed as e:
            raise Void(str(e))
        env = env._replace(base=git(ws, "rev-parse", "HEAD"))
        g = grade.grader(self.check.id)
        system = []
        if in_mode(self.check):
            system.append(MODE)
            self.notes["Prompt"] = "the Jenny mode"
        if start == "engineer repo":
            system.append(ENGINEER.format(ws=ws))
            self.notes["Prompt"] = "the Engineer prompt"
        for url, rel in stand_ins(repo, self.check):
            path = self.d / "fixtures" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(repo / "acceptance" / "fixtures" / rel, path)
            system.append(STAND_IN.format(url=url, path=path))
            stand = f"{url} → fixtures/{rel}"
            self.notes["MCP stand-in"] = "; ".join(filter(None, [self.notes.get("MCP stand-in"), stand]))
        jenny = self.session("jenny", ws, system="\n\n".join(system) or None)
        turns = operator_turns(repo, self.check)
        proposal, scans = [], []
        for i, text in enumerate(turns, 1):
            (turns_dir / f"{i}.md").write_text(jenny.send(text), encoding="utf-8")
            if i == 1:
                # An engineer's repo has no CLAUDE.md: the Engineer prompt has the agent read AGENTS.md.
                need = () if start == "engineer repo" else ("CLAUDE.md", "AGENTS.md")
                leaks = isolation.problems(jenny.config_dir, jenny.id, ws, need=need)
                if leaks:
                    raise Void("Jenny's session was not kept to the Workspace: " + "; ".join(leaks))
                self.notes["Isolation"] = f"pass (session {jenny.id})"
            scan = grade.veneer_scan(env, i)
            if scan is not None:
                scans.append(f"turn {i} {scan}")
            if i in g.PROPOSAL_TURNS:
                results = grade.grade(self.check.id, "proposal", env, turn=i)
                proposal.append(f"turn {i}: {graded(results)}")
                self.failed |= not all(r.ok for r in results)
        results = grade.grade(self.check.id, "write", env)
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


def prompt(repo, checks):
    """The header's Prompt: none, since turn 1 goes as the Operator typed it,
    with the Checks run in the Jenny mode, and under the Engineer prompt, named."""
    out = "Prompt: none"
    mode = [c.id for c in checks if in_mode(c)]
    engineer = [c.id for c in checks if grade.start(c.id, repo) == "engineer repo"]
    if mode:
        out += f", the Jenny mode for {' '.join(mode)}"
    if engineer:
        out += f", the Engineer prompt for {' '.join(engineer)}"
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
            every = fingerprint.load_checks(ctx.repo)
            checks = [every[cid] for cid, r in sorted(gate_plan.items()) if r.needed and r.verdict != "block"]
        else:
            try:
                checks = scope(ctx.repo, a.scope)
            except KeyError as e:
                ap.exit(2, f"run_check: no Check or skill {e.args[0]}\n")
        for check in checks:
            try:
                grade.grader(check.id)
            except grade.NoGrader as e:
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
              f"Date: {now:%Y-%m-%d} · Runtime: claude-code · Driver: {DRIVER} · Model: {ctx.model} · {prompt(ctx.repo, checks)}",
              f"Tool version: {(ctx.repo / 'VERSION').read_text().strip()} · Sample version: {sample_version(ctx.repo)}"
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
