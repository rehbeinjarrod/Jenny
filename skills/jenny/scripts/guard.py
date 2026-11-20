#!/usr/bin/env python3
"""Guard: reject a Workspace commit that holds a malformed record, or a Veneer
slip in `outbox/` text.

Runs as the Workspace's git pre-commit hook, so it holds on every runtime.
`setup` writes the hook with:

    python3 <skills>/jenny/scripts/guard.py --install

From then on every `git commit` runs `guard.py` with no arguments. It reads
what is staged, never the working copy:

- Records (`projects/<slug>/…`, `log/…`): the title line, required header
  lines and their values, three-digit IDs that start with the Project code,
  no ID defined twice, log headings, and canonical terms in the record's
  structure (header keys, section headings, table headers) and in its
  `Score reason:` value, the one value checked, since only Jenny writes it.
- A Milestone record's `Target:` and `Internal:` forms (a derived target
  names a Plan version in the Project) and its members (real Feature IDs),
  and a story map's shape: Milestone lines under each step,
  enablers, `## Not on the map`.
- An Epic's `Technical Enabler:` and `Enables:` lines (active Requirements,
  a `Pain point:` line when there is no `Enables:`), and its Enabler Story
  lines under `## Enabler Stories`.
- A Plan version folder (`projects/<slug>/plans/plan-v<N>/`): frozen once
  committed, so no file in it may be changed, added, removed or renamed,
  except that `Shown: <YYYY-MM-DD> to <who>` lines may be appended to its
  plan record, `plan.md`. Its files are rendered in shown names, so record
  structure is not checked.
- `veneer.md`: still readable by the Veneer scan.
- `outbox/`: the Veneer scan over each text file, outside code (for HTML,
  outside tags, `<code>` and `<pre>`).

A clean commit passes with no output (exit 0). Otherwise stderr names each
file and problem, and the commit is rejected (exit 1).

`--install` writes the hook: exit 0 silently, or 1 with one line on stderr
saying why it was not written (no git repository, `core.hooksPath` set, or a
pre-commit hook that isn't Jenny's, which is kept).

Python 3.9 or later, standard library only.
"""

import datetime
import glob
import os
import re
import stat
import subprocess
import sys

# No `__pycache__/` in the skills folder: it would leave the Workspace's tree
# dirty after every commit.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import veneer_scan  # noqa: E402

MARKER = "jenny:guard"
HOOK = """#!/bin/sh
# jenny:guard. Written by Jenny's setup, which replaces it on upgrade.
# Runs the Guard (jenny/scripts/guard.py) from this Workspace's Jenny skills.
cd "$(git rev-parse --show-toplevel)" || exit 1
for g in .claude/skills/jenny/scripts/guard.py .cursor/skills/jenny/scripts/guard.py; do
  if [ -f "$g" ]; then exec python3 "$g"; fi
done
exit 0
"""

HEADING = "Jenny Guard: commit rejected. Fix each problem below, then commit again."
FOOTER = "Nothing was committed. Never bypass the Guard with --no-verify."

# Delivery terms (setup's Veneer section): a word equal to one of these is
# canonical in a record, even when the Veneer also uses it as a shown name.
CANONICAL = ["Project", "Requirement", "Feature", "Epic", "Slice", "Epic pack",
             "Decision coverage", "Sign-off view", "Sign-off", "Handoff", "Story",
             "Question", "Answer", "Decision", "Source", "Capture", "Milestone", "Spike"]

KINDS = "SRC|REQ|FEA|EPC|Q|ANS|SO|MIL|ENS"
ID = r"[A-Z]{2,4}-(?:%s)-\d+" % KINDS
ID_TOKEN = re.compile(r"(?<![A-Za-z0-9])(([A-Z]{2,4})-(?:%s)-(\d+))(?!\d)" % KINDS)
FILE_ID = re.compile(r"^(%s)(?:-|\.md$)" % ID)
TITLE = re.compile(r"^# ([A-Z]{2,4}(?:-(?:%s)-\d+)?)(?![A-Za-z0-9-])" % KINDS)
HEADER = re.compile(r"^([A-Z][A-Za-z' -]*):(?: (.*)|)$")
LOG_HEADING = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] [^|]+ \| \S.*$")
DEFINITION = re.compile(r"^\s*- \*\*(%s)\*\*" % ID)
SIGNOFF = re.compile(r"^## ([A-Z]{2,4}-SO-\d+) ·")
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")

# Folder of ID-named records → the header lines each must hold.
ID_FOLDERS = {
    "sources": ["Kind", "Owner", "Date", "Kept"],
    "questions": ["Code", "Status", "Impact", "Uncertainty", "Score", "Raised from"],
    "features": ["Code", "Feature"],
    "milestones": ["Code", "Milestone", "Outcome", "Success metric", "Target", "Internal"],
}
# Rendered for readers outside the Workspace, in shown names.
RENDERED = re.compile(r"^(pack-v\d+|signoff-view-v\d+-.*)\.md$")
# A Plan version folder: frozen once committed, its views rendered.
PLAN_FOLDER = re.compile(r"^(projects/[^/]+/plans/plan-v\d+)/")
FROZEN_PLAN = "a Plan folder is frozen once committed: make a new Plan version instead"
PLAN_RECORD = "plan.md"
SHOWN = re.compile(r"^Shown: (\d{4}-\d{2}-\d{2}) to \S.*$")
SHOWN_FORM = "`Shown: <YYYY-MM-DD> to <who>`"


def rendered(parts):
    """Whether a Project file, as its path parts below the Project folder,
    is rendered in shown names: a pack, a Sign-off view or a Plan's file."""
    return bool(RENDERED.match(parts[-1])) or \
        len(parts) == 3 and parts[0] == "plans" and bool(re.fullmatch(r"plan-v\d+", parts[1]))


# ---------------------------------------------------------------- git

def git(*args):
    p = subprocess.run(["git", *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr.decode(errors="replace").strip()))
    return p.stdout


def staged_status():
    """{path: A | M | D} for each path the index differs on from HEAD."""
    out = git("diff", "--cached", "--name-status", "-z", "--no-renames").decode("utf-8").split("\0")
    return {out[i + 1]: out[i] for i in range(0, len(out) - 1, 2) if out[i]}


def staged(filter="ACM"):
    """Paths the index differs on from HEAD, of the kinds in `filter`: by
    default added or changed (a rename is its old path removed and its new
    one added), or "" for every kind."""
    out = git("diff", "--cached", "--name-only", "-z", "--no-renames", *(["--diff-filter=" + filter] if filter else []))
    return [p for p in out.decode("utf-8").split("\0") if p]


def at_head(prefix):
    """The paths under `prefix` at HEAD, or none before the first commit.
    Not through git(): with no HEAD yet, git exits non-zero, which is not a
    failure here."""
    p = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", prefix],
                       capture_output=True)
    return [x for x in p.stdout.decode("utf-8").split("\0") if x] if p.returncode == 0 else []


def indexed(prefix):
    out = git("ls-files", "-z", "--", prefix)
    return [p for p in out.decode("utf-8").split("\0") if p]


def show(path, rev=""):
    """The staged text of `path` (or its text at `rev`), or None when it is
    not UTF-8 text."""
    try:
        return git("show", rev + ":" + path).decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


# ---------------------------------------------------------------- Veneer

class Veneer:
    """The staged `veneer.md`: what to flag in `outbox/` and in records."""

    def __init__(self, text):
        rows = veneer_scan.veneer_rows(text)
        self.terms = veneer_scan.renamed(rows)
        self.shown = {term.lower(): shown for term, shown, _ in rows if term and shown}
        canonical = {c.lower() for c in CANONICAL} | {t.lower() for t, _, _ in rows if t}
        names = []  # (word, canonical term, "shown name" | "alias")
        for term, shown, aliases in rows:
            if not term:
                continue
            for word, what in [(shown, "shown name")] + [(a, "alias") for a in aliases]:
                if word and not any(re.fullmatch(veneer_scan.term_pattern(c), word, re.I)
                                    for c in canonical):
                    names.append((word, term, what))
        self.names = [(re.compile(veneer_scan.term_pattern(w), re.I), term, what) for w, term, what in names]
        # For names_in: one group per name, longest first, so "tech spec" is
        # one hit, not "spec"; group i is the name at hit_names[i].
        longest = sorted(names, key=lambda n: len(n[0]), reverse=True)
        self.finder = re.compile(r"(?<!\w)(?:%s)(?!\w)" % "|".join(
            "(%s)" % veneer_scan.term_pattern(w) for w, _, _ in longest), re.I) if names else None
        self.hit_names = [(term, what) for _, term, what in longest]

    def shown_for(self, word):
        word = re.sub(r"\s+", " ", word)
        for term in self.terms:
            if re.fullmatch(veneer_scan.term_pattern(term), word, re.I):
                return self.shown[term.lower()]
        return "?"

    def name_of(self, text):
        """(canonical term, "shown name" | "alias") when the whole of `text`
        is a shown name or alias, singular or plural; otherwise None."""
        text = re.sub(r"\s+", " ", text.strip().strip("*_").strip())
        for pattern, term, what in self.names:
            if pattern.fullmatch(text):
                return term, what
        return None

    def names_in(self, text):
        """(word as written, canonical term, "shown name" | "alias") for each
        shown name or alias in `text`, as a whole word, singular or plural,
        outside code spans."""
        if self.finder is None:
            return []
        out = []
        for m in self.finder.finditer(veneer_scan.blank_code_spans(text)):
            i = next(i for i, g in enumerate(m.groups()) if g is not None)
            out.append((re.sub(r"\s+", " ", m.group()),) + self.hit_names[i])
        return out


def load_veneer():
    """(Veneer or None, problem or None) from the staged `veneer.md`."""
    if "veneer.md" not in indexed("veneer.md"):
        return None, None
    text = show("veneer.md")
    if text is None:
        return None, "veneer.md: can't be read: it is not UTF-8 text"
    try:
        return Veneer(text), None
    except veneer_scan.Unreadable as e:
        return None, "veneer.md: can't be read: %s" % e


# ---------------------------------------------------------------- outbox

HTML_CODE = re.compile(r"<(pre|code|script|style)\b[^>]*>.*?</\1\s*>", re.I | re.S)
HTML_TAG = re.compile(r"<[^>]*>", re.S)


def blank(m):
    return re.sub(r"[^\n]", " ", m.group())


def html_prose(text):
    """The text with code blocks and tags blanked, line numbers kept."""
    return HTML_TAG.sub(blank, HTML_CODE.sub(blank, text))


def check_outbox(path, veneer):
    text = show(path)
    if text is None or veneer is None:
        return []
    if path.lower().endswith((".html", ".htm")):
        text = html_prose(text)
    return ["%s:%d: `%s`: the Veneer shows this as %s"
            % (path, n, re.sub(r"\s+", " ", word), veneer.shown_for(word))
            for n, word in veneer_scan.scan(text, veneer.terms)]


# ---------------------------------------------------------------- records

def header_block(lines):
    """{key: (line number, value)} for the `Key: value` lines after the title."""
    block, i = {}, 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines):
        m = HEADER.match(lines[i])
        if not m:
            break
        block.setdefault(m.group(1), (i + 1, (m.group(2) or "").strip()))
        i += 1
    return block


class Project:
    """One Project as staged: its code and every ID it defines."""

    def __init__(self, slug):
        self.slug = slug
        self.root = "projects/%s/" % slug
        self.files = indexed(self.root)
        self.code = None
        self._project_md = []
        if self.root + "project.md" in self.files:
            self._project_md = (show(self.root + "project.md") or "").splitlines()
            code = header_block(self._project_md).get("Code")
            self.code = code[1] if code else None
        self._defs = None

    def people(self):
        """{name: role} from the People table of `project.md`."""
        people, table = {}, False
        for line in self._project_md:
            if line.startswith("## "):
                table = line.strip() == "## People"
            elif table and not TABLE_RULE.match(line):
                row = veneer_scan.cells(line)
                if row and len(row) >= 2 and row[0] and row[0] != "Name":
                    people[row[0]] = row[1]
        return people

    def active(self, kind):
        """IDs of `kind` that are in force: those a record file defines
        (MIL), or a `- **<ID>**` line (REQ). A withdrawn line is struck
        through, `- ~~**<ID>**`, so it defines nothing."""
        return {i for i in self.definitions() if "-%s-" % kind in i}

    def definitions(self):
        """{ID: [(path, line or None)]}: ID-named files and folders, and the
        Requirement, Answer, Sign-off and Enabler Story lines that define an
        ID."""
        if self._defs is not None:
            return self._defs
        defs = {}
        units = set()
        for path in self.files:
            rest = path[len(self.root):]
            parts = rest.split("/")
            if len(parts) == 2 and parts[0] in ID_FOLDERS or len(parts) >= 3 and parts[0] == "epics":
                m = FILE_ID.match(parts[1])
                if m:
                    unit = self.root + "/".join(parts[:2])
                    if unit not in units:
                        units.add(unit)
                        defs.setdefault(m.group(1), []).append((unit, None))
            if not path.endswith(".md") or rendered(parts) or parts[0] == "log":
                continue
            text = show(path) or ""
            for n, line in enumerate(text.splitlines(), start=1):
                m = DEFINITION.match(line) or SIGNOFF.match(line)
                if m and re.search(r"-(REQ|ANS|SO|ENS)-", m.group(1)):
                    defs.setdefault(m.group(1), []).append((path, n))
        self._defs = defs
        return defs


def check_ids(path, lines, old=()):
    """Three-digit IDs, outside `> ` quotes (Source text kept as given) and
    outside the lines in `old`."""
    out = []
    for n, line in enumerate(lines, start=1):
        if line.lstrip().startswith(">") or line in old:
            continue
        for m in ID_TOKEN.finditer(line):
            if len(m.group(3)) != 3:
                out.append("%s:%d: `%s`: an ID ends in three digits" % (path, n, m.group(1)))
    return out


def check_title(path, lines, code, want_id=None):
    m = TITLE.match(lines[0]) if lines else None
    if m is None:
        return ["%s:1: the first line is not `# <ID or Project code> · <title>`" % path]
    got = m.group(1)
    if want_id is not None:
        if got != want_id:
            return ["%s:1: the title's ID `%s` is not the file name's `%s`" % (path, got, want_id)]
    elif code and got.split("-")[0] != code:
        return ["%s:1: the title starts `%s`, not the Project code `%s`" % (path, got, code)]
    return []


def check_headers(path, block, required):
    return ["%s: no `%s:` header line" % (path, key) for key in required if key not in block]


def check_value(path, block, key, want, what):
    if key in block and block[key][1] != want:
        n, value = block[key]
        return ["%s:%d: `%s: %s` is not %s `%s`" % (path, n, key, value, what, want)]
    return []


NOT_CANONICAL = "%s:%d: `%s`: records use the canonical term %s, not its %s"


def check_canonical(path, lines, veneer):
    """Shown names or aliases in a record's structure (header keys, section
    headings and table header rows) and in its `Score reason:` value."""
    if veneer is None:
        return []
    out, block = [], header_block(lines)
    places = [(n, key) for key, (n, _) in block.items() if key not in template_keys()]
    for n, line in enumerate(lines, start=1):
        if n > 1 and re.match(r"^#{1,6} ", line):
            heading = line.lstrip("#").strip()
            if not ID_TOKEN.match(heading):
                places.append((n, heading))
        elif line.lstrip().startswith("|") and n < len(lines) and TABLE_RULE.match(lines[n]):
            places += [(n, c) for c in veneer_scan.cells(line) or []]
    for n, text in sorted(places):
        found = veneer.name_of(text)
        if found:
            out.append(NOT_CANONICAL % (path, n, text.strip(), found[0], found[1]))
    if "Score reason" in block:
        # The one value checked: only Jenny writes it, so it never holds the
        # Operator's or a Stakeholder's own words (ADR-0013).
        n, value = block["Score reason"]
        out += [NOT_CANONICAL % (path, n, word, term, what)
                for word, term, what in veneer.names_in(value or "")]
    return out


_TEMPLATE_KEYS = None


SPAN_KEY = re.compile(r"`([A-Z][A-Za-z' -]*):[^`]*`")


def template_keys():
    """Header keys the Tool writes, which are never a slip: each header line
    of a template, and each `Key:` a skill names in a code span."""
    global _TEMPLATE_KEYS
    if _TEMPLATE_KEYS is None:
        skills = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
        keys = set()
        for t in glob.glob(os.path.join(skills, "*", "templates", "*.md")):
            with open(t, encoding="utf-8") as f:
                keys |= {m.group(1) for m in map(HEADER.match, f.read().splitlines()) if m}
        for t in glob.glob(os.path.join(skills, "*", "SKILL.md")):
            with open(t, encoding="utf-8") as f:
                keys |= set(SPAN_KEY.findall(f.read()))
        _TEMPLATE_KEYS = keys
    return _TEMPLATE_KEYS


def committed(path):
    """The lines of `path` at HEAD, or None when it is new."""
    try:
        return git("show", "HEAD:" + path).decode("utf-8-sig", errors="replace").splitlines()
    except RuntimeError:
        return None


def check_log(path, lines, title):
    """A log as this commit leaves it. Only what the commit adds is checked,
    so an older slip never blocks a later operation: the title of a new
    month's file, and each new heading."""
    out, before = [], committed(path)
    if before is None and (not lines or lines[0].rstrip() != title):
        out.append("%s:1: the first line is not `%s`" % (path, title))
    old = set(before or [])
    out += check_ids(path, lines, old)
    for n, line in enumerate(lines, start=1):
        if line.startswith("## ") and line not in old and not LOG_HEADING.match(line.rstrip()):
            out.append("%s:%d: `%s` is not a log heading, `## [YYYY-MM-DD] <op> | <title>`" % (path, n, line.rstrip()))
    return out


def check_duplicates(path, project, file_id=None):
    defs = project.definitions()
    out = []
    if file_id is not None:
        units = [u for u, _ in defs.get(file_id, [])]
        unit = next((u for u in units if path == u or path.startswith(u + "/")), None)
        if unit is not None:
            for other in units:
                if other != unit:
                    out.append("%s: `%s` is also %s" % (path, file_id, other))
    for pid, places in sorted(defs.items()):
        mine = [(p, n) for p, n in places if p == path and n is not None]
        for p, n in mine:
            for other, on in places:
                if (other, on) != (p, n):
                    out.append("%s:%d: `%s` is also defined in %s:%d" % (path, n, pid, other, on))
    return out


TARGET = re.compile(r"^(?:(\d{4}-\d{2}-\d{2}) set by (.+)|derived from plan-v\d+|none)$")
TARGET_FORM = "`<YYYY-MM-DD> set by <name>`, `derived from plan-v<N>` or `none`"


def real_date(text):
    try:
        datetime.date.fromisoformat(text)
        return True
    except ValueError:
        return False


def check_milestone(path, lines, block, project):
    """A Milestone record's values: an outcome and metric, a `Target:` in one
    of its three forms set by someone in People, `Internal: yes | no`, and a
    `## Members` section."""
    out = []
    for key in ("Outcome", "Success metric"):
        if key in block and not block[key][1]:
            out.append("%s:%d: `%s:` has no value" % (path, block[key][0], key))
    if "Target" in block:
        n, value = block["Target"]
        m = TARGET.match(value)
        derived = re.fullmatch(r"derived from (plan-v\d+)", value)
        if value.startswith("derived") and derived is None:
            out.append("%s:%d: `Target: %s`: a derived target names the Plan version it came from, "
                       "`derived from plan-v<N>`" % (path, n, value))
        elif derived and not indexed("%splans/%s/" % (project.root, derived.group(1))):
            out.append("%s:%d: `Target: %s`: there is no Plan version plans/%s/"
                       % (path, n, value, derived.group(1)))
        elif m is None or m.group(1) and not real_date(m.group(1)):
            out.append("%s:%d: `Target: %s` is not %s" % (path, n, value, TARGET_FORM))
        elif m.group(2) and project.people().get(m.group(2).strip()) != "Stakeholder":
            out.append("%s:%d: `Target: %s`: %s is not a Stakeholder in the Project's People"
                       % (path, n, value, m.group(2).strip()))
    if "Internal" in block and block["Internal"][1] not in ("yes", "no"):
        n, value = block["Internal"]
        out.append("%s:%d: `Internal: %s` is not `yes` or `no`" % (path, n, value))
    if "## Members" not in (l.rstrip() for l in lines):
        out.append("%s: no `## Members` section" % path)
    return out + check_members(path, lines, project)


MEMBER_FORM = "`- <CODE>-FEA-<nnn> · <Feature title>` or `- <CODE>-FEA-<nnn>`"
NOT_SLICED = "Not sliced yet."


def check_members(path, lines, project):
    """`## Members` reads `Not sliced yet.` or lists the Milestone's Features,
    `- <FEA ID>` with an optional ` · <title>`, each a Feature in features/
    and listed once."""
    code = code_pattern(project)
    member = re.compile(r"^- (%s-FEA-\d{3})(?: · .+)?$" % code)
    features = project.active("FEA")
    out, seen, not_sliced, section = [], {}, None, False
    for n, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if line.startswith("## "):
            section = line == "## Members"
        elif not section:
            continue
        elif line == NOT_SLICED:
            not_sliced = n
        elif line.startswith("- "):
            m = member.match(line)
            if m is None:
                out.append("%s:%d: `%s` is not %s" % (path, n, line, MEMBER_FORM))
            elif m.group(1) in seen:
                out.append("%s:%d: `%s` is a member twice (also line %d)" % (path, n, m.group(1), seen[m.group(1)]))
            else:
                seen[m.group(1)] = n
                if m.group(1) not in features:
                    out.append("%s:%d: `%s` is not a Feature in features/" % (path, n, m.group(1)))
    if not_sliced and seen:
        out.append("%s:%d: `%s` beside Features listed as members" % (path, not_sliced, NOT_SLICED))
    return out


def code_pattern(project):
    """A regex for the Project code, or any code when it has none."""
    return re.escape(project.code) if project.code else "[A-Z]{2,4}"


MAP_SECTIONS = ("Enablers", "Not on the map")
CARD_FORM = "`- <CODE>-MIL-<nnn>: <CODE>-REQ-<nnn> (<user group>), …`"
# Any ID shape, ENS and kinds to come included: an enabler on the map has none.
ANY_ID = re.compile(r"[A-Z]{2,4}-[A-Z]{2,4}-\d+")
ENABLER = re.compile(r"^- \*\*(.+?)\*\* · Kind: (?:Technical Enabler|Enabler Story) · Enables: (.+?) · Depends on: (.+)$")
ENABLER_FORM = ("`- **<enabler name>** · Kind: <Technical Enabler | Enabler Story> · Enables: <Requirement IDs | none> "
                "· Depends on: <enabler names or Epic IDs | none>`")


def check_storymap(path, lines, project):
    """`storymap.md`: `## <Activity>` / `### <Step>` headings, each card line
    `- <MIL ID>: <REQ ID> (<user>), …` naming a Milestone record and active
    Requirements, each Requirement once; `## Enablers` with named enablers;
    `## Not on the map` with Requirement IDs."""
    code = code_pattern(project)
    card = re.compile(r"^- (%s-MIL-\d{3}): (.+)$" % code)
    placed = re.compile(r"^(%s-REQ-\d{3}) \(([^()]+)\)$" % code)
    off_map = re.compile(r"^- (%s-REQ-\d{3})(?: · .*)?$" % code)
    req_id = re.compile(r"^%s-REQ-\d{3}$" % code)
    epic_id = re.compile(r"^%s-EPC-\d{3}$" % code)
    reqs, mils = project.active("REQ"), project.active("MIL")
    out, seen, enablers = [], {}, []
    section, step = None, False

    def requirement(n, rid):
        if rid not in reqs:
            out.append("%s:%d: `%s` is not an active Requirement" % (path, n, rid))

    def on_map(n, rid):
        requirement(n, rid)
        if rid in seen:
            out.append("%s:%d: `%s` is on the map twice (also line %d)" % (path, n, rid, seen[rid]))
        else:
            seen[rid] = n

    for n, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if line.startswith("## "):
            title = line[3:].strip()
            section, step = (title if title in MAP_SECTIONS else "activity"), False
        elif line.startswith("### "):
            if section != "activity":
                out.append("%s:%d: `%s` is not under an activity heading" % (path, n, line))
            step = section == "activity"
        elif not line.startswith("- ") or section is None:
            continue
        elif section == "activity":
            m = card.match(line)
            items = [placed.match(i.strip()) for i in m.group(2).split(",")] if m else []
            if not step:
                out.append("%s:%d: `%s` is not under a `### <Step>` heading" % (path, n, line))
            elif m is None or not all(items):
                out.append("%s:%d: `%s` is not %s" % (path, n, line, CARD_FORM))
            else:
                if m.group(1) not in mils:
                    out.append("%s:%d: `%s` has no Milestone record in milestones/" % (path, n, m.group(1)))
                for i in items:
                    on_map(n, i.group(1))
        elif section == "Enablers":
            m = ENABLER.match(line)
            if m is None:
                out.append("%s:%d: `%s` is not %s" % (path, n, line, ENABLER_FORM))
            elif ANY_ID.fullmatch(m.group(1).strip()):
                out.append("%s:%d: `%s`: an enabler on the map has a name, not an ID" % (path, n, m.group(1)))
            else:
                enablers.append((n, m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
        else:
            m = off_map.match(line)
            if m is None:
                out.append("%s:%d: `%s` is not `- <CODE>-REQ-<nnn>`" % (path, n, line))
            else:
                on_map(n, m.group(1))

    names = {name for _, name, _, _ in enablers}
    for n, name, enables, depends in enablers:
        if enables != "none":
            for rid in (e.strip() for e in enables.split(",")):
                if req_id.match(rid):
                    requirement(n, rid)
                else:
                    out.append("%s:%d: `Enables: %s`: `%s` is not a Requirement ID" % (path, n, enables, rid))
        if depends != "none":
            for d in (e.strip() for e in depends.split(",")):
                if d not in names and not epic_id.match(d):
                    out.append("%s:%d: `Depends on: %s`: `%s` is not an enabler on the map or an Epic"
                               % (path, n, depends, d))
    present = {l.rstrip() for l in lines}
    out += ["%s: no `## %s` section" % (path, s) for s in MAP_SECTIONS if "## " + s not in present]
    return out


ENS_FORM = ("`- **<CODE>-ENS-<nnn>** <name> · Enables: <Requirement IDs | none> "
            "· Depends on: <Enabler Story or Epic IDs | none>`")


def check_enables(path, n, value, project):
    """`Enables: <value>`: each comma-separated item an active Requirement."""
    req_id = re.compile(r"^%s-REQ-\d{3}$" % code_pattern(project))
    reqs, out = project.active("REQ"), []
    for rid in (e.strip() for e in value.split(",")):
        if not req_id.match(rid):
            out.append("%s:%d: `Enables: %s`: `%s` is not a Requirement ID" % (path, n, value, rid))
        elif rid not in reqs:
            out.append("%s:%d: `Enables: %s`: `%s` is not an active Requirement" % (path, n, value, rid))
    return out


def check_epic(path, lines, block, project):
    """An `epic.md`'s enabler lines. A Technical Enabler has `Technical
    Enabler: yes`, covers nothing, and names the active Requirements it
    enables in `Enables:`, or keeps a `Pain point:` line for having none.
    Each line under `## Enabler Stories` is an Enabler Story, `- **<ENS ID>**
    <name> · Enables: <IDs | none> · Depends on: <ENS or EPC IDs | none>`."""
    code = code_pattern(project)
    story = re.compile(r"^- \*\*(%s-ENS-\d{3})\*\* (\S.*?) · Enables: (.+?) · Depends on: (.+)$" % code)
    out = []
    te = block.get("Technical Enabler")
    is_te = bool(te) and te[1] == "yes"
    if te and not is_te:
        out.append("%s:%d: `Technical Enabler: %s` is not `yes`; every other Epic leaves the line out" % (path, te[0], te[1]))
    if "Enables" in block:
        n, value = block["Enables"]
        if not te:
            out.append("%s:%d: `Enables:` is only for a Technical Enabler, after `Technical Enabler: yes`" % (path, n))
        out += check_enables(path, n, value, project)
    elif is_te and "Pain point" not in block:
        out.append("%s: a Technical Enabler with no `Enables:` line is a pain point: "
                   "it needs a `Pain point:` line with the Operator's reason" % path)
    section, covers, stories = None, [], []
    for n, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if line.startswith("## "):
            section = line[3:].strip()
        elif section == "Covers" and line:
            covers.append(line)
        elif section == "Enabler Stories" and line.startswith("- "):
            m = story.match(line)
            if m is None:
                # An ID without three digits is named by check_ids alone.
                if not re.match(r"^- \*\*%s-ENS-(?!\d{3}\*)\d+\*\*" % code, line):
                    out.append("%s:%d: `%s` is not %s" % (path, n, line, ENS_FORM))
            else:
                stories.append((n, m.group(3).strip(), m.group(4).strip()))
    if is_te and covers != ["None."]:
        out.append("%s: a Technical Enabler covers no Requirement: `## Covers` reads `None.`" % path)
    known = project.active("ENS") | project.active("EPC")
    for n, enables, depends in stories:
        if enables != "none":
            out += check_enables(path, n, enables, project)
        if depends != "none":
            for d in (e.strip() for e in depends.split(",")):
                if d not in known:
                    out.append("%s:%d: `Depends on: %s`: `%s` is not an Enabler Story or Epic in the Project"
                               % (path, n, depends, d))
    return out


def check_record(path, project, veneer):
    """Problems with one staged file under `projects/<slug>/`."""
    if not path.endswith(".md"):
        return []
    text = show(path)
    if text is None:
        return ["%s: not UTF-8 text" % path]
    lines = text.splitlines()
    rest = path[len(project.root):]
    parts = rest.split("/")
    code = project.code

    if len(parts) == 2 and parts[0] == "log" and re.fullmatch(r"\d{4}-\d{2}\.md", parts[1]):
        return check_log(path, lines, "# %s log · %s" % (code or "<CODE>", parts[1][:-3]))

    out = check_ids(path, lines)
    if rendered(parts):
        return out

    block = header_block(lines)
    file_id = None
    required = []
    if rest == "project.md":
        out += check_title(path, lines, code)
        required = ["Code", "Slug", "Name"]
        out += check_value(path, block, "Slug", project.slug, "the folder name")
        if code is not None and not re.fullmatch(r"[A-Z]{2,4}", code):
            out.append("%s:%d: `Code: %s` is not 2 to 4 capital letters" % (path, block["Code"][0], code))
    elif len(parts) == 2 and parts[0] in ID_FOLDERS and FILE_ID.match(parts[1]):
        required = ID_FOLDERS[parts[0]]
        file_id = FILE_ID.match(parts[1]).group(1)
        out += check_title(path, lines, code, file_id)
        if parts[0] == "features":
            out += check_value(path, block, "Feature", file_id, "the file's ID")
        if parts[0] == "milestones":
            out += check_value(path, block, "Milestone", file_id, "the file's ID")
            out += check_milestone(path, lines, block, project)
    elif len(parts) == 3 and parts[0] == "epics" and FILE_ID.match(parts[1]) and parts[2] in ("epic.md", "signoffs.md"):
        file_id = FILE_ID.match(parts[1]).group(1)
        if parts[2] == "epic.md":
            out += check_title(path, lines, code, file_id)
            required = ["Code", "Epic", "Feature"]
            out += check_epic(path, lines, block, project)
        else:
            out += check_title(path, lines, code)
            required = ["Code", "Epic"]
        out += check_value(path, block, "Epic", file_id, "the file's ID")
    elif rest == "storymap.md":
        out += check_title(path, lines, code)
        required = ["Code", "Sources"]
        out += check_storymap(path, lines, project)
    else:
        if parts[-1] == "index.md" or rest == "requirements/unplaced.md":
            required = ["Code"]
        if len(parts) >= 2 and (parts[0] in ID_FOLDERS or parts[0] == "epics"):
            m = FILE_ID.match(parts[1])
            if m:
                file_id = m.group(1)
        out += check_title(path, lines, code)

    if file_id is not None and code and not file_id.startswith(code + "-"):
        out.append("%s: `%s` does not start with the Project code `%s`" % (path, file_id, code))
    if file_id is not None and not re.search(r"-\d{3}$", file_id):
        out.append("%s: `%s`: an ID ends in three digits" % (path, file_id))
    out += check_headers(path, block, required)
    if code:
        out += check_value(path, block, "Code", code, "the Project code")
    out += check_canonical(path, lines, veneer)
    out += check_duplicates(path, project, file_id)
    return out


# ---------------------------------------------------------------- main

def check_plans():
    """A change to any file in a Plan folder that HEAD already holds, other
    than `Shown:` lines appended to its plan record."""
    out, frozen = [], {}
    for path, status in sorted(staged_status().items()):
        m = PLAN_FOLDER.match(path)
        if m is None:
            continue
        folder = m.group(1)
        if folder not in frozen:
            frozen[folder] = bool(at_head(folder + "/"))
        if not frozen[folder]:
            continue
        shown = check_shown(path) if status == "M" and path == folder + "/" + PLAN_RECORD else None
        out += ["%s: %s" % (path, FROZEN_PLAN)] if shown is None else shown
    return out


def check_shown(path):
    """For a committed plan record changed only by appending lines: a problem
    for each appended line that is not a `Shown:` line. None for any other
    change."""
    old, new = show(path, "HEAD"), show(path)
    if old is None or new is None or not new.startswith(old) or not old.endswith("\n"):
        return None
    start = len(old.splitlines())
    out = []
    for n, line in enumerate(new[len(old):].splitlines(), start=start + 1):
        m = SHOWN.match(line)
        if m and real_date(m.group(1)):
            continue
        if not line.startswith("Shown:"):
            return None
        out.append("%s:%d: `%s` is not %s" % (path, n, line, SHOWN_FORM))
    return out


def check():
    """Every problem with what is staged, as `<path>[:<line>]: <problem>`."""
    paths = staged()
    veneer, veneer_problem = load_veneer()
    out = check_plans()
    if veneer_problem and any(p == "veneer.md" or p.startswith("outbox/") for p in paths):
        out.append(veneer_problem)
    projects = {}
    for path in paths:
        if path.startswith("outbox/"):
            out += check_outbox(path, veneer)
        elif re.fullmatch(r"log/\d{4}-\d{2}\.md", path):
            text = show(path)
            out += ["%s: not UTF-8 text" % path] if text is None else \
                check_log(path, text.splitlines(), "# Workspace log · %s" % path[4:-3])
        else:
            m = re.match(r"projects/([^/]+)/.+", path)
            if m:
                slug = m.group(1)
                if slug not in projects:
                    projects[slug] = Project(slug)
                    if projects[slug].code is None:
                        out.append("projects/%s/project.md: missing, or has no `Code:` header line" % slug)
                out += check_record(path, projects[slug], veneer)
    return out


def install():
    def refuse(why):
        print("Can't install the Guard: %s" % why, file=sys.stderr)
        return 1

    try:
        git("rev-parse", "--git-dir")
    except (RuntimeError, OSError):
        return refuse("this folder is not in a git repository.")
    hooks_path = subprocess.run(["git", "config", "core.hooksPath"], capture_output=True, text=True).stdout.strip()
    if hooks_path:
        return refuse("git's core.hooksPath is set (%s), so git runs the hooks there instead. "
                      "Add a pre-commit hook there that runs `python3 %s` from the Workspace."
                      % (hooks_path, os.path.abspath(__file__)))
    hook = os.path.abspath(git("rev-parse", "--git-path", "hooks/pre-commit").decode().strip())
    if os.path.exists(hook):
        with open(hook, encoding="utf-8", errors="replace") as f:
            if MARKER not in f.read():
                return refuse("%s is a pre-commit hook that isn't Jenny's, and is kept as it is. "
                              "Add a line to it that runs `python3 %s` from the Workspace."
                              % (hook, os.path.abspath(__file__)))
    os.makedirs(os.path.dirname(hook), exist_ok=True)
    with open(hook, "w", encoding="utf-8", newline="\n") as f:
        f.write(HOOK)
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return 0


def main(argv):
    if argv == ["--install"]:
        return install()
    if argv:
        print("usage: guard.py [--install]", file=sys.stderr)
        return 2
    try:
        os.chdir(git("rev-parse", "--show-toplevel").decode().strip())
        problems = check()
    except Exception as e:  # never a traceback: say what went wrong
        print("Jenny Guard: could not check this commit: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 1
    if not problems:
        return 0
    print("\n".join([HEADING] + problems + [FOOTER]), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
