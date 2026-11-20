#!/usr/bin/env python3
"""SL-03's and SL-04's Milestone key lines: whether Milestones bound the
slice, and whether each Milestone's members are its Features.

    python3 "$REPO/acceptance/headless/graders/SL-03/milestones.py" "$P"

Reads the Project folder given and prints one line per problem; prints nothing
when there is none. Always exits 0, so the key line reads its output.

- A Requirement's Milestone is the card line of `storymap.md` it sits on
  (`- <MIL ID>: <REQ ID> (<user>), …`). One under `## Not on the map`, or on
  no card line, has none and bounds nothing.
- A Feature holds the Requirements whose `- **<REQ ID>**` lines are in its
  file (a struck-through, withdrawn line holds nothing). A Feature holding
  Requirements of two Milestones straddles them:
  `<FEA ID>: Requirements in <MIL ID> and <MIL ID>`.
- A Milestone's Features are those holding one of its Requirements. Its
  `## Members` must list exactly those, as `- <FEA ID>` lines, and read
  `Not sliced yet.` only when there are none:
  `<MIL ID>: lists <IDs | none>, but its Features are <IDs>`,
  `<MIL ID>: still reads "Not sliced yet."`, or
  `<MIL ID>: lists none, and does not read "Not sliced yet."`.
"""

import re
import sys
from pathlib import Path

CARD = re.compile(r"^- ([A-Z]{2,4}-MIL-\d{3}): (.+)$")
REQ = re.compile(r"[A-Z]{2,4}-REQ-\d{3}")
HELD = re.compile(r"^- \*\*([A-Z]{2,4}-REQ-\d{3})\*\*")
MEMBER = re.compile(r"^- ([A-Z]{2,4}-FEA-\d{3})\b")
NOT_SLICED = "Not sliced yet."
FILE_ID = re.compile(r"^([A-Z]{2,4}-(?:FEA|MIL)-\d{3})-")

# The Guard reads `## Members` too; a grader keeps its own reading, so a Guard
# change cannot quietly change what a Check grades.


def milestone_of(storymap):
    """{REQ ID: MIL ID} from the card lines, above `## Enablers`."""
    out = {}
    for line in storymap.splitlines():
        if line.rstrip() in ("## Enablers", "## Not on the map"):
            break
        m = CARD.match(line.rstrip())
        if m:
            for rid in REQ.findall(m.group(2)):
                out[rid] = m.group(1)
    return out


def held(features):
    """{FEA ID: [REQ IDs]} from each `features/<FEA ID>-*.md`."""
    out = {}
    for f in sorted(features.glob("*-FEA-[0-9][0-9][0-9]-*.md")):
        fid = FILE_ID.match(f.name).group(1)
        out[fid] = [m.group(1) for m in map(HELD.match, f.read_text(encoding="utf-8").splitlines()) if m]
    return out


def members(text):
    """(member FEA IDs, whether `Not sliced yet.` is there) under `## Members`."""
    ids, not_sliced, section = [], False, False
    for line in text.splitlines():
        line = line.rstrip()
        if line.startswith("## "):
            section = line == "## Members"
        elif section and line == NOT_SLICED:
            not_sliced = True
        elif section:
            m = MEMBER.match(line)
            if m:
                ids.append(m.group(1))
    return ids, not_sliced


def problems(project):
    project = Path(project)
    where = milestone_of((project / "storymap.md").read_text(encoding="utf-8"))
    features = held(project / "features")
    out, of_milestone = [], {}
    for fid, rids in features.items():
        mids = sorted({where[r] for r in rids if r in where})
        if len(mids) > 1:
            out.append("%s: Requirements in %s" % (fid, " and ".join(mids)))
        for mid in mids:
            of_milestone.setdefault(mid, set()).add(fid)
    for f in sorted((project / "milestones").glob("*-MIL-[0-9][0-9][0-9]-*.md")):
        mid = FILE_ID.match(f.name).group(1)
        want = sorted(of_milestone.get(mid, ()))
        got, not_sliced = members(f.read_text(encoding="utf-8"))
        got = sorted(set(got))
        if got != want:
            out.append("%s: lists %s, but its Features are %s" % (mid, ", ".join(got) or "none",
                                                                  ", ".join(want) or "none"))
        elif want and not_sliced:
            out.append('%s: still reads "%s"' % (mid, NOT_SLICED))
        elif not want and not not_sliced:
            out.append('%s: lists none, and does not read "%s"' % (mid, NOT_SLICED))
    return out


if __name__ == "__main__":
    for line in problems(sys.argv[1]):
        print(line)
