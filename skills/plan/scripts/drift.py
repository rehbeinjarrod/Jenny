#!/usr/bin/env python3
"""Drift: how a Plan version's dates moved since the version Stakeholders
last saw, and what changed in the inputs to move them.

    python3 <skills>/plan/scripts/drift.py <project dir> <plan dir>

`<project dir>` is `projects/<slug>`; `<plan dir>` is a `plan-v<N>` folder
holding `forecast.json` and `inputs.json`: a committed one, or a new one in a
scratch folder. It is compared with the latest version below N under
`<project dir>/plans/` whose `plan.md` has a `Shown:` line,
`Shown: <YYYY-MM-DD> to <who>`.

Prints to stdout, in Markdown:

- a first line naming both versions, and when and to whom the earlier one
  was shown;
- `## Milestones` and `## Epics`: one line per row whose likely or very
  likely date (or a Milestone's chance of meeting its target) moved, old →
  new, then one `No move:` line;
- `## Inputs`: Throughput weeks, Story counts, ranges, finished Epics,
  start and in flight from `inputs.json`; `Depends on`, Milestone members and
  targets from `forecast.json`. Or `No input changed.`

With no shown version, one line saying so. Every date is copied from a
`forecast.json` or `inputs.json`. Writes nothing.

Exit 0, or 2 with stderr naming what can't be read.

Python 3.9 or later, standard library only.
"""

import json
import os
import re
import sys

sys.dont_write_bytecode = True

PLAN_DIR = re.compile(r"^plan-v(\d+)$")
SHOWN = re.compile(r"^Shown: (\d{4}-\d{2}-\d{2}) to (\S.*)$")


class Unreadable(Exception):
    """Something the script needs can't be read (exit 2)."""


def read_json(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except ValueError as e:
        raise Unreadable("%s: not valid JSON: %s" % (path, e))
    except OSError as e:
        raise Unreadable("%s: %s" % (path, e.strerror or e))


def version(plan_dir):
    m = PLAN_DIR.match(os.path.basename(os.path.normpath(plan_dir)))
    if m is None:
        raise Unreadable("%s: the plan folder is not named plan-v<N>" % plan_dir)
    return int(m.group(1))


def last_shown(project_dir, below):
    """(N, date, who) of the latest version under N=`below` with a `Shown:`
    line, its latest such line; or None."""
    plans = os.path.join(project_dir, "plans")
    found = []
    try:
        names = os.listdir(plans) if os.path.isdir(plans) else []
    except OSError as e:
        raise Unreadable("%s: %s" % (plans, e.strerror or e))
    for name in names:
        m = PLAN_DIR.match(name)
        record = os.path.join(plans, name, "plan.md")
        if m is None or int(m.group(1)) >= below or not os.path.isfile(record):
            continue
        try:
            with open(record, encoding="utf-8-sig") as f:
                shown = [SHOWN.match(l.rstrip()) for l in f]
        except (OSError, UnicodeDecodeError) as e:
            raise Unreadable("%s: %s" % (record, e))
        shown = [s for s in shown if s]
        if shown:
            found.append((int(m.group(1)), shown[-1].group(1), shown[-1].group(2)))
    return max(found) if found else None


def load(plan_dir):
    return (read_json(os.path.join(plan_dir, "forecast.json")),
            read_json(os.path.join(plan_dir, "inputs.json")))


# ---------------------------------------------------------------- dates

def date_or_state(row, key):
    """`row[key]`, or why it has none: "no date (<reason>)", or "done"."""
    if row.get(key):
        return row[key]
    return "no date (%s)" % row["no_date"] if row.get("no_date") else "done"


def chance(row):
    """A Milestone's chance of meeting its target as a whole percent, "no
    target", or None for a row that has no chance to give (undated, or an
    Epic)."""
    if row.get("target_met_share") is not None:
        return "%d%%" % round(row["target_met_share"] * 100)
    return "no target" if row.get("likely_finish") and "milestone" in row else None


def move_line(old, new, rid, label, old_v):
    """The one line naming how a row moved, or None when nothing did."""
    if old is None:
        if new.get("likely_finish"):
            return "- `%s` %s: new since %s, likely %s, very likely %s" % (
                rid, label, old_v, new["likely_finish"], new["very_likely_finish"])
        return "- `%s` %s: new since %s, %s" % (rid, label, old_v, date_or_state(new, "likely_finish"))
    if new is None:
        return "- `%s` %s: not in this version (was likely %s, very likely %s)" % (
            rid, label, date_or_state(old, "likely_finish"), date_or_state(old, "very_likely_finish"))
    parts = []
    for key, word in (("likely_finish", "likely"), ("very_likely_finish", "very likely")):
        a, b = date_or_state(old, key), date_or_state(new, key)
        if a != b:
            parts.append("%s %s → %s" % (word, a, b))
    a, b = chance(old), chance(new)
    if a != b and a and b:
        parts.append("chance of meeting the target %s → %s" % (a, b))
    return "- `%s` %s: %s" % (rid, label, "; ".join(parts)) if parts else None


def section(title, old_rows, new_rows, id_key, label_key, old_v):
    old = {r[id_key]: r for r in old_rows}
    new = {r[id_key]: r for r in new_rows}
    order = [r[id_key] for r in new_rows] + [i for i in old if i not in new]
    lines, still = [], []
    for rid in order:
        row = new.get(rid) or old[rid]
        line = move_line(old.get(rid), new.get(rid), rid, row.get(label_key, ""), old_v)
        if line:
            lines.append(line)
        else:
            still.append("`%s`" % rid)
    if still:
        lines.append("- No move: %s" % ", ".join(still))
    return ["", "## " + title] + (lines or ["- None."])


# ---------------------------------------------------------------- inputs

def ids(items):
    return ", ".join("`%s`" % i for i in items)


def adds_drops(a, b):
    parts = []
    if sorted(set(b) - set(a)):
        parts.append("adds " + ids(sorted(set(b) - set(a))))
    if sorted(set(a) - set(b)):
        parts.append("drops " + ids(sorted(set(a) - set(b))))
    return "; ".join(parts)


def story_counts(c):
    return "%d open, %d done, read %s" % (c["open"], c["done"], c["read"]) if c else "none"


def range_text(r):
    return "%d to %d" % (r["low"], r["high"]) if r else "none"


def input_lines(old_f, old_i, new_f, new_i):
    out = []
    ow = {w["week"]: w["done"] for w in old_i.get("throughput", {}).get("weeks", [])}
    nw = {w["week"]: w["done"] for w in new_i.get("throughput", {}).get("weeks", [])}
    if ow != nw:
        oh, nh = old_f.get("history", {}), new_f.get("history", {})
        parts = ["Throughput: %s → %s weeks of history (%s → %s)"
                 % (oh.get("weeks"), nh.get("weeks"), oh.get("status"), nh.get("status"))]
        for word, weeks in (("added", [w for w in sorted(nw) if w not in ow]),
                            ("dropped", [w for w in sorted(ow) if w not in nw])):
            if weeks:
                parts.append("%s %s" % (word, ", ".join("%s: %d" % (w, (nw if word == "added" else ow)[w])
                                                         for w in weeks)))
        changed = [w for w in sorted(nw) if w in ow and ow[w] != nw[w]]
        if changed:
            parts.append("changed " + ", ".join("%s: %d → %d" % (w, ow[w], nw[w]) for w in changed))
        out.append("- " + "; ".join(parts))
    a, b = old_i.get("throughput", {}).get("from"), new_i.get("throughput", {}).get("from")
    if a != b:
        out.append("- Throughput from: %s → %s" % (a, b))
    a, b = len(old_i.get("finished_epics", [])), len(new_i.get("finished_epics", []))
    if a != b:
        out.append("- Finished Epics: %d → %d" % (a, b))
    oc, nc = old_i.get("epics", {}), new_i.get("epics", {})
    for e in sorted(set(oc) | set(nc)):
        if oc.get(e) != nc.get(e):
            out.append("- `%s` Story counts: %s → %s" % (e, story_counts(oc.get(e)), story_counts(nc.get(e))))
    orr, nr = old_i.get("ranges", {}), new_i.get("ranges", {})
    for e in sorted(set(orr) | set(nr)):
        if orr.get(e) != nr.get(e):
            out.append("- `%s` range: %s → %s" % (e, range_text(orr.get(e)), range_text(nr.get(e))))
    oe = {r["epic"]: r for r in old_f.get("epics", [])}
    for r in new_f.get("epics", []):
        o = oe.get(r["epic"])
        if o and "depends_on" in o and "depends_on" in r and o["depends_on"] != r["depends_on"]:
            out.append("- `%s` Depends on: %s" % (r["epic"], adds_drops(o["depends_on"], r["depends_on"])))
    om = {m["milestone"]: m for m in old_f.get("milestones", [])}
    for m in new_f.get("milestones", []):
        o = om.get(m["milestone"])
        if not o:
            continue
        if sorted(o.get("members", [])) != sorted(m.get("members", [])):
            out.append("- `%s` members: %s" % (m["milestone"], adds_drops(o.get("members", []), m.get("members", []))))
        sources = ("target_source" in o and "target_source" in m)
        if o.get("target") != m.get("target") or sources and o["target_source"] != m["target_source"]:
            out.append("- `%s` target: %s → %s" % (m["milestone"], target(o), target(m)))
    for key, word in (("start", "Start"), ("in_flight", "In flight")):
        a, b = old_f.get(key), new_f.get(key)
        if a != b:
            out.append("- %s: %s → %s" % (word, a, b))
    return out or ["- No input changed."]


def target(m):
    if not m.get("target"):
        return "none"
    source = m.get("target_source")
    return "%s %s" % (m["target"], source) if source else m["target"]


# ---------------------------------------------------------------- main

def drift(project_dir, plan_dir):
    n = version(plan_dir)
    new_f, new_i = load(plan_dir)
    shown = last_shown(project_dir, n)
    if shown is None:
        return ["No Plan version before plan-v%d has a `Shown:` line, "
                "so there is nothing to measure drift against." % n]
    old_n, date, who = shown
    old_v = "plan-v%d" % old_n
    old_f, old_i = load(os.path.join(project_dir, "plans", old_v))
    try:
        return (["Drift from %s (shown %s to %s) to plan-v%d" % (old_v, date, who, n)]
                + section("Milestones", old_f["milestones"], new_f["milestones"], "milestone", "name", old_v)
                + section("Epics", old_f["epics"], new_f["epics"], "epic", "title", old_v)
                + ["", "## Inputs"] + input_lines(old_f, old_i, new_f, new_i))
    except (KeyError, TypeError, AttributeError) as e:
        raise Unreadable("%s or %s: not a Forecast: %s" % (old_v, plan_dir, e))


def main(argv):
    if len(argv) != 3:
        print("usage: drift.py <project dir> <plan dir>", file=sys.stderr)
        return 2
    try:
        lines = drift(argv[1], argv[2])
    except Unreadable as e:
        print("Can't read: %s" % e, file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
