#!/usr/bin/env python3
"""SO-01's diagram key lines: whether each flow diagram in a Sign-off view
explains itself, and whether the published page keeps that explanation around
each whiteboard.

    python3 "$REPO/acceptance/headless/graders/SO-01/diagrams.py" view "$V"
    python3 "$REPO/acceptance/headless/graders/SO-01/diagrams.py" page "$O"

Prints one line per diagram that falls short, and why; prints nothing when
every one is in shape. Always exits 0, so the key line reads its output.

In the view, each ```mermaid block has:

- a lead sentence: the last non-blank line before the fence is prose, not a
  heading, list, table or fence;
- node labels in words with IDs: each node besides the stadium-shaped start
  and stop (`id([…])`), bracketed or named bare on an edge, has a label with words beside its IDs (none a bare ID),
  at least one Requirement, Question or Decision ID, and at most 12 words
  besides the IDs (about 8 asked for);
- a walkthrough: the list straight after the fence has one top-level bullet
  per node, each naming its node in bold as the node's label does, in flow
  order (no bullet comes before the bullet for a node with an arrow into
  it), and each bullet marked 🔴 or 🟠 points back to its item
  ("see _Your calls_").

On the page, each whiteboard embed (`data-card-appearance="embed"`) has a
`<p>` straight before it and, after its Mermaid `<details>`, a `<ul>`.
"""

import re
import sys

ID = re.compile(r"\b[A-Z][A-Z0-9]*-(?:REQ|Q|ANS)-\d{3}\b")
ANY_ID = re.compile(r"\b[A-Z][A-Z0-9]*-[A-Z]+-\d{3}\b")  # an Epic or Source ID is still an ID, not words
# id( [ | { | (( | ( ) — `id([` is a stadium (start or stop) and has no label to grade.
NODE = re.compile(r"\b([A-Za-z_]\w*)(\(\(|\(\[|\[|\{|\()")
CLOSE = {"((": "))", "([": "])", "[": "]", "{": "}", "(": ")"}
KEYWORDS = {"classDef", "class", "style", "flowchart", "graph", "linkStyle", "subgraph", "end", "LR", "TD", "TB", "RL", "BT"}
ARROW = re.compile(r"-->|---|==>|-\.->")
BULLET = re.compile(r"^[-*] ")
WORD = re.compile(r"[A-Za-z][A-Za-z'’$%0-9-]*|\$?\d[\d,.]*%?")
POINTS_BACK = re.compile(r"\bsee _[^_]+_", re.I)


def graph(source):
    """The diagram's nodes besides start and stop, as [(node id, its label, or
    None when it has none)] in the order the source first names them, and its
    arrows as [(from id, to id)], start and stop included."""
    out, stadiums, arrows = {}, set(), []
    for line in source.splitlines():
        if line.strip().split(" ", 1)[0] in KEYWORDS:
            continue
        line = re.sub(r"\|[^|]*\|", " ", line)  # edge labels
        pos = 0
        bare = line
        while (m := NODE.search(line, pos)):
            opener = m.group(2)
            end = line.find(CLOSE[opener], m.end())
            if end < 0:
                break
            if opener == "([":
                stadiums.add(m.group(1))
            elif m.group(1) not in KEYWORDS:
                out.setdefault(m.group(1), line[m.end():end])
            bare = bare.replace(line[m.start():end + len(CLOSE[opener])], " " + m.group(1) + " ", 1)
            pos = end + len(CLOSE[opener])
        chain = [part.strip().rstrip(";") for part in ARROW.split(bare)]
        names = [n if re.fullmatch(r"[A-Za-z_]\w*", n) and n not in KEYWORDS else None for n in chain]
        for name in names:
            if name and name not in stadiums:
                out.setdefault(name, None)
        arrows += [(a, b) for a, b in zip(names, names[1:]) if a and b]
    return [(n, l) for n, l in out.items() if n not in stadiums], arrows


def words_of(text):
    return re.findall(r"[a-z0-9]+", ANY_ID.sub(" ", re.sub(r"<br\s*/?>", " ", text)).lower())


def named_node(bullet, found):
    """The node a walkthrough bullet names in bold, as its label says, or None."""
    bold = re.search(r"\*\*(.+?)\*\*", bullet)
    said = words_of(bold.group(1)) if bold else []
    for node, label in found:
        own = words_of(label or "")
        if said and own and (said == own[:len(said)] or own == said[:len(own)]):
            return node
    return None


def label_problems(node, label):
    if label is None:
        return [f"node {node} has no label"]
    text = re.sub(r"<br\s*/?>", " ", label).strip('"')
    words = WORD.findall(ANY_ID.sub(" ", text))
    if not words:
        return [f"node {node} is a bare ID ({text.strip()})"]
    problems = []
    if not ID.search(text):
        problems.append(f"node {node} has no ID ({text.strip()})")
    if len(words) > 12:
        problems.append(f"node {node} has {len(words)} words besides its IDs")
    return problems


def lead(lines, fence):
    """The last non-blank line before the fence at index `fence`, or ''."""
    k = fence - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    return lines[k].strip() if k >= 0 else ""


def walkthrough(lines, after):
    """The top-level bullets of the list after index `after`, each with its
    continuation lines joined on."""
    k = after + 1
    while k < len(lines) and not lines[k].strip():
        k += 1
    bullets = []
    while k < len(lines) and lines[k].strip() and (BULLET.match(lines[k]) or lines[k].startswith(" ")):
        if BULLET.match(lines[k]):
            bullets.append(lines[k])
        elif bullets:
            bullets[-1] += " " + lines[k].strip()
        k += 1
    return bullets


def diagram_problems(lines, fence, close):
    problems = []
    if not lead(lines, fence) or re.match(r"^(#|[-*] |\||```|>)", lead(lines, fence)):
        problems.append("no lead sentence before it")

    found, arrows = graph("\n".join(lines[fence + 1:close]))
    for node, label in found:
        problems += label_problems(node, label)

    bullets = walkthrough(lines, close)
    if not bullets:
        problems.append("no walkthrough after it")
    elif len(bullets) != len(found):
        problems.append(f"{len(bullets)} walkthrough bullets for {len(found)} nodes")
    place = {}
    for at, bullet in enumerate(bullets):
        node = named_node(bullet, found)
        if node is None:
            bold = re.search(r"\*\*(.+?)\*\*", bullet)
            problems.append(f"walkthrough bullet {bold.group(1) if bold else bullet[:40]!r} names no node")
        else:
            place.setdefault(node, at)
    against = [(a, b) for a, b in arrows if a in place and b in place and place[a] > place[b]]
    if against:
        problems.append(f"walkthrough is not in flow order: {against[0][1]} comes before {against[0][0]}, against the arrow")
    for bullet in bullets:
        if ("🔴" in bullet or "🟠" in bullet) and not POINTS_BACK.search(bullet):
            which = ID.findall(bullet)
            problems.append(f"walkthrough bullet {which[0] if which else bullet[:40]} does not point back to its item")
    return problems


def view_problems(text):
    lines = text.splitlines()
    out, count, heading, i = [], 0, "", 0
    while i < len(lines):
        if lines[i].startswith("#"):
            heading = lines[i].lstrip("#").strip()
        if lines[i].startswith("```mermaid"):
            count += 1
            close = i + 1
            while close < len(lines) and not lines[close].startswith("```"):
                close += 1
            problems = diagram_problems(lines, i, close)
            if problems:
                out.append(f"diagram {count} ({heading}): " + "; ".join(problems))
            i = close
        i += 1
    if count == 0:
        out.append("no diagram")
    return out


def page_problems(html):
    out = []
    embeds = list(re.finditer(r"<a\b[^>]*data-card-appearance=\"embed\"[^>]*>\s*</a>", html))
    for n, m in enumerate(embeds, 1):
        problems = []
        if not re.search(r"</p>\s*$", html[:m.start()]):
            problems.append("no lead <p> straight before the whiteboard")
        after = html[m.end():]
        details = re.match(r"\s*<details\b.*?</details>", after, re.S)
        rest = after[details.end():] if details else after
        if not details:
            problems.append("no Mermaid <details> after the whiteboard")
        if not re.match(r"\s*<ul\b", rest):
            problems.append("no walkthrough <ul> after the whiteboard")
        if problems:
            out.append(f"whiteboard {n}: " + "; ".join(problems))
    if not embeds:
        out.append("no whiteboard")
    return out


def main(argv):
    if len(argv) != 3 or argv[1] not in ("view", "page"):
        print("usage: diagrams.py view|page FILE", file=sys.stderr)
        return 0
    with open(argv[2], encoding="utf-8") as f:
        text = f.read()
    for line in (view_problems if argv[1] == "view" else page_problems)(text):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
