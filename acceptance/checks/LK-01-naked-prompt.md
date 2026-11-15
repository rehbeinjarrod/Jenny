---
id: LK-01
version: 7
skills: [lookup]
cursor-bench: false
routing: true
inputs: []
promise: false
---

# LK-01 · A plain-words question about deposits

The Operator asks a question in plain words, with no `/lookup`. Jenny works out the answer from two Requirements in one Feature, cites the IDs and the file, stays inside the hall Project, writes nothing, and speaks in Veneer names.

Grader: `acceptance/headless/graders/LK-01.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

Sample v7 as it is. No fixtures. The key relies on:

- `projects/hall-bookings/features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-002` (deposit 20% of the hire fee, minimum $50) and `HAL-REQ-003` (main hall $30 an hour for members, $45 for non-members).
- `projects/court-bookings/`: the leak-trap Project, whose IDs start `CRT-`.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. How much deposit does a non-member pay to book the main hall for three hours?

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- The right amount: 3 × $45 = $135, 20% is $27, so the $50 minimum applies. `grep -c '\$50' "$TURNS/1.md"` → 1 or more.
- Not the 20% figure as the deposit. `grep -ciE '(deposit (is|of)|pays?( a)?) \$27|\$27 deposit' "$TURNS/1.md"` → `0`.
- Cites both Requirements. `grep -c 'HAL-REQ-002' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-REQ-003' "$TURNS/1.md"` → 1 or more.
- Cites the file. `grep -c 'features/HAL-FEA-001-book-and-pay.md' "$TURNS/1.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- The working is shown ($135, 20% is $27, below the $50 minimum) so the Operator can check it.
- Short: the answer comes first, then what it rests on.
