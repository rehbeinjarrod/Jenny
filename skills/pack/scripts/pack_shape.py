#!/usr/bin/env python3
"""Pack shape scan: name every way a drafted pack misses the template's
shape or the 300-line cap.

Run on a draft, writing no file, or on a pack file:

    python3 <skills>/pack/scripts/pack_shape.py <<'PACK'
    ...the drafted pack...
    PACK
    python3 <skills>/pack/scripts/pack_shape.py <path to pack-v<N>.md>

The sections are the `## ` headings of `../templates/pack.md`. Every line
starting `## ` in the pack counts as a heading, fenced or not, as the
acceptance key reads it. Headings are matched by their stable start (`For the agent`, `<n>.`, `Appendix <X>`)
so Veneer shown names in a heading don't matter. Prints, one per line:

    missing: <the template's heading>
    <line>: out of order: <heading>
    <line>: repeated: <heading>
    <line>: not a pack section: <heading>
    over 300 lines: <count>

Exit codes: 0 good, printing `<count> lines`; 1 problems; 2 the pack file or
the template can't be read (one line on stderr says why).

Python 3.9 or later, standard library only.
"""

import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "pack.md"
CAP = 300
KEY = re.compile(r"## (For the agent|[0-9]+\.|Appendix [A-Z]\b)")


def headings(text):
    """(line number, heading) for each line starting `## `."""
    return [(n, line.rstrip()) for n, line in enumerate(text.splitlines(), start=1)
            if line.startswith("## ")]


def key(heading):
    m = KEY.match(heading)
    return m.group(1) if m else None


def kept_in_order(ranks):
    """Indexes of a longest run of `ranks` in rising order; on a tie, the run
    keeping the later headings, so the one moved early is the one named."""
    best = [1] * len(ranks)
    for i in range(len(ranks)):
        for j in range(i):
            if ranks[j] < ranks[i]:
                best[i] = max(best[i], best[j] + 1)
    kept, want, ceiling = set(), max(best, default=0), float("inf")
    for i in reversed(range(len(ranks))):
        if best[i] == want and ranks[i] < ceiling:
            kept.add(i)
            want, ceiling = want - 1, ranks[i]
    return kept


def problems(text, template):
    expected = [h for _, h in headings(template)]
    rank = {key(h): i for i, h in enumerate(expected)}
    found, out, seen = [], [], set()
    for n, h in headings(text):
        k = key(h)
        if k not in rank:
            out.append((n, "%d: not a pack section: %s" % (n, h)))
        elif k in seen:
            out.append((n, "%d: repeated: %s" % (n, h)))
        else:
            seen.add(k)
            found.append((n, h, rank[k]))
    kept = kept_in_order([r for _, _, r in found])
    for i, (n, h, _) in enumerate(found):
        if i not in kept:
            out.append((n, "%d: out of order: %s" % (n, h)))
    missing = ["missing: " + h for h in expected if key(h) not in seen]
    count = text.count("\n")  # as `wc -l` counts
    over = ["over %d lines: %d" % (CAP, count)] if count > CAP else []
    return missing + [p for _, p in sorted(out)] + over, count


def main(argv):
    if len(argv) > 2:
        print("usage: pack_shape.py [pack file]", file=sys.stderr)
        return 2
    try:
        template = TEMPLATE.read_text(encoding="utf-8")
    except OSError as e:
        print("can't read the pack template: %s" % e, file=sys.stderr)
        return 2
    if len(argv) == 2:
        try:
            text = Path(argv[1]).read_text(encoding="utf-8")
        except OSError as e:
            print("can't read %s: %s" % (argv[1], e), file=sys.stderr)
            return 2
    else:
        text = sys.stdin.read()
    named, count = problems(text, template)
    print("\n".join(named) if named else "%d lines" % count)
    return 1 if named else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
