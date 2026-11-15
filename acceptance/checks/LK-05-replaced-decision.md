---
id: LK-05
version: 7
skills: [lookup]
cursor-bench: false
routing: true
inputs: []
promise: false
---

# LK-05 · A replaced Decision returns the current one

The rule for late cancellation was decided once (the hirer forfeits the deposit) and later replaced (half the deposit comes back). Jenny answers with the current Decision and notes that it replaced the earlier one.

Grader: `acceptance/headless/graders/LK-05.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

Sample v7 as it is. No fixtures. The key relies on:

- `projects/hall-bookings/questions/HAL-Q-002-late-cancellation-refund.md`: `HAL-ANS-002` (withdrawn: deposit forfeited), replaced by `HAL-ANS-003` (half the deposit back, owner Margaret Osei).
- `projects/hall-bookings/features/HAL-FEA-002-cancel-a-booking.md`: `HAL-REQ-006` (withdrawn) replaced by `HAL-REQ-007` (half the deposit back).
- `projects/court-bookings/`: the leak-trap Project (24-hour rule, IDs `CRT-`).
- `veneer.md`: Question shown as Open item.

## Operator script

1. What does a hirer get back if they cancel a hall booking 10 hours before it starts?

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- The current rule. `grep -ciw 'half' "$TURNS/1.md"` → 1 or more.
- Cites the current Decision and Requirement. `grep -c 'HAL-ANS-003' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-REQ-007' "$TURNS/1.md"` → 1 or more.
- Names the current Decision's owner. `grep -c 'Margaret Osei' "$TURNS/1.md"` → 1 or more.
- Notes the replacement. `grep -c 'HAL-ANS-002' "$TURNS/1.md"` → 1 or more; `grep -ciE 'replac|supersed|withdr' "$TURNS/1.md"` → 1 or more.
- Stays in one Project. `grep -ciE 'CRT-|24 hours' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- Leads with the current rule (half the deposit); the forfeit rule appears only as what was replaced, with its date.
