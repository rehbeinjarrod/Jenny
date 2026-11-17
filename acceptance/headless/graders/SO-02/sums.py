#!/usr/bin/env python3
"""SO-02's "The numbers add up" key line: whether each worked example's stated
outcome follows from its stated inputs by the hall's rules.

    ex | python3 "$REPO/acceptance/headless/graders/SO-02/sums.py"

Reads worked-example lines on stdin and prints one line per example whose
numbers don't add up (`<n>: <why>`, n counting the lines read); prints nothing
when every one adds up. Always exits 0, so the key line reads its output.

The rules (acceptance/checks/SO-02-worked-examples.md):

- hire fee = hours × $30 for a member or × $45 for a non-member, with no
  cleaning fee (HAL-REQ-003, HAL-ANS-005);
- deposit = the larger of $50 and 20% of the hire fee (HAL-REQ-002, HAL-ANS-001);
- no booking ends after midnight (HAL-ANS-004);
- a line citing HAL-Q-007 gives the outcome under each answer (the member and
  the non-member rate) and calls neither settled.

An example's inputs are its hours (`6 hours`, `5-hour`, or a time span such as
`7 pm to midnight`) and who books; with no hours, a hire fee it states is taken
as given. Every dollar figure in the line must then be a rate, the $50
minimum, a hire fee, 20% of one or a deposit those inputs give; each figure it
calls a hire fee, a deposit or 20% must be that one; each product it works
(`6 x $30 = $180`, `5 hours at $30 is $150`) must hold; the hours its times
give must be hours it states; and a time past midnight must be refused. A span
past midnight that its own clause refuses (`8 pm to 1 am is not allowed`, or a
bare `one from 7 pm to 1 am is not.`) is no booking, so it states no hours and
gives none. So is one an example's scenario asks for when the first clause of
its `Outcome:` refuses it or holds it to midnight (`… from 8 pm to 1 am.
Inputs: … Outcome: the booking is refused.`, `… Outcome: the latest end is
midnight`). A span the Outcome itself books past midnight is still graded.
The Outcome is the shape examples.py joins onto one line.

A figure followed by `higher`, `lower`, `more`, `less`, `cheaper` or `dearer`
may also be the gap between two fees or deposits the line states (`the hire
fee is $60 higher`). Any other difference, such as a fee less its deposit, is
a figure no rule gives.
"""

import re
import sys

MEMBER, NON_MEMBER = 30, 45
MINIMUM, SHARE = 50, 0.2
GUESS = "HAL-Q-007"

MONEY = r"\$(\d+(?:\.\d{1,2})?)"
REFUSED = re.compile(r"not (?:be )?(?:allowed|accepted|possible)|refused|cannot|can't|would not|isn't allowed|"
                     r"no later|too late|turned down", re.I)
# "…; one from 7 pm to 1 am is not." refuses only within its own clause.
BARE_REFUSAL = re.compile(r"\b(?:is|are) not\s*$", re.I)
CLAUSE_END = re.compile(r"[.;!?,]|:(?!\d)")  # the colon in `1:30 am` ends no clause
GAP_WORDS = r"\s*(?:higher|lower|more|less|cheaper|dearer)\b"
GAP_WORD = re.compile(GAP_WORDS, re.I)
NOT_GAP = r"(?!\d|\.\d|" + GAP_WORDS + ")"
NEGATION = re.compile(r"\b(?:neither|not|none|nothing|no|isn't|aren't|un\w+)\b", re.I)


def cents(x):
    return round(float(x) * 100)


def clock(h, half):
    """The hour of the day, 0 to 24 at midnight, past 24 into the next morning."""
    h = int(h) % 12
    return h + 12 if half == "pm" else h + 24  # an `am` end is the next morning


def refused_here(t, end_at):
    """Whether the clause running on from the end time at index `end_at` refuses it:
    `1 am is not allowed`, `1 am is not.`. A refusal in another clause refuses
    something else."""
    stop = CLAUSE_END.search(t, end_at)
    clause = t[end_at:stop.start() if stop else len(t)]
    return bool(REFUSED.search(clause) or BARE_REFUSAL.search(clause))


# An outcome that holds the asked-for span to midnight: `the latest end is midnight`.
MIDNIGHT = re.compile(r"\bmidnight\b", re.I)


def refused_by_outcome(t, end_at):
    """Whether a span asked for in the example's scenario (before its `Inputs:`)
    is refused, or held to midnight, by its `Outcome:`: the shape
    examples.py joins onto one line."""
    inputs = t.find("Inputs:")
    outcome = re.search(r"Outcome:\s*", t)
    if inputs < 0 or end_at > inputs or not outcome:
        return False
    said = t[outcome.end():]
    return bool(REFUSED.search(said) or MIDNIGHT.search(said))


def spans(t):
    """(start, end, end_at) of each `<h> am|pm to midnight|<h> am|pm`, ends past 24 the
    next morning, `end_at` the index of its end time."""
    out = []
    for m in re.finditer(r"\b(\d{1,2})(?::\d\d)? ?(am|pm) (?:to|until|till|-|–) "
                         r"(midnight|(\d{1,2})(?::\d\d)? ?(am|pm))", t, re.I):
        start = int(m.group(1)) % 12 + (12 if m.group(2).lower() == "pm" else 0)
        end = 24 if m.group(3).lower() == "midnight" else clock(m.group(4), m.group(5).lower())
        out.append((start, end, m.start(3)))
    return out


def rates(t):
    if GUESS in t:
        return {MEMBER, NON_MEMBER}
    non = re.search(r"non-?members?\b", t, re.I)
    member = re.search(r"(?<![-\w])(?<!non )members?\b", t, re.I)
    if non and not member:
        return {NON_MEMBER}
    if member and not non:
        return {MEMBER}
    return {MEMBER, NON_MEMBER}


def deposit(fee):
    return max(cents(MINIMUM), round(fee * SHARE))


def wrong(line):
    """Each way the example's numbers don't add up; empty when they do."""
    t = line.replace("`", "").replace("×", "x").replace("*", "")
    problems = []

    stated = {int(h) for h in re.findall(r"\b(\d+)[ -]hours?\b", t, re.I)}
    hours = set(stated)
    for start, end, end_at in spans(t):
        if end > 24 and (refused_here(t, end_at) or refused_by_outcome(t, end_at)):
            continue
        if stated and end - start not in stated:
            problems.append(f"{start}:00 to {end % 24}:00 is {end - start} hours, not {sorted(stated)}")
        hours.add(end - start)
    # An end time in the small hours; 12 am is midnight itself, which a booking may end on.
    past = [m.group(0) for m in re.finditer(r"\b(?:to|until|till) (?:1[01]|[1-9])(?::\d\d)? ?am\b", t, re.I)
            if not (REFUSED.search(t) or refused_here(t, m.start()) or refused_by_outcome(t, m.start()))]
    if past:
        problems.append(f"ends after midnight ({past[0]}) and is not refused")

    rate = rates(t)
    fees = {cents(h * r) for h in hours for r in rate}
    if not hours:
        fees = {cents(f) for f in re.findall(r"hire fee (?:is|of) " + MONEY, t, re.I)}
    shares = {round(f * SHARE) for f in fees}
    deposits = {deposit(f) for f in fees}
    allowed = {cents(r) for r in rate} | {cents(MINIMUM)} | fees | shares | deposits
    # A gap between two of the line's own fees or deposits: `the hire fee is $60 higher`.
    said = {cents(x) for x in re.findall(MONEY, t)}
    gaps = {abs(a - b) for kind in (fees, deposits) for a in said & kind for b in said & kind if a != b}

    for m in re.finditer(MONEY, t):
        x = m.group(1)
        if cents(x) in allowed:
            continue
        if GAP_WORD.match(t, m.end()) and cents(x) in gaps:
            continue
        problems.append(f"${x} follows from no input")

    def claims(patterns, want, what):
        for p in patterns:
            for m in re.finditer(p, t, re.I):
                for x in filter(None, m.groups()):
                    if cents(x) not in want:
                        problems.append(f"${x} is not {what}")

    claims([r"hire fee (?:is|of) " + MONEY + NOT_GAP, MONEY + r" hire fee"], fees, "the hire fee")
    claims([r"deposit (?:is|of|would be|becomes)? ?(?:only |just |still |the )*" + MONEY + NOT_GAP,
            MONEY + r" deposit"], deposits, "the deposit")
    claims([r"20% (?:of " + r"\$\d+(?:\.\d+)? )?is (?:only |just )?" + MONEY + r"(?: or " + MONEY + ")?"],
           shares, "20% of the hire fee")
    for m in re.finditer(r"20% of " + MONEY + r" is " + MONEY, t, re.I):
        if round(cents(m.group(1)) * SHARE) != cents(m.group(2)):
            problems.append(f"20% of ${m.group(1)} is not ${m.group(2)}")

    for a, b, c in re.findall(r"\$?(\d+) x \$?(\d+) (?:=|is) (?:a |an )?(?:hire fee of )?" + MONEY, t, re.I):
        if cents(a) * int(b) != cents(c) and cents(b) * int(a) != cents(c):
            problems.append(f"{a} x {b} is not ${c}")
    for h, r, c in re.findall(r"\b(\d+) hours? at " + MONEY + r"(?: an hour)? (?:is|=|comes to) (?:a |an )?"
                              r"(?:hire fee of )?" + MONEY, t, re.I):
        if int(h) * cents(r) != cents(c):
            problems.append(f"{h} hours at ${r} is not ${c}")

    if GUESS in t:
        shown = {cents(x) for x in re.findall(MONEY, t)}
        if not any(cents(h * MEMBER) in shown and cents(h * NON_MEMBER) in shown for h in hours):
            problems.append("does not give the outcome at both the member and the non-member rate")
        for sentence in re.split(r"(?<=[.;!?])\s+", t):
            if re.search(r"\b(?:settled|agreed|decided)\b", sentence, re.I) and not NEGATION.search(sentence):
                problems.append(f"calls an answer settled: {sentence.strip()}")
    return problems


def main():
    for n, line in enumerate(sys.stdin.read().splitlines(), 1):
        if line.strip():
            problems = wrong(line)
            if problems:
                print(f"{n}: " + "; ".join(problems))
    return 0


if __name__ == "__main__":
    sys.exit(main())
