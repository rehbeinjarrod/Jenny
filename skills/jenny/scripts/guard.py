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
  structure (header keys, section headings, table headers).
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

KINDS = "SRC|REQ|FEA|EPC|Q|ANS|SO"
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
}
# Rendered for readers outside the Workspace, in shown names.
RENDERED = re.compile(r"^(pack-v\d+|signoff-view-v\d+-.*)\.md$")


# ---------------------------------------------------------------- git

def git(*args):
    p = subprocess.run(["git", *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr.decode(errors="replace").strip()))
    return p.stdout


def staged():
    """Paths added or changed in the index (renames count as added)."""
    out = git("diff", "--cached", "--name-only", "-z", "--no-renames", "--diff-filter=ACM")
    return [p for p in out.decode("utf-8").split("\0") if p]


def indexed(prefix):
    out = git("ls-files", "-z", "--", prefix)
    return [p for p in out.decode("utf-8").split("\0") if p]


def show(path):
    """The staged text of `path`, or None when it is not UTF-8 text."""
    try:
        return git("show", ":" + path).decode("utf-8-sig")
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
        if self.root + "project.md" in self.files:
            text = show(self.root + "project.md") or ""
            code = header_block(text.splitlines()).get("Code")
            self.code = code[1] if code else None
        self._defs = None

    def definitions(self):
        """{ID: [(path, line or None)]}: ID-named files and folders, and the
        Requirement, Answer and Sign-off lines that define an ID."""
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
            if not path.endswith(".md") or RENDERED.match(parts[-1]) or parts[0] == "log":
                continue
            text = show(path) or ""
            for n, line in enumerate(text.splitlines(), start=1):
                m = DEFINITION.match(line) or SIGNOFF.match(line)
                if m and re.search(r"-(REQ|ANS|SO)-", m.group(1)):
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


def check_canonical(path, lines, veneer):
    """Shown names or aliases in a record's structure: header keys, section
    headings and table header rows."""
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
            out.append("%s:%d: `%s`: records use the canonical term %s, not its %s"
                       % (path, n, text.strip(), found[0], found[1]))
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
    if RENDERED.match(parts[-1]):
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
    elif len(parts) == 3 and parts[0] == "epics" and FILE_ID.match(parts[1]) and parts[2] in ("epic.md", "signoffs.md"):
        file_id = FILE_ID.match(parts[1]).group(1)
        if parts[2] == "epic.md":
            out += check_title(path, lines, code, file_id)
            required = ["Code", "Epic", "Feature"]
        else:
            out += check_title(path, lines, code)
            required = ["Code", "Epic"]
        out += check_value(path, block, "Epic", file_id, "the file's ID")
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

def check():
    """Every problem with what is staged, as `<path>[:<line>]: <problem>`."""
    paths = staged()
    veneer, veneer_problem = load_veneer()
    out = []
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
