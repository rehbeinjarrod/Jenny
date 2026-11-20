#!/usr/bin/env python3
"""The one place that decides what a Check depends on.

A Check's Fingerprint is 12 hex digits taken over:

- every file of each skill in its `skills:` list, and each extra Tool file in
  its `inputs:` list;
- the Check file itself, the fixtures it names, and the sample (unless it is an
  Engineer repo Check, which has no sample);
- the runtime, the driver and the exact model ID, and for the headless
  driver its code (`acceptance/headless/*.py` but its tests) and the Check's
  own script folder (`acceptance/headless/graders/<ID>/`, the scripts its key
  lines call, if it has any);
- for a Check that has Jenny in its Workspace, installed or laid frozen
  (every Check whose Start begins from the sample, so every one but an
  Engineer repo one), the shared parts: the Jenny core,
  the AGENTS block, install, and the skill set;
- for a routing Check, the skill set.

Every Check is read through the Check value (acceptance/headless/check.py).

The skill set is which skills exist with each one's `name` and `description`,
so a body edit to one skill moves only that skill's Checks.

Usage: fingerprint.py <check ID> --model <exact model ID>
                      [--driver headless] [--runtime claude-code] [--root <repo>]
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "acceptance" / "headless"))

from check import CHECKS, FIXTURES, frontmatter, load  # noqa: E402

SAMPLE = "acceptance/sample"
# The parts every skill shares, besides the skill set. A change to any of them
# moves every Check with Jenny in its Workspace: every one whose Start begins from the sample.
SHARED = ("skills/jenny", "skills/setup/templates/agents-block.md", "skills/setup/scripts/install.sh")
DRIVER = "headless"
HEADLESS = "acceptance/headless"
RUNTIME = "claude-code"


def files_under(root, rel):
    """`rel` itself if it is a file, every file under it if a folder (Python's
    `__pycache__` left out), else nothing."""
    p = root / rel
    if p.is_file():
        return [rel]
    if p.is_dir():
        return sorted(f.relative_to(root).as_posix() for f in p.rglob("*")
                      if f.is_file() and "__pycache__" not in f.relative_to(p).parts)
    return []


def named_fixtures(root, text):
    """Fixture paths a Check's text names: any path-like token, with anything up
    to `fixtures/` dropped, that is a file or folder under the fixtures folder
    (`"$F/signoff/x/."`, with `F` set to the fixtures folder, names `signoff/x`).
    A bare word with no `/` (a skill name such as `capture`) never names one."""
    base = root / FIXTURES
    out = set()
    text = re.sub(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?", "", text)  # `$F/x` → `/x`
    for token in re.findall(r"[A-Za-z0-9_.\-/]*/[A-Za-z0-9_.\-/]*", text):
        rel = token.split("fixtures/", 1)[-1].lstrip("/")
        while rel.endswith(("/", ".")) and rel not in (".", ""):
            rel = rel[:-2] if rel.endswith("/.") else rel[:-1]
        if rel not in ("", ".") and (base / rel).exists() and ".." not in rel.split("/"):
            out.add(f"{FIXTURES}/{rel}")
    return out


def skill_set(root):
    """Which skills exist, with each one's name and description."""
    lines = []
    for p in sorted((root / "skills").glob("*/SKILL.md")):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        lines.append(f"skill {p.parent.name} name={fm.get('name', '')} description={fm.get('description', '')}")
    return lines


def driver_files(root, check, driver):
    """The headless driver's code, its tests left out, and the Check's own
    script folder."""
    if driver != "headless":
        return []
    code = sorted(p.relative_to(root).as_posix() for p in (root / HEADLESS).glob("*.py")
                  if not p.name.startswith("test_"))
    return code + files_under(root, f"{HEADLESS}/graders/{check.id}")


def dependencies(root, check, driver=None):
    """The repo-relative files a Check depends on, sorted."""
    root = Path(root)
    paths = {check.path, *driver_files(root, check, driver)}
    for name in check.skills:
        paths.update(files_under(root, f"skills/{name}"))
    for rel in check.inputs:
        paths.update(files_under(root, rel))
    for rel in named_fixtures(root, check.text):
        paths.update(files_under(root, rel))
    if check.start.sample:
        paths.update(files_under(root, SAMPLE))
        for rel in SHARED:
            paths.update(files_under(root, rel))
    return sorted(paths)


def fingerprint(root, check_id, *, model, driver=DRIVER, runtime=RUNTIME):
    """The Check's Fingerprint in `root`: 12 hex digits. KeyError for an unknown ID."""
    root = Path(root)
    check = load(check_id, root)
    h = hashlib.sha256()
    h.update(f"runtime={runtime}\ndriver={driver}\nmodel={model}\n".encode())
    for rel in dependencies(root, check, driver):
        h.update(f"file {rel} {hashlib.sha256((root / rel).read_bytes()).hexdigest()}\n".encode())
    if check.start.sample or check.routing:
        h.update("\n".join(skill_set(root)).encode())
    return h.hexdigest()[:12]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Print a Check's Fingerprint.")
    ap.add_argument("check")
    ap.add_argument("--model", required=True, help="the exact model ID, never an alias")
    ap.add_argument("--driver", default=DRIVER)
    ap.add_argument("--runtime", default=RUNTIME)
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    try:
        print(fingerprint(a.root, a.check, model=a.model, driver=a.driver, runtime=a.runtime))
    except KeyError:
        print(f"no Check {a.check} in {Path(a.root) / CHECKS}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
