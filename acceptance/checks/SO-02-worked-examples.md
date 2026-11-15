---
id: SO-02
version: 2
skills: [signoff]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# SO-02 · Sign-off view: worked examples cite their ID and add up

The Operator asks for Margaret's Sign-off view of the hall's book-and-pay Epic and confirms it. The view's worked examples are invented, marked as made up, and each cites the ID of the open item or Decision whose gap it shows. Applying the hall's rules to each example's stated inputs gives its stated outcome.

Grader: `acceptance/headless/graders/SO-02.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

As SO-01: Sample v7, then after install the overlay below, committed as `Overlay: HAL-EPC-001 pack v2 for Sign-off`:

```sh
cp -r "$REPO/acceptance/fixtures/signoff/hall-bookings/." "$WS/projects/hall-bookings/" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 pack v2 for Sign-off"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-002` (deposit 20% of the hire fee, minimum $50), `HAL-REQ-003` ($30 an hour for members, $45 for non-members).
- `questions/`: `HAL-ANS-001` (the deposit rule), `HAL-ANS-004` (a booking runs until midnight, no later), `HAL-ANS-005` (no cleaning fee); `HAL-Q-007` open and being built on a guess (member rate for a non-member's event).
- `epics/HAL-EPC-001-book-and-pay/pack-v2.md`: the latest pack.

## Operator script

1. Sign-off view for Margaret, the book and pay spec.
2. Yes, write it.

## Key at proposal

Graded after turn 1.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more.

## Key at write

Graded after turn 2. `V="$WS/projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret.md"`, `ex() { grep -E '^\s*[-*] \*\*Example\*\*' "$V"; }` (the worked-example lines), and `sec() { awk -v h="^## $1" '$0 ~ h {f=1; next} /^## /{f=0} f' "$V"; }`.

- One commit; the view is new. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" diff --name-status "$BASE" HEAD -- projects/hall-bookings/epics/` → `A	projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret.md`.
- There are worked examples, one for the guess. `ex | wc -l` → 2 or more; `sec 🔴 | grep -E '^\s*[-*] \*\*Example\*\*' | grep -c 'HAL-Q-007'` → 1 or more.
- Each is marked as made up. `ex | grep -civ 'made up'` → `0`.
- Each cites the ID it shows. `ex | grep -cvE 'HAL-(Q|ANS)-[0-9]{3}'` → `0`.
- Each states its inputs in numbers. `ex | grep -cv '[0-9]'` → `0`.
- The numbers add up: every line's stated outcome follows from its stated inputs. `ex | python3 "$REPO/acceptance/headless/graders/SO-02/sums.py"` → empty. The script prints each line that doesn't add up, and why, by these rules: hire fee = hours × $30 for a member or × $45 for a non-member, with no cleaning fee (`HAL-REQ-003`, `HAL-ANS-005`); deposit = the larger of $50 and 20% of the hire fee (`HAL-REQ-002`, `HAL-ANS-001`); no booking ends after midnight (`HAL-ANS-004`); a line citing `HAL-Q-007` gives the outcome under each answer (member rate and non-member rate) and calls neither settled.

## By eye

- Each example sits under the item it illustrates and shows what changes with the answer, not just restates the rule.
- No example is presented as agreed or as a real booking.
