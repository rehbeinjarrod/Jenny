"""The Key-line parser: a Check's key lines, read from its Markdown as written.

From the Check it reads Key at proposal and Key at write, their preludes, the
proposal turns and the Start's `sh` block, into a Key: the shape grade.py
grades (PROPOSAL_TURNS, proposal(turn), write(), PROPOSAL_PRELUDE, PRELUDE,
AFTER_INSTALL, LAY), built from grade.Line.

A key line is one bullet: its label, then its commands, each a code span with
the output it expects after ` → `: `exact text`, empty, or `<n> or more`.
`Each → <expectation>:` gives every command listed after it that expectation.
A command holding a backtick is in a double-backtick span.

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

install_key() reads the Install key, in the same bullet form, from its
section of the Claude Code runner doc.

A sentence after the one a bullet's commands end in is prose, not graded.
A bullet with no command, or a command with no expectation, raises
KeyLineError naming the Check, the section and the bullet.
"""

import re
from pathlib import Path

import grade

ARROW = " → "
SETS = re.compile(r"[A-Za-z_]\w*(=|\(\) )")  # a code span that sets a variable or a shell function


class KeyLineError(ValueError):
    pass


def section(text, heading, level=2):
    """The body under a heading of `level` (`##` by default), up to the next
    heading at that level or above."""
    m = re.search(rf"^{'#' * level} {re.escape(heading)}\n(.*?)(?=^#{{1,{level}}} |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


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
    """The expectation at the start of `text` and where it ends, as grade.Line
    holds it: "" for empty, grade.at_least(n) for `<n> or more`, else the text
    of a code span. None when `text` starts with none of these."""
    if text.startswith("empty"):
        return "", len("empty")
    m = re.match(r"(\d+) or more", text)
    if m:
        return grade.at_least(int(m.group(1))), m.end()
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
    """The grade.Line a bullet writes. `where` names the Check and section,
    for the error."""
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
    return grade.Line(bullet[:label_end].rstrip(), [("; ".join([*sets, c]), e) for c, e in parts])


def lines(body, where):
    return [line(b, where) for b in bullets(body)]


def fixed_turns(cmd):
    """The turns whose replies a command names by number, `$TURNS/<k>.md`."""
    return {int(k) for k in re.findall(r"\$TURNS/(\d+)\.md", cmd)}


def for_turn(line, turn):
    """The line with only the commands for `turn`: those that name its reply
    or no fixed reply at all."""
    return grade.Line(line.label, [(c, e) for c, e in line.parts if fixed_turns(c) <= {turn}])


class Key:
    """A Check's key lines, in the shape grade.py grades."""

    def __init__(self, check_id, text, kind):
        body = section(text, "Key at proposal")
        self.PROPOSAL_PRELUDE = prelude(body)
        turns = {int(n) for n in re.findall(r"after turn (\d+)", graded(body), re.I)}
        turns |= fixed_turns(graded(body))
        by_turn = turn_bodies(body) or {None: body}
        turns |= {t for t in by_turn if t is not None}
        self.PROPOSAL_TURNS = tuple(sorted(turns))
        self._proposal = []  # (the turns it is graded after, or None for every turn; the line)
        for t, part in by_turn.items():
            for l in lines(part, f"{check_id} Key at proposal"):
                fixed = set().union(*(fixed_turns(c) for c, _ in l.parts))
                self._proposal.append(({t} if t is not None else fixed or None, l))
        body = section(text, "Key at write")
        self.PRELUDE = prelude(body)
        self._write = lines(body, f"{check_id} Key at write")
        if not self._write:
            raise KeyLineError(f"{check_id} Key at write: no key lines")
        blocks = re.findall(r"^```sh\n(.*?)\n```$", section(text, "Start"), re.M | re.S)
        if len(blocks) > 1:
            raise KeyLineError(f"{check_id} Start: {len(blocks)} `sh` blocks, where one is the most")
        block = blocks[0] if blocks else None
        self.AFTER_INSTALL = block if kind == "install" else None
        self.LAY = block if kind != "install" else None

    def proposal(self, turn):
        return [for_turn(l, turn) if turns and len(turns) > 1 else l
                for turns, l in self._proposal if turns is None or turn in turns]

    def write(self):
        return list(self._write)


def check_file(check_id, repo):
    found = sorted((Path(repo) / "acceptance" / "checks").glob(f"{check_id}-*.md"))
    if not found:
        raise grade.NoGrader(f"no Check {check_id} in {Path(repo) / 'acceptance' / 'checks'}")
    return found[0]


def install_key(repo=grade.REPO):
    """The Install key lines, from the Install key section of the Claude Code
    runner doc in `repo`."""
    text = (Path(repo) / "acceptance" / "runner" / "claude-code.md").read_text(encoding="utf-8")
    found = lines(section(text, "Install key", level=3), "Install key")
    if not found:
        raise KeyLineError("Install key: no key lines")
    return found


def load(check_id, repo=grade.REPO):
    """The Key of the Check `check_id` in `repo`."""
    text = check_file(check_id, repo).read_text(encoding="utf-8")
    return Key(check_id, text, grade.start(check_id, repo))
