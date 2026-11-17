#!/usr/bin/env python3
"""SO-02's worked-example key lines.

    python3 "$REPO/acceptance/headless/graders/SO-02/examples.py" "$V"
    python3 "$REPO/acceptance/headless/graders/SO-02/examples.py" --shape "$V"

With the view alone, prints each worked example on one line: its
`**Example**` line, then each of its sub-bullets with the bullet dropped, so
the other key lines (and sums.py) read the whole example as one line.

With `--shape`, prints one line per example not in the template's shape, and
why; nothing when every one is in shape:

- a scenario: words after the example's `):`, saying who does what;
- one `**Inputs:**` sub-bullet (or `**Inputs**:`), with a number in it;
- for an example citing a Question (`-Q-`), one `**If <answer>:**` sub-bullet
  per answer, at least two, and no `**Outcome:**`; for one citing only a
  Decision (`-ANS-`), exactly one `**Outcome:**` sub-bullet and no `**If`.

A view with no worked example prints that. Always exits 0.
"""

import re
import sys

START = re.compile(r"^(\s*)[-*] \*\*Example\*\*")
SUB = re.compile(r"^\s*[-*] ")


def blocks(text):
    """Each example as (its first line, [its sub-bullets and continuation lines, stripped])."""
    lines = text.splitlines()
    out, i = [], 0
    while i < len(lines):
        m = START.match(lines[i])
        if not m:
            i += 1
            continue
        indent = len(m.group(1))
        first, subs = lines[i], []
        i += 1
        while i < len(lines) and lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) > indent:
            line = lines[i].strip()
            if SUB.match(lines[i]):
                subs.append(SUB.sub("", line, count=1))
            elif subs:
                subs[-1] += " " + line
            else:
                first += " " + line
            i += 1
        out.append((first, subs))
    return out


def joined(text):
    out = []
    for first, subs in blocks(text):
        parts = [first.rstrip()] + subs
        parts = [p if re.search(r"[.;:!?]$", p.replace("*", "")) else p + "." for p in parts[:-1]] + parts[-1:]
        out.append(" ".join(parts))
    return out


def shape_problems(text):
    out = []
    found = blocks(text)
    for n, (first, subs) in enumerate(found, 1):
        ids = re.findall(r"\b[A-Z][A-Z0-9]*-(?:Q|ANS)-\d{3}\b", first)
        name = f"example {n} ({', '.join(ids) or 'no ID'})"
        problems = []
        scenario = re.sub(r"[*`]", "", first.split("):", 1)[1]) if "):" in first else ""
        if len(re.findall(r"[A-Za-z]+", scenario)) < 3:
            problems.append("no scenario after its heading")
        inputs = [s for s in subs if re.match(r"\*\*Inputs(?::\*\*|\*\*:)", s)]
        if len(inputs) != 1:
            problems.append(f"{len(inputs)} **Inputs:** sub-bullets, not 1")
        elif not re.search(r"\d", inputs[0]):
            problems.append("**Inputs:** has no number")
        answers = [s for s in subs if s.startswith("**If ")]
        outcomes = [s for s in subs if re.match(r"\*\*Outcome(?::\*\*|\*\*:)", s)]
        if any("-Q-" in i for i in ids):
            if len(answers) < 2 or outcomes:
                problems.append(f"a question needs an **If …:** outcome per answer, has {len(answers)} and {len(outcomes)} **Outcome:**")
        elif ids:
            if len(outcomes) != 1 or answers:
                problems.append(f"a decision needs one **Outcome:**, has {len(outcomes)} and {len(answers)} **If …:**")
        if problems:
            out.append(f"{name}: " + "; ".join(problems))
    if not found:
        out.append("no worked example")
    return out


def main(argv):
    args = argv[1:]
    shape = "--shape" in args
    paths = [a for a in args if a != "--shape"]
    if len(paths) != 1:
        print("usage: examples.py [--shape] FILE", file=sys.stderr)
        return 0
    with open(paths[0], encoding="utf-8") as f:
        text = f.read()
    for line in (shape_problems if shape else joined)(text):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
