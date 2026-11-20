"""The Check value: one Check read once from its Markdown, the one reader of
its frontmatter, its Start and its Operator turns.

A Check holds:

- its frontmatter fields (id, version, skills, inputs, routing, promise), its
  path (repo-relative) and its text;
- its Start: the kind (`install`, `no install` or `engineer repo`, read only
  from `## Start`), whether the Workspace begins from the sample, whether an
  install session runs, the Start's `sh` block, and its MCP stand-ins;
- its Operator turns, word for word, with each `<paste: <file>>` replaced by
  that fixture's whole text and `<REPO>` by the clone's path: the clone it
  was loaded from;
- its key (`key`, a Key): Key at proposal and Key at write, read on first
  use and kept, so loading every Check (the Fingerprint, the gate planner)
  reads no key line: one Check's unreadable line raises only when that
  Check's key is read, as the runner does for every Check it is to run.

load() reads one Check by ID, load_all() every Check in a clone, by ID.
install_key() reads the Install key, in the same bullet form, from its
section of the Claude Code runner doc.

Key lines
---------

A key line is one bullet: its label, then its commands, each a code span with
the output it expects after ` → `: `exact text`, empty, or `<n> or more`.
`Each → <expectation>:` gives every command listed after it that expectation.
A command holding a backtick is in a double-backtick span. A key line is read
into a Line: its label and its (command, expectation) parts, the expectation
"" for empty and at_least(n) for `<n> or more`.

A prelude is the variables (`H=…`) and shell functions (`f() { …; }`) set in
code spans in the section's "Graded …" paragraph.

Which turns a Key at proposal line is graded after:

- a line under an `After turn <n>:` paragraph, after turn n;
- otherwise, a line whose commands name fixed replies (`$TURNS/<k>.md`),
  after each turn k they name, with that turn's commands and any that name
  no fixed reply;
- otherwise, after every proposal turn.

The proposal turns are the turns the "Graded …" paragraph names (`after turn
<n>`, `$TURNS/<n>.md`) and the `After turn <n>:` paragraphs.

A code span before a bullet's first command that sets a variable (`H=…`)
ends the label, and is set before each of the bullet's commands.

A sentence after the one a bullet's commands end in is prose, not graded.
A bullet with no command, or a command with no expectation, raises
KeyLineError naming the Check, the section and the bullet.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import NamedTuple

CHECKS = "acceptance/checks"
FIXTURES = "acceptance/fixtures"

INSTALL, NO_INSTALL, ENGINEER_REPO = "install", "no install", "engineer repo"


class CheckError(ValueError):
    pass


class KeyLineError(CheckError):
    pass


@dataclass(frozen=True)
class Start:
    """How a Check's Workspace is made before Jenny's first turn."""
    kind: str             # install | no install | engineer repo
    block: str | None = None  # the `sh` block: the change after install, or what lays the Workspace
    stand_ins: tuple = ()  # (URL, fixture) of each MCP stand-in

    @property
    def sample(self):
        """The Workspace begins from the committed sample: every kind but an Engineer repo."""
        return self.kind != ENGINEER_REPO

    @property
    def installs(self):
        """An install session runs before Jenny's first turn."""
        return self.kind == INSTALL


@dataclass(frozen=True)
class Check:
    """One Check, read once from its Markdown in the clone `root`."""
    id: str
    version: str
    path: str  # repo-relative
    skills: tuple
    inputs: tuple
    routing: bool
    promise: bool
    start: Start
    root: Path  # the clone it was loaded from
    text: str

    @property
    def turns(self):
        """The Operator script's turns, word for word, `<paste: …>` and `<REPO>`
        resolved against the clone."""
        def paste(m):
            return (self.root / FIXTURES / m.group(1)).read_text(encoding="utf-8").rstrip("\n")
        return [re.sub(r"<paste: ([^>]+)>", paste, t).replace("<REPO>", str(self.root))
                for t in operator_script(self.text)]

    @cached_property
    def key(self):
        """Its Key at proposal and Key at write, read on first use.
        KeyLineError for a bullet that can't be read."""
        return read_key(self.id, self.text)


def frontmatter(text):
    """The `key: value` lines between the opening `---` lines, values parsed as
    `[a, b]` lists, `true`/`false`, or plain strings; comments dropped."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if not sep:
            continue
        value = value.split(" #", 1)[0].strip()
        if value.startswith("[") and value.endswith("]"):
            out[key.strip()] = tuple(v.strip() for v in value[1:-1].split(",") if v.strip())
        elif value in ("true", "false"):
            out[key.strip()] = value == "true"
        else:
            out[key.strip()] = value
    return out


def section(text, heading, level=2):
    """The body under a heading of `level` (`## <heading>` by default), up to
    the next heading at that level or above it but the title."""
    m = re.search(rf"^{'#' * level} {re.escape(heading)}\n(.*?)(?=^#{{2,{level}}} |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def start(text, where="Check"):
    """The Start that a Check's text gives in its `## Start`. CheckError for
    more than one `sh` block."""
    body = section(text, "Start")
    kind = ENGINEER_REPO if "**Engineer repo.**" in body else NO_INSTALL if "**No install.**" in body else INSTALL
    blocks = re.findall(r"^```sh\n(.*?)\n```$", body, re.M | re.S)
    if len(blocks) > 1:
        raise CheckError(f"{where} Start: {len(blocks)} `sh` blocks, where one is the most")
    stand_ins = tuple(re.findall(r"MCP stand-in: `([^`]+)` → `([^`]+)`", body))
    return Start(kind, blocks[0] if blocks else None, stand_ins)


def operator_script(text):
    """The Operator script's numbered turns as written, a turn's later lines
    joined to it."""
    turns = []
    for line in section(text, "Operator script").splitlines():
        m = re.match(r"^\d+\. (.*)$", line)
        if m:
            turns.append(m.group(1))
        elif turns and line.strip():
            turns[-1] += "\n" + line
    return turns


def parse(text, root, path):
    """The Check that `text` writes, at `path` (repo-relative) in the clone
    `root`; None when its frontmatter has no `id`."""
    fm = frontmatter(text)
    if "id" not in fm:
        return None
    return Check(
        id=fm["id"], version=str(fm.get("version", "")), path=path,
        skills=tuple(fm.get("skills", ())), inputs=tuple(fm.get("inputs", ())),
        routing=fm.get("routing") is True, promise=fm.get("promise") is True,
        start=start(text, fm["id"]), root=Path(root), text=text)


def read(root, p):
    """The Check in the file `p` of the clone `root`, or None."""
    root = Path(root)
    return parse(p.read_text(encoding="utf-8"), root, p.relative_to(root).as_posix())


def load_all(root):
    """Every Check in the clone `root`, by ID."""
    root = Path(root)
    found = (read(root, p) for p in sorted((root / CHECKS).glob("*.md")))
    return {c.id: c for c in found if c is not None}


def load(check_id, root):
    """The Check `check_id` (its frontmatter `id`, whatever its file is named)
    in the clone `root`, the only Check parsed. KeyError when there is none."""
    root = Path(root)
    for p in sorted((root / CHECKS).glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if frontmatter(text).get("id") == check_id:
            return parse(text, root, p.relative_to(root).as_posix())
    raise KeyError(f"no Check {check_id} in {root / CHECKS}")


# ------------------------------------------------------------ key lines

ARROW = " → "
SETS = re.compile(r"[A-Za-z_]\w*(=|\(\) )")  # a code span that sets a variable or a shell function


def at_least(n):
    """The expectation `<n> or more`: a count of n or more."""
    return f"{n} or more"


AT_LEAST_ONE = at_least(1)


class Line(NamedTuple):
    """One key line: what it proves, as the Check words it, and its
    (command, expectation) parts."""
    label: str
    parts: tuple


@dataclass(frozen=True)
class Key:
    """A Check's Key at proposal and Key at write."""
    proposal_turns: tuple    # the turns whose replies Key at proposal grades, after each
    proposal_prelude: tuple  # set before each Key at proposal command
    write_prelude: tuple     # set before each Key at write command
    write: tuple             # the Key at write lines, graded after the last turn
    by_turn: tuple = ()      # (the turns it is graded after, or None for every turn; the line)

    def proposal(self, turn):
        """The Key at proposal lines graded after `turn`."""
        return [for_turn(l, turn) if turns and len(turns) > 1 else l
                for turns, l in self.by_turn if turns is None or turn in turns]


def bullets(body):
    return [line[2:] for line in body.splitlines() if line.startswith("- ")]


def spans(text):
    """(start, end, text) of each code span, as Markdown reads them: a run of
    backticks opens one and the next run of the same length closes it, so a
    span in double backticks may hold single and triple ones."""
    out, i = [], 0
    while True:
        m = re.compile(r"`+").search(text, i)
        if not m:
            return out
        close = re.compile(rf"(?<!`){m.group(0)}(?!`)").search(text, m.end())
        if not close:
            return out
        span = text[m.end():close.start()]
        if len(span) > 2 and span.startswith(" ") and span.endswith(" "):
            span = span[1:-1]
        out.append((m.start(), close.end(), span))
        i = close.end()


def code_spans(text):
    return [s for _, _, s in spans(text)]


def expectation(text):
    """The expectation at the start of `text` and where it ends: "" for empty,
    at_least(n) for `<n> or more`, else the text of a code span. None when
    `text` starts with none of these."""
    if text.startswith("empty"):
        return "", len("empty")
    m = re.match(r"(\d+) or more", text)
    if m:
        return at_least(int(m.group(1))), m.end()
    found = spans(text)
    if found and found[0][0] == 0:
        return found[0][2], found[0][1]
    return None


def turn_bodies(body):
    """{turn: its text} when the section splits its lines under `After turn
    <n>:` paragraphs, else None. Text before the first such paragraph is
    under None."""
    parts = re.split(r"^After turn (\d+):$", body, flags=re.M)
    if len(parts) == 1:
        return None
    return {None: parts[0], **{int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}}


def graded(body):
    """The section's "Graded …" paragraph."""
    return next((p for p in body.split("\n\n") if p.strip().startswith("Graded ")), "")


def prelude(body):
    return tuple(s for s in code_spans(graded(body)) if SETS.match(s))


def line(bullet, where):
    """The Line a bullet writes. `where` names the Check and section, for the
    error."""
    def fail(why):
        raise KeyLineError(f"{where}: {why}: - {bullet}")

    # Code spans and `Each → ` openers, in the order the bullet has them.
    events = [(start, end, cmd) for start, end, cmd in spans(bullet)]
    events += [(m.start(), m.end(), None) for m in re.finditer(r"\b[Ee]ach" + ARROW, bullet)]
    parts, label_end, each, pos, sets = [], None, None, 0, []
    for start, end, cmd in sorted(events):
        if start < pos:  # inside an expectation already read, or an opener inside a span
            continue
        if cmd is None:  # Each → <expectation>: the commands listed after it expect that
            got = expectation(bullet[end:])
            if got is None:
                fail("no expectation after Each →")
            each, pos = got[0], end + got[1]
        elif bullet.startswith(ARROW, end):
            got = expectation(bullet[end + len(ARROW):])
            if got is None:
                fail(f"no expectation for `{cmd}`")
            parts.append((cmd, got[0]))
            pos = end + len(ARROW) + got[1]
        elif each is not None:
            parts.append((cmd, each))
            pos = end
        elif not parts and SETS.match(cmd):  # set before the commands; ends the label
            sets.append(cmd)
            if label_end is None:
                label_end = start
            pos = end
            continue
        elif label_end is None:  # a code span in the label
            pos = end
            continue
        else:
            fail(f"no expectation for `{cmd}`")
        if label_end is None:
            label_end = start
        if parts and bullet.startswith(".", pos):  # the commands end; the rest is prose
            prose = bullet[pos:]
            if any(prose.startswith(ARROW, end) for _, end, _ in spans(prose)):
                fail("a command after the sentence its line's commands end")
            break
    if not parts:
        fail("no command")
    for cmd, _ in parts:  # graded after one turn, so it may name one turn's reply
        if len(fixed_turns(cmd)) > 1:
            fail(f"`{cmd}` names {len(fixed_turns(cmd))} fixed replies, where one is the most")
    return Line(bullet[:label_end].rstrip(), tuple(("; ".join([*sets, c]), e) for c, e in parts))


def lines(body, where):
    return [line(b, where) for b in bullets(body)]


def fixed_turns(cmd):
    """The turns whose replies a command names by number, `$TURNS/<k>.md`."""
    return {int(k) for k in re.findall(r"\$TURNS/(\d+)\.md", cmd)}


def for_turn(line, turn):
    """The line with only the commands for `turn`: those that name its reply
    or no fixed reply at all."""
    return Line(line.label, tuple((c, e) for c, e in line.parts if fixed_turns(c) <= {turn}))


def read_key(check_id, text):
    """The Key that a Check's text writes. KeyLineError for a bullet that
    can't be read, or a Key at write with no line."""
    body = section(text, "Key at proposal")
    turns = {int(n) for n in re.findall(r"after turn (\d+)", graded(body), re.I)}
    turns |= fixed_turns(graded(body))
    split = turn_bodies(body) or {None: body}
    turns |= {t for t in split if t is not None}
    by_turn = []
    for t, part in split.items():
        for l in lines(part, f"{check_id} Key at proposal"):
            fixed = set().union(*(fixed_turns(c) for c, _ in l.parts))
            by_turn.append(({t} if t is not None else fixed or None, l))
    write_body = section(text, "Key at write")
    write = tuple(lines(write_body, f"{check_id} Key at write"))
    if not write:
        raise KeyLineError(f"{check_id} Key at write: no key lines")
    return Key(tuple(sorted(turns)), prelude(body), prelude(write_body), write, tuple(by_turn))


def install_key(root):
    """The Install key lines, from the Install key section of the Claude Code
    runner doc in the clone `root`."""
    text = (Path(root) / "acceptance" / "runner" / "claude-code.md").read_text(encoding="utf-8")
    found = lines(section(text, "Install key", level=3), "Install key")
    if not found:
        raise KeyLineError("Install key: no key lines")
    return found
