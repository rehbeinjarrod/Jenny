#!/usr/bin/env python3
"""The gate planner: what each Check's evidence says, and what it still needs
(the gate rules in acceptance/runner/check-format.md).

For each Check at its current Fingerprint it weighs every counted run in the
results files, in file-name order:

- A counted run is a `pass` or `fail` row at that Fingerprint. `void` and
  `not run` rows never count. A results file counts only if its header has a
  `Driver:` and a `Model:` and its table a Fingerprint column; older files are
  history.
- A Check needs 3 counted runs, or none if its Fingerprint is unchanged since
  the last published Tool version (carry-over).
- A Check with a fail needs 3 more after its first 3: 6 counted runs.
- 2 or more fails block. A Promise Check blocks on a confirmed fail: one more
  fail in the 3 runs after a fail, which the 2-fail rule already covers.
- With runs still needed, the verdict is `needs runs`; otherwise 1 fail is a
  `flake` and none a `pass`.

Each block gets a line saying why: its fails, its counted runs and the
results files holding the fails. Each Check needing runs gets one with the
runs still needed, its counted runs and its fails.

Beside the verdict, each Check's pass rate across every Fingerprint, on the
same runtime, driver and model, with its 95% Wilson interval: the slow drift
one gate can't see. Each flake names the results file holding its fail.

Usage: plan.py --model <exact model ID> [--driver headless] [--runtime claude-code]
               [--root <repo>] [--results <folder>] [--published latest|none|<tag>]
               [--published-tree <folder holding that tag's tree>]
"""

import argparse
import contextlib
import io
import math
import re
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fingerprint  # noqa: E402
from check import load_all  # noqa: E402  (fingerprint puts the headless driver on the path)

RUNS = 3      # counted runs a Check needs at a new Fingerprint
CONFIRM = 3   # more runs, after the first RUNS, that a fail asks for
BLOCK = 2     # fails that block


@dataclass(frozen=True)
class Row:
    check: str
    promise: bool
    fingerprint: str
    carried: bool
    runs: int
    fails: int
    needed: int
    verdict: str  # pass | flake | block | needs runs
    results: tuple = ()     # counted results at this Fingerprint, oldest first
    fail_files: tuple = ()  # the results files holding those fails, by name
    pooled_passes: int = 0  # passes across every Fingerprint, this runtime, driver and model
    pooled_runs: int = 0    # counted runs across the same

    @property
    def base(self):
        """Counted runs the Check needs before any fail: none when carried over."""
        return 0 if self.carried else RUNS


@dataclass(frozen=True)
class Evidence:
    """One counted Check run: a pass or fail row of a fingerprinted results file."""
    check: str
    fingerprint: str
    result: str  # pass | fail
    runtime: str
    driver: str
    model: str
    file: str    # the results file's name


def header_field(header, name):
    """The value of `<name>: <value>` in a results file's header lines, or None."""
    m = re.search(rf"(?:^|· ){name}: (\S+)", header, re.M)
    return m.group(1) if m else None


def evidence(*sources):
    """Every pass or fail row of every fingerprinted results file in `sources`
    (folders of results files, or single files; None is skipped), as Evidence,
    in file-name then row order."""
    paths = []
    for src in sources:
        if src is None:
            continue
        src = Path(src)
        paths += sorted(src.glob("*.md")) if src.is_dir() else [src]
    out = []
    for path in sorted(paths, key=lambda p: p.name):
        lines = path.read_text(encoding="utf-8").splitlines()
        first = next((i for i, l in enumerate(lines) if l.startswith("|")), None)
        if first is None:
            continue
        header = "\n".join(lines[:first])
        driver, model = header_field(header, "Driver"), header_field(header, "Model")
        if not (driver and model):
            continue
        cols = [c.strip() for c in lines[first].strip().strip("|").split("|")]
        if not {"Check", "Fingerprint", "Result"} <= set(cols):
            continue
        for line in lines[first + 2:]:
            if not line.startswith("|"):
                break
            cells = dict(zip(cols, (c.strip() for c in line.strip().strip("|").split("|"))))
            if cells.get("Result") in ("pass", "fail"):
                out.append(Evidence(cells["Check"], cells["Fingerprint"], cells["Result"],
                                    header_field(header, "Runtime"), driver, model, path.name))
    return out


def counted_runs(results_dir):
    """Every pass or fail row of every fingerprinted results file, as
    (check, fingerprint, result), in file-name then row order."""
    return [(e.check, e.fingerprint, e.result) for e in evidence(results_dir)]


def wilson(passes, runs, z=1.96):
    """The 95% Wilson interval (low, high) for `passes` of `runs`, or None for no runs."""
    if not runs:
        return None
    p, d = passes / runs, 1 + z * z / runs
    centre = (p + z * z / (2 * runs)) / d
    half = z * math.sqrt(p * (1 - p) / runs + z * z / (4 * runs * runs)) / d
    return max(0.0, centre - half), min(1.0, centre + half)


def rate(row):
    """A Row's pooled pass rate with its error bar, e.g. `4/5 80% (38–96%)`."""
    k, n = row.pooled_passes, row.pooled_runs
    if not n:
        return "none yet"
    lo, hi = wilson(k, n)
    return f"{k}/{n} {100 * k / n:.0f}% ({100 * lo:.0f}–{100 * hi:.0f}%)"


def weigh(results, base, promise):
    """(needed, verdict) for one Check's counted results, oldest first."""
    fails = [i for i, r in enumerate(results) if r == "fail"]
    required = RUNS + CONFIRM if fails else base
    needed = max(0, required - len(results))
    confirmed = any(0 < j - i <= CONFIRM for i in fails for j in fails)
    if len(fails) >= BLOCK or (promise and confirmed):
        return needed, "block"
    if needed:
        return needed, "needs runs"
    return 0, "flake" if fails else "pass"


def plan(root, results_dir, *, model, driver=fingerprint.DRIVER, runtime=fingerprint.RUNTIME,
         published_root=None, extra=()):
    """A Row for every Check in `root`, in ID order. `results_dir` (or None) and
    the `extra` results files hold the evidence. `published_root` is the tree
    of the last published Tool version, or None for no carry-over."""
    run = dict(model=model, driver=driver, runtime=runtime)
    published = load_all(published_root) if published_root else {}
    found = evidence(results_dir, *extra)
    rows = []
    for cid, check in sorted(load_all(root).items()):
        fp = fingerprint.fingerprint(root, cid, **run)
        carried = cid in published and fingerprint.fingerprint(published_root, cid, **run) == fp
        here = [e for e in found if e.check == cid and e.fingerprint == fp]
        results = [e.result for e in here]
        pooled = [e.result for e in found if e.check == cid
                  and (e.runtime, e.driver, e.model) == (runtime, driver, model)]
        needed, verdict = weigh(results, 0 if carried else RUNS, check.promise)
        rows.append(Row(cid, check.promise, fp, carried, len(results), results.count("fail"), needed,
                        verdict, tuple(results),
                        tuple(dict.fromkeys(e.file for e in here if e.result == "fail")),
                        pooled.count("pass"), len(pooled)))
    return rows


def gate(rows):
    """The gate's verdict over every Check: block, needs runs, or pass."""
    verdicts = {r.verdict for r in rows}
    return "block" if "block" in verdicts else "needs runs" if "needs runs" in verdicts else "pass"


def latest_tag(root):
    """The newest `v<version>` tag merged into HEAD, or None."""
    p = subprocess.run(["git", "-C", str(root), "tag", "--merged", "HEAD", "--list", "v*",
                        "--sort=-version:refname"], capture_output=True, text=True, check=True)
    tags = p.stdout.split()
    return tags[0] if tags else None


def extract(root, tag, into):
    """The tree at `tag`, written under `into`."""
    p = subprocess.run(["git", "-C", str(root), "archive", tag], capture_output=True, check=True)
    with tarfile.open(fileobj=io.BytesIO(p.stdout)) as tar:
        if hasattr(tarfile, "data_filter"):  # Python 3.12, and 3.9.17 onward
            tar.extractall(into, filter="data")
        else:
            tar.extractall(into)


@contextlib.contextmanager
def published_tree(root, published):
    """(tag, tree) of the last published Tool version: `published` is `latest`,
    `none` or a tag. The tree is None with no tag, else a temporary folder."""
    tag = None if published == "none" else latest_tag(root) if published == "latest" else published
    with tempfile.TemporaryDirectory() as tmp:
        if tag:
            extract(root, tag, tmp)
        yield tag, Path(tmp) if tag else None


def render(rows, published):
    out = [f"Carry-over from: {published or 'none'}", "",
           "| Check | Promise | Fingerprint | Runs | Fails | Needed | Verdict | Pass rate, all Fingerprints (95% CI) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        verdict = r.verdict + (" (carried over)" if r.carried and r.verdict == "pass" and not r.runs else "")
        out.append(f"| {r.check} | {'yes' if r.promise else ''} | {r.fingerprint} | {r.runs} | "
                   f"{r.fails} | {r.needed} | {verdict} | {rate(r)} |")
    flakes = [f"Flake: {r.check} at {r.fingerprint}, fail in {', '.join(r.fail_files)}"
              for r in rows if r.verdict == "flake"]
    def plural(n, word):
        return f"{n} {word}" + ("" if n == 1 else "s")
    why = [f"Block: {r.check} at {r.fingerprint}, {plural(r.fails, 'fail')} in {plural(r.runs, 'run')}, "
           f"in {', '.join(r.fail_files)}" for r in rows if r.verdict == "block"]
    why += [f"Needs runs: {r.check} at {r.fingerprint}, {r.needed} more after {r.runs} counted, "
            f"{plural(r.fails, 'fail')}" for r in rows if r.verdict == "needs runs"]
    out += [""]
    for lines in (flakes, why):
        out += lines + ([""] if lines else [])
    out += [f"Runs needed: {sum(r.needed for r in rows)}", f"Gate: {gate(rows)}"]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Print the gate plan.")
    ap.add_argument("--model", required=True, help="the exact model ID, never an alias")
    ap.add_argument("--driver", default=fingerprint.DRIVER)
    ap.add_argument("--runtime", default=fingerprint.RUNTIME)
    ap.add_argument("--root", default=str(fingerprint.ROOT))
    ap.add_argument("--results", help="default: <root>/acceptance/results")
    ap.add_argument("--published", default="latest",
                    help="the last published Tool version's tag, `latest` (default) or `none`")
    ap.add_argument("--published-tree",
                    help="that Tool version's tree, already extracted; `--published` then names its tag")
    a = ap.parse_args(argv)
    if a.published_tree and a.published in ("latest", "none"):
        ap.error("--published-tree needs --published <tag>, the tag it was extracted from")
    root = Path(a.root)
    results = Path(a.results) if a.results else root / "acceptance" / "results"
    run = dict(model=a.model, driver=a.driver, runtime=a.runtime)
    if a.published_tree:
        tag, rows = a.published, plan(root, results, published_root=Path(a.published_tree), **run)
    else:
        with published_tree(root, a.published) as (tag, tree):
            rows = plan(root, results, published_root=tree, **run)
    print(render(rows, tag))
    return 0


if __name__ == "__main__":
    sys.exit(main())
