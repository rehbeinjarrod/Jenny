#!/usr/bin/env python3
"""Throughput: a team's weekly count of finished work, and its finished Epics'
Story counts, from what the Atlassian MCP returned for Jira's done items.

    python3 throughput.py <jira.json> --today YYYY-MM-DD [--leave-out KEY,...] [--into <inputs.json>]

`<jira.json>` holds the two searches `jira.md` names, as the MCP returned them:

    {"done": [<every issue of every page of the done-items search>],
     "never_in_progress": ["<key of each issue the never-in-progress search returned>"]}

Each issue is Jira's own shape: `key`, and `fields` with `issuetype`
(`hierarchyLevel`), `status` (`name`, `statusCategory.key`), `resolution`
(`name`, or null), `resolutiondate`, `statuscategorychangedate`, `created`,
`labels` and, for a child of an Epic, `parent` (`key`, `fields.status`).

An item counts in the week (by its Monday) of its `resolutiondate`, or its
`statuscategorychangedate` when no resolution is set. Left out, each with its
reason: an item below standard level or not done; won't do, by a resolution
off the allow-list, a won't-do status or a won't-do label; closed without
work (never in progress, and done within an hour of being made); done before
the 52 weeks read, or this week, which has not ended; and each key the
Operator named with `--leave-out`. A never-in-progress item that is not
closed without work counts, and is named so the Operator can decide on it.

The weeks run from the Monday of the oldest counted item (or 51 weeks
before the last full week, when older items were read) to the last full week before `--today`, with
weeks of 0 kept. A finished Epic is a `parent` in the done status category
and not won't do; its Story count is every standard-level child of it read
that was real work, counted in the weeks or done outside them.

Prints, as JSON: `window` (`from`, `to` Mondays), `weeks`, `finished_epics`,
`never_in_progress` (counted, with each done date), `left_out` (with
reasons) and `counted`. With `--into`, also sets `throughput.weeks` and
`finished_epics` in that `inputs.json`, keeping everything else.

Exit 0: done. Exit 1: stderr names each input problem, one per line, and
nothing is printed or written. Exit 2: something can't be read or written.

Python 3.9 or later, standard library only.
"""

import datetime
import json
import re
import sys

sys.dont_write_bytecode = True

# jira.md's Done JQL repeats these two: `updated >= -52w` and `resolution in (Done, Fixed)`.
WEEKS_READ = 52
RESOLUTIONS = {"done", "fixed"}   # the allow-list, normalised: any other resolution is won't do
WONT_DO = {"wontdo", "wontfix", "cancelled", "canceled", "duplicate", "rejected", "abandoned", "notdoing"}
NO_WORK = datetime.timedelta(hours=1)


class Unreadable(Exception):
    pass


def norm(name):
    return re.sub(r"[^a-z]", "", name.lower())


def parse_time(v):
    if not isinstance(v, str):
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.datetime.strptime(v, fmt)
        except ValueError:
            pass
    try:
        return datetime.datetime.strptime(v[:10], "%Y-%m-%d")
    except ValueError:
        return None


def monday(d):
    return d - datetime.timedelta(days=d.weekday())


def name_of(obj):
    return obj.get("name") if isinstance(obj, dict) else None


def category(status):
    sc = status.get("statusCategory") if isinstance(status, dict) else None
    return sc.get("key") if isinstance(sc, dict) else None


def read_jira(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise Unreadable("%s: %s" % (path, e.strerror or e))
    except UnicodeDecodeError:
        raise Unreadable("%s: not UTF-8 text" % path)
    try:
        data = json.loads(text)
    except ValueError as e:
        return None, ["jira.json: not valid JSON: %s" % e]
    if not isinstance(data, dict) or not isinstance(data.get("done"), list):
        return None, ["jira.json: `done` is missing or not a list"]
    never = data.get("never_in_progress", [])
    if not isinstance(never, list) or not all(isinstance(k, str) for k in never):
        return None, ["jira.json: `never_in_progress` is not a list of keys"]
    problems = []
    for i, issue in enumerate(data["done"]):
        key = issue.get("key") if isinstance(issue, dict) else None
        if not isinstance(key, str):
            problems.append("jira.json: `done[%d]` has no `key`" % i)
        elif not isinstance(issue.get("fields"), dict):
            problems.append("jira.json: `done[%d]` (%s) has no `fields`" % (i, key))
        else:
            for field, kind, shape in SHAPES:
                v = issue["fields"].get(field)
                if v is not None and not isinstance(v, kind):
                    problems.append("jira.json: `done[%d]` (%s): `%s` is not %s" % (i, key, field, shape))
    return data, problems


SHAPES = (("issuetype", dict, "an object"), ("status", dict, "an object"), ("resolution", dict, "an object or null"),
          ("parent", dict, "an object"), ("labels", list, "a list"))


def wont_do(status, resolution, labels):
    """The won't-do reason of an item or Epic, or None."""
    if resolution is not None and norm(resolution) not in RESOLUTIONS:
        return "won't do: resolution %s" % resolution
    if status and norm(status) in WONT_DO:
        return "won't do: status %s" % status
    for label in labels or []:
        if isinstance(label, str) and norm(label) in WONT_DO:
            return "won't do: label %s" % label
    return None


def gap(later, earlier):
    """later - earlier, comparing two naive times when either is naive."""
    if (later.tzinfo is None) != (earlier.tzinfo is None):
        later, earlier = later.replace(tzinfo=None), earlier.replace(tzinfo=None)
    return later - earlier


# What `classify` makes of an item: counted in a week; real work done before
# the weeks read or in this week (still a Story of its Epic); or not work.
COUNTED, BEFORE, THIS_WEEK, NOT_WORK = "counted", "before", "this week", "not work"


def classify(issue, never, leave_out, first, last):
    """(kind, done date or None, reason or None)."""
    f = issue["fields"]
    if (f.get("issuetype") or {}).get("hierarchyLevel", 0) != 0:
        return NOT_WORK, None, "not a standard-level item"
    status = f.get("status") or {}
    if category(status) != "done":
        return NOT_WORK, None, "not done: status %s" % name_of(status)
    resolution = name_of(f.get("resolution"))
    reason = wont_do(name_of(status), resolution, f.get("labels"))
    if reason:
        return NOT_WORK, None, reason
    done_at = parse_time(f.get("resolutiondate") if resolution is not None else None) \
        or parse_time(f.get("statuscategorychangedate"))
    if done_at is None:
        return NOT_WORK, None, "no done date"
    made = parse_time(f.get("created"))
    if issue["key"] in never and made is not None and gap(done_at, made) <= NO_WORK:
        return NOT_WORK, None, "closed without work: never in progress, done within an hour of being made"
    if issue["key"] in leave_out:
        return NOT_WORK, None, "left out by the Operator"
    week = monday(done_at.date())
    if week > last:
        return THIS_WEEK, None, "done this week, which has not ended"
    if week < first:
        return BEFORE, None, "done before the %d weeks read" % WEEKS_READ
    return COUNTED, done_at.date(), None


def finished_epic(parent):
    """The key of a parent Epic that is finished (done, and not won't do), or None."""
    if not isinstance(parent, dict) or not isinstance(parent.get("key"), str):
        return None
    status = (parent.get("fields") or {}).get("status")
    if category(status) != "done" or wont_do(name_of(status), None, None):
        return None
    return parent["key"]


def work_out(data, today, leave_out):
    last = monday(today) - datetime.timedelta(weeks=1)
    earliest = last - datetime.timedelta(weeks=WEEKS_READ - 1)
    never = set(data.get("never_in_progress", []))
    counted, left_out, never_counted, children = [], [], [], {}
    before = False
    for issue in data["done"]:
        kind, d, reason = classify(issue, never, leave_out, earliest, last)
        if kind != NOT_WORK:
            epic = finished_epic(issue["fields"].get("parent"))
            if epic:
                children[epic] = children.get(epic, 0) + 1
        if kind != COUNTED:
            left_out.append({"key": issue["key"], "reason": reason})
            before = before or kind == BEFORE
            continue
        counted.append(d)
        if issue["key"] in never:
            never_counted.append({"key": issue["key"], "done": d.isoformat()})
    weeks, window = [], None
    if counted:
        first = earliest if before else monday(min(counted))
        by_week = {}
        for d in counted:
            by_week[monday(d)] = by_week.get(monday(d), 0) + 1
        w = first
        while w <= last:
            weeks.append({"week": w.isoformat(), "done": by_week.get(w, 0)})
            w += datetime.timedelta(weeks=1)
        window = {"from": first.isoformat(), "to": last.isoformat()}
    return {
        "window": window,
        "weeks": weeks,
        "finished_epics": [{"key": k, "stories": n} for k, n in sorted(children.items(), key=lambda kv: key_order(kv[0]))],
        "never_in_progress": never_counted,
        "left_out": left_out,
        "counted": len(counted),
    }


def key_order(key):
    m = re.match(r"^(.*?)(\d+)$", key)
    return (m.group(1), int(m.group(2))) if m else (key, 0)


def into(path, result):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise Unreadable("%s: %s" % (path, e.strerror or e))
    except UnicodeDecodeError:
        raise Unreadable("%s: not UTF-8 text" % path)
    except ValueError as e:
        return ["%s: not valid JSON: %s" % (path, e)]
    if not isinstance(data, dict):
        return ["%s: is not a JSON object" % path]
    tp = data.get("throughput")
    if not isinstance(tp, dict):
        tp = data["throughput"] = {}
    tp["weeks"] = result["weeks"]
    data["finished_epics"] = result["finished_epics"]
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    except OSError as e:
        raise Unreadable("%s: %s" % (path, e.strerror or e))
    return []


USAGE = "usage: throughput.py <jira.json> --today YYYY-MM-DD [--leave-out KEY,...] [--into <inputs.json>]"


def parse_args(argv):
    if len(argv) < 2:
        return None
    opts, rest = {"--today": None, "--leave-out": "", "--into": None}, argv[2:]
    while rest:
        if rest[0] not in opts or len(rest) < 2:
            return None
        opts[rest[0]] = rest[1]
        rest = rest[2:]
    try:
        today = datetime.date.fromisoformat(opts["--today"] or "")
    except ValueError:
        return None
    leave = {k.strip() for k in opts["--leave-out"].split(",") if k.strip()}
    return argv[1], today, leave, opts["--into"]


def main(argv):
    args = parse_args(argv)
    if args is None:
        print(USAGE, file=sys.stderr)
        return 2
    path, today, leave_out, into_path = args
    try:
        data, problems = read_jira(path)
        if not problems:
            read = {i["key"] for i in data["done"]}
            problems = ["--leave-out: %s is not a done item read" % k for k in sorted(leave_out - read, key=key_order)]
        if not problems:
            result = work_out(data, today, leave_out)
            if into_path:
                problems = into(into_path, result)
    except Unreadable as e:
        print("Can't read: %s" % e, file=sys.stderr)
        return 2
    for p in problems:
        print(p, file=sys.stderr)
    if problems:
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
