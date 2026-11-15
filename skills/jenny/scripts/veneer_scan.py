#!/usr/bin/env python3
"""Veneer scan: name every Veneer-renamed canonical term in a reply.

Run from the Workspace root with the reply on stdin:

    python3 <skills>/jenny/scripts/veneer_scan.py <<'REPLY'
    ...the reply...
    REPLY

Reads `./veneer.md`. Every canonical term with a shown name is a hit wherever
it appears as a whole word, singular or plural, in any case, outside fenced
blocks and code spans. Prints one `<line>: <word>` per hit.

Exit codes: 0 clean, or no `veneer.md`; 1 hits; 2 `veneer.md` can't be read
(one line on stderr says why).

Python 3.9 or later, standard library only.
"""

import re
import sys

VENEER = "veneer.md"
HEADER = ["Canonical term", "Shown as", "Also understood as"]


class Unreadable(Exception):
    pass


def cells(line):
    """The cells of a Markdown table row, or None if the line isn't one.
    An escaped pipe stays inside its cell; bold or italic marks are dropped."""
    line = line.strip()
    if not line.startswith("|"):
        return None
    line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [re.sub(r"^[*_]+|[*_]+$", "", c.strip().replace("\\|", "|")).strip()
            for c in re.split(r"(?<!\\)\|", line)]


def renamed_terms(text):
    """Canonical terms to flag, from the Veneer table: each with a shown name,
    less any that is itself a shown name, since Jenny must say those."""
    return renamed(veneer_rows(text))


def renamed(rows):
    """renamed_terms, from rows already read by veneer_rows."""
    rows = [(term, shown) for term, shown, _ in rows if term and shown]
    shown_names = {shown.lower() for _, shown in rows}
    return [term for term, _ in rows if term.lower() not in shown_names]


def veneer_rows(text):
    """(canonical term, shown name, [aliases]) for each row of the Veneer
    table, cells as written (blank shown name: ""). Raises Unreadable."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if [c.lower() for c in cells(line) or []] == [h.lower() for h in HEADER]:
            break
    else:
        raise Unreadable("no table headed | " + " | ".join(HEADER) + " |")

    rule = cells(lines[i + 1]) if i + 1 < len(lines) else None
    if rule is None or len(rule) != len(HEADER) or not all(re.fullmatch(r":?-+:?", c) for c in rule):
        raise Unreadable("the table's header has no --- row under it")

    rows = []
    for n, line in enumerate(lines[i + 2:], start=i + 3):
        row = cells(line)
        if row is None:
            break
        if not 2 <= len(row) <= len(HEADER):
            raise Unreadable("line %d has %d cells, not %d" % (n, len(row), len(HEADER)))
        aliases = [a.strip() for a in row[2].split(",")] if len(row) > 2 else []
        rows.append((row[0], row[1], [a for a in aliases if a]))
    return rows


def term_pattern(term):
    """A term as a whole word or phrase, its last word singular or plural."""
    words = term.split()
    last = words[-1]
    if re.search(r"[^aeiou]y$", last, re.I):
        last = re.escape(last[:-1]) + "(?:y|ies)"
    elif re.search(r"(?:s|x|z|ch|sh)$", last, re.I):
        last = re.escape(last) + "(?:es)?"
    else:
        last = re.escape(last) + "s?"
    return r"\s+".join([re.escape(w) for w in words[:-1]] + [last])


def hit_finder(terms):
    if not terms:
        return None
    # Longest first, so "Epic pack" is one hit, not "Epic".
    alts = [term_pattern(t) for t in sorted(terms, key=len, reverse=True)]
    return re.compile(r"(?<!\w)(?:" + "|".join(alts) + r")(?!\w)", re.I)


FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def blank_code_spans(line):
    """The line with every inline code span replaced by spaces."""
    out, i = [], 0
    while i < len(line):
        if line[i] != "`":
            out.append(line[i])
            i += 1
            continue
        run = re.match(r"`+", line[i:]).group()
        close = re.compile(r"(?<!`)" + run + r"(?!`)")
        m = close.search(line, i + len(run))
        if m is None:
            out.append(run)  # no closing run: literal backticks
            i += len(run)
        else:
            out.append(" " * (m.end() - i))
            i = m.end()
    return "".join(out)


def prose_lines(reply):
    """(line number, text) for each line outside fenced blocks, spans blanked."""
    fence = None
    for n, line in enumerate(reply.splitlines(), start=1):
        m = FENCE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                continue
            yield n, blank_code_spans(line)
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                and not line[m.end():].strip():
            fence = None


def scan(reply, terms):
    finder = hit_finder(terms)
    if finder is None:
        return []
    return [(n, m.group()) for n, line in prose_lines(reply) for m in finder.finditer(line)]


def main():
    try:
        with open(VENEER, encoding="utf-8-sig") as f:
            terms = renamed_terms(f.read())
    except FileNotFoundError:
        return 0
    except (OSError, UnicodeDecodeError, Unreadable) as e:
        print("Can't read %s: %s" % (VENEER, e), file=sys.stderr)
        return 2

    reply = sys.stdin.read()
    hits = scan(reply, terms)
    for n, word in hits:
        print("%d: %s" % (n, re.sub(r"\s+", " ", word)))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
