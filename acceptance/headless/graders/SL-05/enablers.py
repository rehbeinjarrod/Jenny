#!/usr/bin/env python3
"""SL-05's enabler key line: whether the slice turned every pending enabler
into a Technical Enabler or an Enabler Story, and whether each Technical
Enabler is well formed and depended on.

    python3 "$REPO/acceptance/headless/graders/SL-05/enablers.py" "$P"

Reads the Project folder given and prints one line per problem; prints nothing
when there is none. Always exits 0, so the key line reads its output.

- Each `- ` line still under `## Enablers` in `storymap.md` is pending:
  `storymap.md: pending enabler <name>`.
- An Epic is a Technical Enabler when its `epic.md` has the header line
  `Technical Enabler: yes`. It needs an `Enables:` line, and `## Covers`
  holds no Requirement:
  `<EPC ID>: a Technical Enabler with no Enables: line`,
  `<EPC ID>: a Technical Enabler covering <REQ IDs>`.
- Each Epic whose `## Covers` holds a Requirement a Technical Enabler enables
  lists that Technical Enabler under `## Depends on`, unless it is handed off
  (a `Tech face:` line), when its `epic.md` stays as it was:
  `<EPC ID>: covers <REQ ID>, which <TE ID> enables, but does not list it under Depends on`.
"""

import re
import sys
from pathlib import Path

REQ = re.compile(r"[A-Z]{2,4}-REQ-\d{3}")
EPIC_DIR = re.compile(r"^([A-Z]{2,4}-EPC-\d{3})-")
ENABLER = re.compile(r"^- \*\*(.+?)\*\*")

# The Guard reads these lines too; a grader keeps its own reading, so a Guard
# change cannot quietly change what a Check grades.


def sections(text):
    """({header key: value}, {section heading: [lines]}) of one `epic.md`."""
    header, body, current = {}, {}, None
    for line in text.splitlines()[1:]:
        line = line.rstrip()
        if line.startswith("## "):
            current = line[3:].strip()
            body[current] = []
        elif current is None:
            m = re.match(r"^([A-Z][A-Za-z' -]*): ?(.*)$", line)
            if m:
                header.setdefault(m.group(1), m.group(2).strip())
        elif line:
            body[current].append(line)
    return header, body


def pending(storymap):
    out, section = [], False
    for line in storymap.splitlines():
        if line.startswith("## "):
            section = line.rstrip() == "## Enablers"
        elif section and line.startswith("- "):
            m = ENABLER.match(line)
            out.append(m.group(1) if m else line[2:].strip())
    return out


def problems(project):
    project = Path(project)
    out = []
    storymap = project / "storymap.md"
    if storymap.exists():
        out += ["storymap.md: pending enabler %s" % n for n in pending(storymap.read_text(encoding="utf-8"))]
    epics = {}
    for f in sorted((project / "epics").glob("*/epic.md")):
        m = EPIC_DIR.match(f.parent.name)
        if m:
            epics[m.group(1)] = sections(f.read_text(encoding="utf-8"))
    enabled = []  # (TE ID, REQ ID)
    for eid, (header, body) in epics.items():
        if header.get("Technical Enabler") != "yes":
            continue
        if "Enables" not in header:
            out.append("%s: a Technical Enabler with no Enables: line" % eid)
        covered = REQ.findall(" ".join(body.get("Covers", [])))
        if covered:
            out.append("%s: a Technical Enabler covering %s" % (eid, ", ".join(covered)))
        enabled += [(eid, r) for r in REQ.findall(header.get("Enables", ""))]
    for te, rid in enabled:
        for eid, (header, body) in sorted(epics.items()):
            if eid == te or rid not in REQ.findall(" ".join(body.get("Covers", []))):
                continue
            if any(l.startswith("- Tech face:") for l in body.get("External items", [])):
                continue
            if te not in " ".join(body.get("Depends on", [])):
                out.append("%s: covers %s, which %s enables, but does not list it under Depends on" % (eid, rid, te))
    return out


if __name__ == "__main__":
    for line in problems(sys.argv[1]):
        print(line)
