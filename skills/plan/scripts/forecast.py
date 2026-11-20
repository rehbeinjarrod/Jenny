#!/usr/bin/env python3
"""Forecast: a Project's likely and very likely finish dates, worked out from
Throughput and Story counts by a seeded Monte Carlo, with each Epic's share of
trials on the critical path.

    python3 <skills>/plan/scripts/forecast.py <project dir> <plan dir>
    python3 <skills>/plan/scripts/forecast.py --check <plan dir>

`<project dir>` is `projects/<slug>`; `<plan dir>` is its
`plans/plan-v<N>`, and N is the seed.

Reads the dependency graph and Milestones from the Project's records:

- `epics/*/epic.md`: `Epic:`, `Feature:`, `Enables:` (a Technical Enabler),
  `## Covers`, `## Depends on` and `## Enabler Stories` lines.
- `milestones/*.md`: `Milestone:`, `Target:` and `## Members`. A target
  `derived from plan-v<N>` is the very likely date that frozen Plan version's
  `forecast.json` gave the Milestone.

Reads everything else from `<plan dir>/inputs.json`:

    {
      "throughput": {"from": "<JQL and run date, or typed>",
                     "weeks": [{"week": "YYYY-MM-DD", "done": <Stories>}, ...]},
      "finished_epics": [{"key": "<Jira key or name>", "stories": <n>}, ...],
      "epics": {"<EPC ID>": {"open": <n>, "done": <n>, "read": "YYYY-MM-DD"}},
      "ranges": {"<EPC ID>": {"low": <n>, "high": <n>}},
      "start": "YYYY-MM-DD",
      "in_flight": <k, default 2>
    }

`epics` holds each handed-off Epic's Story counts; one with no open Stories
is done, and one with no entry is not started. `ranges` holds engineers' low
to high Story counts. `finished_epics` is resampled for an Epic with neither.

Model: calendar weeks, each date the Friday of its week. One team, and up to
k Epics in flight sharing a week's Throughput equally, in order: topological
by dependencies, then earliest Milestone, then Epic ID. An Epic's Enabler
Stories are done first, so a dependency on one waits only for that Epic's
Enabler Stories. 10,000 trials, every draw through a private
`random.Random(<Plan version>).random()`.

Writes `<plan dir>/forecast.json`, which also keeps each Epic's `depends_on`
(the Epics it waits on) and each Milestone's `target_source`, so the Drift
script can compare two versions; and the Gantt drawn from it in Mermaid:
`gantt.mmd`, or above 20 dated Epics one chapter per Milestone,
`gantt-<MIL ID>.mmd` (and `gantt-other.mmd` for Epics in no Milestone). No
Epic dated, no Gantt. The chart is compact, one section per row, explicit
dates only. Epics are grouped under the first Milestone holding them,
Technical Enablers first as "(groundwork)"; each Epic row is dark from its
likely start to its likely finish, with an `active` tail to its very likely
finish, and `crit` when critical. Each group ends with its Milestone's row: a
diamond at the very likely date, and a red one at any target (one red
diamond when both fall on the same day). An undated Epic or Milestone has no
row.

Mermaid mistakes fail silently, so every Gantt is read back and checked
against the Forecast before anything is written; `--check` does the same for
a plan folder's `forecast.json` and `gantt*.mmd` as they stand.

Exit 0: a good Forecast, which may still leave Epics with no date (each says
why). Exit 1: stderr names each input problem (or, a line starting `gantt`,
a chart that doesn't match the Forecast), one per line, and nothing is
written. Exit 2: something can't be read or written, named on stderr.

Python 3.9 or later, standard library only.
"""

import datetime
import heapq
import json
import os
import random
import re
import sys

sys.dont_write_bytecode = True

TRIALS = 10000
HORIZON = 260          # Throughput draws per trial; a longer trial wraps round
MAX_WEEKS = 5200       # a trial still running after 100 years stops there
WINDOW = 26            # weeks of Throughput history used
NO_DATES_UNDER = 5     # weeks of history below which nothing is dated
NORMAL_FROM = 11       # weeks of history from which dates are not early
MIN_FINISHED = 5       # finished Epics needed to resample a Story count
DEFAULT_IN_FLIGHT = 2
EPS = 1e-9

ID = r"[A-Z]{2,4}-(?:REQ|EPC|ENS|FEA|MIL)-\d+"
HEADER = re.compile(r"^([A-Z][A-Za-z' -]*):(?: (.*)|)$")
TITLE = re.compile(r"^# (\S+) · (.+)$")
ENS_LINE = re.compile(r"^- \*\*([A-Z]{2,4}-ENS-\d+)\*\* (\S.*?) · Enables: (.+?) · Depends on: (.+)$")
DEP_LINE = re.compile(r"^- ([A-Z]{2,4}-(?:REQ|EPC|ENS)-\d+)\b")
MEMBER = re.compile(r"^- ([A-Z]{2,4}-FEA-\d+)\b")
TARGET_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (set by .+)$")
TARGET_DERIVED = re.compile(r"^derived from (plan-v\d+)$")
PLAN_DIR = re.compile(r"^plan-v(\d+)$")


class Unreadable(Exception):
    """Something the script needs can't be read (exit 2)."""


# ---------------------------------------------------------------- records

def read_text(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return f.read()
    except UnicodeDecodeError:
        raise Unreadable("%s: not UTF-8 text" % path)
    except OSError as e:
        raise Unreadable("%s: %s" % (path, e.strerror or e))


def header_block(lines):
    """{key: value} for the `Key: value` lines after the title."""
    block, i = {}, 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines):
        m = HEADER.match(lines[i])
        if not m:
            break
        block.setdefault(m.group(1), (m.group(2) or "").strip())
        i += 1
    return block


def sections(lines):
    """{heading: [(line number, line)]} for each `## ` section."""
    out, name = {}, None
    for n, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if line.startswith("## "):
            name = line[3:].strip()
            out.setdefault(name, [])
        elif name is not None:
            out[name].append((n, line))
    return out


def id_list(value):
    """The comma-separated IDs in `value`, or none for `none`."""
    value = value.strip()
    return [] if value.lower() == "none" else [v.strip() for v in value.split(",") if v.strip()]


class Epic:
    def __init__(self, eid, title, feature, path):
        self.id = eid
        self.title = title
        self.feature = feature
        self.path = path
        self.enabler = False   # a Technical Enabler
        self.enables = []      # a Technical Enabler's `Enables:` Requirement IDs
        self.covers = []       # Requirement IDs under `## Covers`
        self.depends = []      # (line number, ID) under `## Depends on`
        self.ens = []          # (line number, ENS ID, [Enables], [Depends on])


class Milestone:
    def __init__(self, mid, name, target, source, members, path):
        self.id = mid
        self.name = name
        self.target = target   # a date string, or None
        self.source = source   # "set by <name>", "derived from plan-v<N>", or None
        self.members = members
        self.path = path


def id_number(i):
    return int(i.rsplit("-", 1)[1])


def read_project(project_dir):
    """(epics by ID, milestones by ID, problems)."""
    if not os.path.isdir(project_dir):
        raise Unreadable("%s: no such Project folder" % project_dir)
    problems, epics, milestones = [], {}, {}
    epics_dir = os.path.join(project_dir, "epics")
    for name in sorted(os.listdir(epics_dir)) if os.path.isdir(epics_dir) else []:
        path = os.path.join(epics_dir, name, "epic.md")
        if not os.path.isfile(path):
            continue
        lines = read_text(path).splitlines()
        block = header_block(lines)
        title = TITLE.match(lines[0]) if lines else None
        folder = re.match(r"[A-Z]{2,4}-EPC-\d+", name)
        eid = block.get("Epic") or (title.group(1) if title else folder.group(0) if folder else name)
        epic = Epic(eid, title.group(2).strip() if title else "", block.get("Feature", ""), path)
        if eid in epics:
            problems.append("%s: `%s` is also %s" % (path, eid, epics[eid].path))
            continue
        if block.get("Technical Enabler") == "yes":
            epic.enabler = True
            epic.enables = [i for i in id_list(block.get("Enables", "none")) if "-REQ-" in i]
        secs = sections(lines)
        for _, line in secs.get("Covers", []):
            epic.covers += re.findall(r"[A-Z]{2,4}-REQ-\d+", line)
        for n, line in secs.get("Depends on", []):
            if not line.startswith("- "):
                continue
            m = DEP_LINE.match(line)
            if m is None:
                problems.append("%s:%d: `%s` names no Requirement, Epic or Enabler Story ID first" % (path, n, line))
            else:
                epic.depends.append((n, m.group(1)))
        for n, line in secs.get("Enabler Stories", []):
            m = ENS_LINE.match(line)
            if m:
                epic.ens.append((n, m.group(1), id_list(m.group(3)), id_list(m.group(4))))
        epics[eid] = epic
    mil_dir = os.path.join(project_dir, "milestones")
    for name in sorted(os.listdir(mil_dir)) if os.path.isdir(mil_dir) else []:
        if not name.endswith(".md") or not re.match(r"[A-Z]{2,4}-MIL-\d+", name):
            continue
        path = os.path.join(mil_dir, name)
        lines = read_text(path).splitlines()
        block = header_block(lines)
        title = TITLE.match(lines[0]) if lines else None
        mid = block.get("Milestone") or re.match(r"[A-Z]{2,4}-MIL-\d+", name).group(0)
        target, source = None, None
        m = TARGET_DATE.match(block.get("Target", ""))
        if m:
            target, source = m.group(1), m.group(2)
        m = TARGET_DERIVED.match(block.get("Target", ""))
        if m:
            source = block["Target"]
            target, problem = derived_target(project_dir, m.group(1), mid)
            if problem:
                problems.append("%s: `Target: %s`: %s" % (path, source, problem))
        members = []
        for _, line in sections(lines).get("Members", []):
            m = MEMBER.match(line)
            if m:
                members.append(m.group(1))
        milestones[mid] = Milestone(mid, title.group(2).strip() if title else "",
                                    target, source, members, path)
    return epics, milestones, problems


def derived_target(project_dir, version, mid):
    """(date, problem): the very likely date `plans/<version>/forecast.json`
    gave Milestone `mid`, or a problem saying why there is none."""
    path = os.path.join(project_dir, "plans", version, "forecast.json")
    if not os.path.isfile(path):
        return None, "there is no plans/%s/forecast.json" % version
    try:
        rows = json.loads(read_text(path)).get("milestones", [])
        date = next((m.get("very_likely_finish") for m in rows if m.get("milestone") == mid), None)
    except (ValueError, AttributeError):
        raise Unreadable("%s: not a Forecast" % path)
    if not date:
        return None, "%s gives `%s` no very likely date" % (version, mid)
    return date, None


# ---------------------------------------------------------------- graph

def build_graph(epics, milestones):
    """({Epic ID: {dependency Epic ID: "all" | "enablers"}},
    {Milestone ID: [Epic IDs]}, {Feature ID: [Epic IDs]}, problems).

    "all" waits for the whole Epic; "enablers" for its Enabler Stories."""
    problems = []
    covered_by = {}
    for e in epics.values():
        for r in e.covers:
            covered_by.setdefault(r, e.id)
    ens_epic = {ens: e.id for e in epics.values() for _, ens, _, _ in e.ens}
    deps = {eid: {} for eid in epics}

    def add(eid, dep, kind):
        if dep == eid:
            return
        if deps[eid].get(dep) != "all":
            deps[eid][dep] = kind

    def resolve(epic, where, ref, whole):
        """The Epic and kind `ref` (a REQ, EPC or ENS ID) stands for."""
        if "-EPC-" in ref:
            if ref not in epics:
                problems.append("%s: `Depends on`: `%s` is not an Epic in the Project" % (where, ref))
                return
            add(epic.id, ref, "all")
        elif "-ENS-" in ref:
            if ref not in ens_epic:
                problems.append("%s: `Depends on`: `%s` is not an Enabler Story in the Project" % (where, ref))
                return
            add(epic.id, ens_epic[ref], "enablers")
        elif "-REQ-" in ref and whole:
            if ref not in covered_by:
                problems.append("%s: `Depends on`: no Epic covers `%s`" % (where, ref))
                return
            add(epic.id, covered_by[ref], "all")
        else:
            problems.append("%s: `Depends on`: `%s` is not an Enabler Story or Epic" % (where, ref))

    for eid in sorted(epics):
        e = epics[eid]
        for n, ref in e.depends:
            resolve(e, "%s:%d" % (e.path, n), ref, True)
        for n, _, enables, depends in e.ens:
            for ref in depends:
                resolve(e, "%s:%d" % (e.path, n), ref, False)
            for r in enables:
                other = covered_by.get(r)
                if other and other != eid:
                    add(other, eid, "enablers")
        for r in e.enables:
            other = covered_by.get(r)
            if other and other != eid:
                add(other, eid, "all")

    by_feature = {}
    for e in epics.values():
        by_feature.setdefault(e.feature, []).append(e.id)
    members = {}
    for mid in sorted(milestones, key=id_number):
        m = milestones[mid]
        if not m.members:
            problems.append("%s: `%s` has no members: `## Members` lists no Feature" % (m.path, mid))
            continue
        members[mid] = sorted({e for fea in m.members for e in by_feature.get(fea, [])})
    return deps, members, by_feature, problems


def find_cycles(deps):
    """Each cycle once, as `A → B → A`, found by depth-first search."""
    colour, stack, cycles, seen = {}, [], [], set()

    def visit(n):
        colour[n] = 1
        stack.append(n)
        for d in sorted(deps[n]):
            if colour.get(d) == 1:
                loop = stack[stack.index(d):]
                key = frozenset(loop)
                if key not in seen:
                    seen.add(key)
                    cycles.append(" → ".join(list(reversed(loop)) + [loop[-1]]))
            elif d not in colour:
                visit(d)
        stack.pop()
        colour[n] = 2

    for n in sorted(deps):
        if n not in colour:
            visit(n)
    return cycles


def plan_order(deps, members):
    """Epic IDs in plan order: topological by dependencies, ties by earliest
    Milestone, then ID. The graph has no cycles."""
    rank = {}
    for mid, ids in members.items():
        for eid in ids:
            rank[eid] = min(rank.get(eid, float("inf")), id_number(mid))
    key = lambda eid: (rank.get(eid, float("inf")), id_number(eid), eid)
    waiting = {eid: len(d) for eid, d in deps.items()}
    users = {eid: [] for eid in deps}
    for eid, d in deps.items():
        for p in d:
            users[p].append(eid)
    ready = [(key(eid), eid) for eid, n in waiting.items() if n == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        _, eid = heapq.heappop(ready)
        order.append(eid)
        for u in users[eid]:
            waiting[u] -= 1
            if waiting[u] == 0:
                heapq.heappush(ready, (key(u), u))
    return order


# ---------------------------------------------------------------- inputs

def is_count(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def parse_date(v):
    if not isinstance(v, str):
        return None
    try:
        return datetime.date.fromisoformat(v)
    except ValueError:
        return None


def read_inputs(path, epics):
    """(inputs, problems), every problem prefixed `inputs.json`."""
    text = read_text(path)
    try:
        data = json.loads(text)
    except ValueError as e:
        return None, ["inputs.json: not valid JSON: %s" % e]
    problems = []
    if not isinstance(data, dict):
        return None, ["inputs.json: is not a JSON object"]
    known = {"throughput", "finished_epics", "epics", "ranges", "start", "in_flight"}
    problems += ["inputs.json: `%s` is not a known key" % k for k in sorted(set(data) - known)]

    tp = data.get("throughput")
    weeks = []
    if not isinstance(tp, dict):
        problems.append("inputs.json: `throughput` is missing or not an object")
    else:
        if not isinstance(tp.get("from"), str) or not tp["from"].strip():
            problems.append("inputs.json: `throughput.from` is missing: where the weeks came from")
        if not isinstance(tp.get("weeks"), list):
            problems.append("inputs.json: `throughput.weeks` is missing or not a list")
        else:
            seen = {}
            for i, w in enumerate(tp["weeks"]):
                d = parse_date(w.get("week")) if isinstance(w, dict) else None
                if d is None or not is_count(w.get("done")):
                    problems.append('inputs.json: `throughput.weeks[%d]` is not {"week": "YYYY-MM-DD", "done": <Stories>}' % i)
                    continue
                monday = d - datetime.timedelta(days=d.weekday())
                if monday in seen:
                    problems.append("inputs.json: `throughput.weeks[%d]`: the week of %s is also `throughput.weeks[%d]`"
                             % (i, d, seen[monday]))
                else:
                    seen[monday] = i
                    weeks.append((monday, w["done"]))

    finished = []
    fe = data.get("finished_epics", [])
    if not isinstance(fe, list):
        problems.append("inputs.json: `finished_epics` is not a list")
    else:
        for i, f in enumerate(fe):
            if not isinstance(f, dict) or not is_count(f.get("stories")) or f["stories"] == 0:
                problems.append('inputs.json: `finished_epics[%d]` is not {"key": "<key>", "stories": <n over 0>}' % i)
            else:
                finished.append(f["stories"])

    counts = {}
    ep = data.get("epics", {})
    if not isinstance(ep, dict):
        problems.append("inputs.json: `epics` is not an object")
    else:
        for eid in sorted(ep):
            c = ep[eid]
            if eid not in epics:
                problems.append("inputs.json: `epics`: `%s` is not an Epic in the Project" % eid)
            elif not isinstance(c, dict) or not is_count(c.get("open")) or not is_count(c.get("done")) \
                    or parse_date(c.get("read")) is None:
                problems.append('inputs.json: `epics.%s` is not {"open": <n>, "done": <n>, "read": "YYYY-MM-DD"}' % eid)
            else:
                counts[eid] = c

    ranges = {}
    rg = data.get("ranges", {})
    if not isinstance(rg, dict):
        problems.append("inputs.json: `ranges` is not an object")
    else:
        for eid in sorted(rg):
            r = rg[eid]
            if eid not in epics:
                problems.append("inputs.json: `ranges`: `%s` is not an Epic in the Project" % eid)
            elif not isinstance(r, dict) or not is_count(r.get("low")) or not is_count(r.get("high")) \
                    or r["low"] > r["high"]:
                problems.append('inputs.json: `ranges.%s` is not {"low": <n>, "high": <n, not under low>}' % eid)
            else:
                ranges[eid] = (r["low"], r["high"])

    start = parse_date(data.get("start"))
    if start is None:
        problems.append('inputs.json: `start` is missing or not a date, "YYYY-MM-DD"')
    k = data.get("in_flight", DEFAULT_IN_FLIGHT)
    if not is_count(k) or k == 0:
        problems.append("inputs.json: `in_flight` is not a whole number over 0")
    if problems:
        return None, problems
    return {"from": tp["from"], "weeks": sorted(weeks), "finished": finished, "counts": counts,
            "ranges": ranges, "start": start, "in_flight": k}, []


# ---------------------------------------------------------------- model

def history(weeks):
    """(Stories done in each calendar week of the window, oldest first,
    status). The window is the last 26 calendar weeks up to the latest week
    given, from the first week given; a week missing in between finished no
    Stories."""
    if not weeks:
        return [], "too short"
    done = dict(weeks)
    first, latest = weeks[0][0], weeks[-1][0]
    span = min(WINDOW, (latest - first).days // 7 + 1)
    window = [done.get(latest - datetime.timedelta(weeks=n), 0) for n in reversed(range(span))]
    if len(window) < NO_DATES_UNDER:
        status = "too short"
    elif len(window) < NORMAL_FROM:
        status = "early"
    else:
        status = "normal"
    return window, status


def count_sources(epics, inputs):
    """{Epic ID: "done" | "stories" | "range" | "history" | None}."""
    out = {}
    for eid in epics:
        c = inputs["counts"].get(eid)
        if c is not None:
            out[eid] = "done" if c["open"] == 0 else "stories"
        elif eid in inputs["ranges"]:
            out[eid] = "range"
        elif len(inputs["finished"]) >= MIN_FINISHED:
            out[eid] = "history"
        else:
            out[eid] = None
    return out


def simulate(order, deps, epics, inputs, sources, window, seed):
    """Per trial, each simulated Epic's start week, finish week and whether it
    sat on the critical path. Weeks count from 0, the start date's week.

    Returns {Epic ID: (starts, finishes, critical count)}."""
    rng = random.Random(seed)
    draw = rng.random
    k = inputs["in_flight"]
    all_ids = sorted(epics)
    sim = [e for e in order if sources[e] not in (None, "done")]
    done_ids = {e for e in order if sources[e] == "done"}
    n_ens = {e: len(epics[e].ens) for e in epics}
    finished, n_finished = inputs["finished"], len(inputs["finished"])
    n_window = len(window)
    starts = {e: [] for e in sim}
    finishes = {e: [] for e in sim}
    critical = {e: 0 for e in sim}

    for _ in range(TRIALS):
        # One draw per Epic, then a fixed run of Throughput draws, so a change
        # to one Epic's count leaves every other draw where it was.
        u = {e: draw() for e in all_ids}
        tp = [window[int(draw() * n_window)] for _ in range(HORIZON)]
        ens_left, rest_left = {}, {}
        for e in sim:
            src = sources[e]
            if src == "stories":
                c = inputs["counts"][e]
                ens = min(max(0, n_ens[e] - c["done"]), c["open"])
                total = c["open"]
            else:
                if src == "range":
                    low, high = inputs["ranges"][e]
                    total = low + int(u[e] * (high - low + 1))
                else:
                    total = finished[int(u[e] * n_finished)]
                ens = n_ens[e]
                total = max(total, ens)
            ens_left[e], rest_left[e] = float(ens), float(total - ens)
        ens_week = {e: -1 for e in done_ids}
        finish = {e: -1 for e in done_ids}
        for e in sim:
            if ens_left[e] <= EPS:
                ens_week[e] = -1
        start = {}
        active = []
        w = 0
        while len(finish) < len(sim) + len(done_ids) and w < MAX_WEEKS:
            for e in sim:
                if len(active) >= k:
                    break
                if e in start:
                    continue
                if all(done_before((finish if kind == "all" else ens_week).get(p), w)
                       for p, kind in deps[e].items()):
                    start[e] = w
                    active.append(e)
            # A week's Throughput is shared equally; what a closing Epic
            # leaves goes to the others. An Epic that becomes ready mid-week
            # starts the next week, so Throughput left when all close is lost.
            capacity = float(tp[w % HORIZON])
            running = list(active)
            while running and capacity > EPS:
                share = capacity / len(running)
                closing = [e for e in running if ens_left[e] + rest_left[e] <= share + EPS]
                if closing:
                    for e in closing:
                        capacity -= ens_left[e] + rest_left[e]
                        ens_left[e] = rest_left[e] = 0.0
                        running.remove(e)
                    continue
                for e in running:
                    take = min(share, ens_left[e])
                    ens_left[e] -= take
                    rest_left[e] -= share - take
                capacity = 0.0
            for e in list(active):
                if ens_left[e] <= EPS and e not in ens_week:
                    ens_week[e] = w
                if ens_left[e] + rest_left[e] <= EPS:
                    finish[e] = w
                    active.remove(e)
            w += 1
        for e in sim:
            if e not in start:
                start[e] = w
            if e not in finish:
                finish[e] = w
            starts[e].append(start[e])
            finishes[e].append(finish[e])
        # The critical path: back from the latest-finishing Epic through the
        # latest-finishing dependency each time.
        node = max(sim, key=lambda e: finish[e]) if sim else None
        while node is not None:
            critical[node] += 1
            best, best_week = None, None
            for p, kind in sorted(deps[node].items()):
                if p in done_ids:
                    continue
                pw = finish[p] if kind == "all" else ens_week.get(p, -1)
                if best_week is None or pw > best_week:
                    best, best_week = p, pw
            node = best
    return {e: (starts[e], finishes[e], critical[e]) for e in sim}


def done_before(week, w):
    """Whether work finished in `week` (None: not yet) is done before week `w`."""
    return week is not None and week < w


def percentile(values, p):
    """Nearest-rank percentile of `values`."""
    s = sorted(values)
    i = max(0, -(-len(s) * p // 100) - 1)
    return s[int(i)]


def friday(d):
    return d + datetime.timedelta(days=4 - d.weekday())


def week_date(start, week):
    return (friday(start) + datetime.timedelta(weeks=week)).isoformat()


# ---------------------------------------------------------------- forecast

def downstream_of(roots, deps):
    """Every Epic that waits, directly or not, on one in `roots`."""
    out = set(roots)
    grew = True
    while grew:
        grew = False
        for e, d in deps.items():
            if e not in out and any(p in out for p in d):
                out.add(e)
                grew = True
    return out


def forecast(project_dir, plan_dir):
    """(forecast dict, {Gantt file name: Mermaid text}, problems)."""
    m = PLAN_DIR.match(os.path.basename(os.path.normpath(plan_dir)))
    if not os.path.isdir(plan_dir):
        raise Unreadable("%s: no such plan folder" % plan_dir)
    epics, milestones, problems = read_project(project_dir)
    deps, members, by_feature, more = build_graph(epics, milestones)
    problems += more
    problems += ["a cycle in `Depends on`: %s" % c for c in find_cycles(deps)]
    if m is None:
        problems.append("%s: the plan folder is not named plan-v<N>, and N is the seed" % plan_dir)
    inputs_path = os.path.join(plan_dir, "inputs.json")
    if not os.path.isfile(inputs_path):
        raise Unreadable("%s: no such file" % inputs_path)
    inputs, more = read_inputs(inputs_path, epics)
    problems += more
    if problems:
        return None, {}, problems

    seed = int(m.group(1))
    order = plan_order(deps, members)
    window, status = history(inputs["weeks"])
    sources = count_sources(epics, inputs)
    reasons = {}
    if status == "too short":
        for e in order:
            reasons[e] = "under %d weeks of Throughput history" % NO_DATES_UNDER
    elif sum(window) == 0:
        for e in order:
            reasons[e] = "no Stories finished in the Throughput window"
    else:
        uncounted = sorted(e for e in order if sources[e] is None)
        for e in uncounted:
            reasons[e] = ("no Story count: fewer than %d finished Epics and no engineer range"
                          % MIN_FINISHED)
        for e in sorted(downstream_of(uncounted, deps) - set(uncounted)):
            reasons[e] = "waits on %s, which has no date" % ", ".join(
                sorted(p for p in upstream_of(e, deps) if p in uncounted))
    live_sources = {e: (sources[e] if e not in reasons else None) for e in epics}
    runs = simulate(order, deps, epics, inputs, live_sources, window, seed) if any(
        s not in (None, "done") for s in live_sources.values()) else {}

    start = inputs["start"]
    early = status == "early"
    out_epics = []
    for e in order:
        row = {"epic": e, "title": epics[e].title, "depends_on": sorted(deps[e]),
               "count_source": sources[e] or "none"}
        if sources[e] == "stories":
            row["counts_read"] = inputs["counts"][e]["read"]
        if e in reasons:
            row.update(likely_start=None, likely_finish=None, very_likely_finish=None,
                       critical_share=None, early=early, no_date=reasons[e])
        elif sources[e] == "done":
            row.update(likely_start=None, likely_finish=None, very_likely_finish=None,
                       critical_share=0.0, early=early, no_date=None)
        else:
            s, f, c = runs[e]
            row.update(likely_start=week_date(start, percentile(s, 50)),
                       likely_finish=week_date(start, percentile(f, 50)),
                       very_likely_finish=week_date(start, percentile(f, 85)),
                       critical_share=round(c / TRIALS, 4), early=early, no_date=None)
        out_epics.append(row)

    out_mils = []
    for mid in sorted(milestones, key=id_number):
        ms = milestones[mid]
        ids = members[mid]
        row = {"milestone": mid, "name": ms.name, "members": ids, "target": ms.target,
               "target_source": ms.source}
        unsliced = [f for f in ms.members if f not in by_feature]
        waiting = sorted(e for e in ids if e in reasons)
        live = [e for e in ids if e in runs]
        if unsliced:
            row.update(likely_finish=None, very_likely_finish=None, target_met_share=None,
                       no_date="member %s has no Epic yet" % ", ".join(unsliced))
        elif waiting:
            row.update(likely_finish=None, very_likely_finish=None, target_met_share=None,
                       no_date="member %s has no date" % ", ".join(waiting))
        elif not live:
            # Every member is done: nothing left to forecast.
            row.update(likely_finish=None, very_likely_finish=None, target_met_share=None, no_date=None)
        else:
            weeks = [max(runs[e][1][t] for e in live) for t in range(TRIALS)]
            row.update(likely_finish=week_date(start, percentile(weeks, 50)),
                       very_likely_finish=week_date(start, percentile(weeks, 85)))
            if ms.target:
                met = sum(1 for wk in weeks if week_date(start, wk) <= ms.target)
                row["target_met_share"] = round(met / TRIALS, 4)
            else:
                row["target_met_share"] = None
            row["no_date"] = None
        out_mils.append(row)

    result = {
        "seed": seed,
        "trials": TRIALS,
        "start": start.isoformat(),
        "in_flight": inputs["in_flight"],
        "history": {
            "from": inputs["from"],
            "weeks": len(window),
            "window": WINDOW,
            "status": status,
            "finished_epics": len(inputs["finished"]),
        },
        "epics": out_epics,
        "milestones": out_mils,
    }
    return result, gantt(result, {e for e in epics if epics[e].enabler}), []


def upstream_of(e, deps):
    """Every Epic `e` waits on, directly or not."""
    out, todo = set(), list(deps[e])
    while todo:
        p = todo.pop()
        if p not in out:
            out.add(p)
            todo += list(deps[p])
    return out


# ---------------------------------------------------------------- gantt

CHAPTER_OVER = 20      # dated Epics above which each Milestone is its own chart
GANTT_HEAD = """---
displayMode: compact
config:
  gantt:
    leftPadding: 230
    barHeight: 22
    fontSize: 12
    sectionFontSize: 12
---
gantt
    dateFormat YYYY-MM-DD
    axisFormat %d %b
    tickInterval 2week
    todayMarker off
"""
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
UNSAFE = {"#": "no. ", ":": " -", ";": ","}   # Mermaid ends a name at these
BAR = re.compile(r"^    (?!section )([^:]+?) :(.+)$")
TAGS = {"crit", "active", "milestone"}
GANTT_FILE = re.compile(r"gantt.*\.mmd")


def short(iso):
    d = datetime.date.fromisoformat(iso)
    return "%d %s" % (d.day, MONTHS[d.month - 1])


def mermaid_label(text, fallback):
    """`text` on one line, with the characters that end a Mermaid name
    replaced, or `fallback` when nothing is left."""
    text = re.sub("[%s]" % "".join(UNSAFE), lambda m: UNSAFE[m.group()], " ".join(text.split())).strip()
    return text or fallback


def task_id(record_id, part):
    return "%s_%s" % (record_id.replace("-", "_"), part) if part else record_id.replace("-", "_")


def is_critical(row):
    return (row["critical_share"] or 0) >= 0.5


def bars(result):
    """{task ID: (tags, label, start, end)}: every bar and diamond the
    Forecast calls for, from `forecast.json` alone. A diamond's end is `0d`."""
    out = {}
    for e in result["epics"]:
        if not e["likely_finish"]:
            continue
        crit = ("crit",) if is_critical(e) else ()
        out[task_id(e["epic"], "")] = (crit, "likely " + short(e["likely_finish"]),
                                       e["likely_start"], e["likely_finish"])
        if e["very_likely_finish"] != e["likely_finish"]:
            out[task_id(e["epic"], "tail")] = (("active",) + crit, "by " + short(e["very_likely_finish"]),
                                               e["likely_finish"], e["very_likely_finish"])
    for m in result["milestones"]:
        by, target = m["very_likely_finish"], m["target"]
        if not by:
            continue
        if target == by:
            out[task_id(m["milestone"], "target")] = (("crit", "milestone"), "target = by " + short(by), by, "0d")
            continue
        if target:
            out[task_id(m["milestone"], "target")] = (("crit", "milestone"), "target " + short(target), target, "0d")
        out[task_id(m["milestone"], "by")] = (("milestone",), "by " + short(by), by, "0d")
    return out


def bar_line(tid, bar):
    tags, label, start, end = bar
    return "    %s :%s, %s, %s" % (label, ", ".join(tags + (tid,)), start, end)


def gantt(result, enablers):
    """{file name: Mermaid text}, or {} when no Epic is dated."""
    want = bars(result)
    dated = [e for e in result["epics"] if e["likely_finish"]]
    if not dated:
        return {}
    placed, groups = set(), []
    for m in result["milestones"]:
        rows = [e for e in dated if e["epic"] in m["members"] and e["epic"] not in placed]
        placed |= {e["epic"] for e in rows}
        groups.append((m["milestone"], m, rows))
    groups.append(("other", None, [e for e in dated if e["epic"] not in placed]))

    chapters = []
    for key, m, rows in groups:
        lines = []
        for e in sorted(rows, key=lambda e: e["epic"] not in enablers):
            lines.append("    section %s%s" % (mermaid_label(e["title"], e["epic"]),
                                              " (groundwork)" if e["epic"] in enablers else ""))
            lines += [bar_line(t, want[t]) for t in (task_id(e["epic"], ""), task_id(e["epic"], "tail")) if t in want]
        if m is not None and m["very_likely_finish"]:
            lines.append("    section ◆ %s" % mermaid_label(m["name"], m["milestone"]))
            lines += [bar_line(t, want[t]) for t in (task_id(m["milestone"], "target"), task_id(m["milestone"], "by"))
                      if t in want]
        if lines:
            chapters.append((key, lines))
    if len(dated) <= CHAPTER_OVER:
        return {"gantt.mmd": GANTT_HEAD + "".join(l + "\n" for _, lines in chapters for l in lines)}
    return {"gantt-%s.mmd" % key: GANTT_HEAD + "".join(l + "\n" for l in lines) for key, lines in chapters}


def check_gantt(result, charts):
    """Problems, one per line, where the Mermaid in `charts` ({file name:
    text}) is not the chart `forecast.json` calls for: each bar and diamond
    read back from the text, its tags, label and dates matched, and every
    section holding at least one."""
    want, seen, problems = bars(result), {}, []
    if want and not charts:
        problems.append("gantt: no gantt*.mmd for a Forecast with dates")
    for fname in sorted(charts):
        lines = charts[fname].split("\n")
        if "displayMode: compact" not in lines[:3]:
            problems.append("%s: not `displayMode: compact`" % fname)
        if "gantt" not in lines:
            problems.append("%s: no `gantt` line" % fname)
            continue
        section = None   # (where, bars under it) of the open section
        for n, line in enumerate(lines[lines.index("gantt") + 1:], start=lines.index("gantt") + 2):
            if not line or line in GANTT_HEAD.split("\n"):
                continue
            where = "%s:%d" % (fname, n)
            if line.startswith("    section "):
                if section and not section[1]:
                    problems.append("%s: a section with no bar" % section[0])
                section = (where, [])
                if any(c in line for c in UNSAFE):
                    problems.append("%s: a section name holds `#`, `:` or `;`" % where)
                continue
            m = BAR.match(line)
            if section:
                section[1].append(where)
            if m is None:
                problems.append("%s: `%s` is not a section or bar" % (where, line.strip()))
                continue
            items = [i.strip() for i in m.group(2).split(",")]
            tags = tuple(i for i in items if i in TAGS)
            rest = [i for i in items if i not in TAGS]
            if len(rest) != 3 or "after" in " ".join(rest).split() or "vert" in items:
                problems.append("%s: `%s` is not `<tags>, <id>, <start>, <end>` with explicit dates" % (where, line.strip()))
                continue
            tid, start, end = rest
            got = (tuple(sorted(tags)), m.group(1), start, end)
            if tid in seen:
                problems.append("%s: `%s` is also %s" % (where, tid, seen[tid]))
                continue
            seen[tid] = where
            if tid not in want:
                problems.append("%s: `%s` is not in forecast.json" % (where, tid))
                continue
            exp = want[tid]
            exp = (tuple(sorted(exp[0])),) + exp[1:]
            if got != exp:
                problems.append("%s: `%s` is %s, %s to %s, tagged %s; forecast.json calls for %s, %s to %s, tagged %s"
                                % (where, tid, got[1], got[2], got[3], ", ".join(got[0]) or "nothing",
                                   exp[1], exp[2], exp[3], ", ".join(exp[0]) or "nothing"))
        if section and not section[1]:
            problems.append("%s: a section with no bar" % section[0])
    problems += ["gantt: `%s` from forecast.json has no bar" % t for t in sorted(set(want) - set(seen))]
    return problems


def check(plan_dir):
    """`--check`: (problems) for a plan folder's files as they stand."""
    if not os.path.isdir(plan_dir):
        raise Unreadable("%s: no such plan folder" % plan_dir)
    path = os.path.join(plan_dir, "forecast.json")
    try:
        result = json.loads(read_text(path))
    except ValueError as e:
        raise Unreadable("%s: not valid JSON: %s" % (path, e))
    charts = {n: read_text(os.path.join(plan_dir, n)) for n in sorted(os.listdir(plan_dir)) if GANTT_FILE.fullmatch(n)}
    try:
        return check_gantt(result, charts)
    except (KeyError, TypeError, ValueError) as e:
        raise Unreadable("%s: not a Forecast: %s" % (path, e))


def main(argv):
    if len(argv) != 3:
        print("usage: forecast.py <project dir> <plan dir>\n       forecast.py --check <plan dir>", file=sys.stderr)
        return 2
    try:
        if argv[1] == "--check":
            problems = check(argv[2])
        else:
            plan_dir = argv[2]
            result, charts, problems = forecast(argv[1], plan_dir)
            if not problems:
                problems = check_gantt(result, charts)
    except Unreadable as e:
        print("Can't read: %s" % e, file=sys.stderr)
        return 2
    for p in problems:
        print(p, file=sys.stderr)
    if problems:
        return 1
    if argv[1] == "--check":
        return 0
    return write(plan_dir, {"forecast.json": json.dumps(result, indent=2, ensure_ascii=False) + "\n", **charts})


def write(plan_dir, files):
    """Write `files` ({file name: text}) into the plan folder, replacing any
    earlier Gantt: 0, or 2 with stderr naming what could not be written."""
    path = plan_dir
    try:
        for old in os.listdir(plan_dir):
            if GANTT_FILE.fullmatch(old):
                path = os.path.join(plan_dir, old)
                os.remove(path)
        for fname, text in files.items():
            path = os.path.join(plan_dir, fname)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
    except OSError as e:
        print("Can't write: %s: %s" % (path, e.strerror or e), file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
