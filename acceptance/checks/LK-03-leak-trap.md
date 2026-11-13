---
id: LK-03
version: 4
skills: [lookup]
cursor-bench: false
repeat-at-gate: true
---

# LK-03 · Leak trap: same words, other Project

The Operator asks about deposits and late cancellation in the court bookings Project, which uses the same words as the hall Project with different rules. Jenny answers from the court records only and pulls in no hall rule.

## Start

Sample v7 as it is. No fixtures. The key relies on:

- `projects/court-bookings/features/CRT-FEA-001-book-and-cancel-a-court.md`: `CRT-REQ-001` (paid in full at booking, no deposit) and `CRT-REQ-003` (cancelling less than 24 hours before the start gets no refund).
- `projects/hall-bookings/features/HAL-FEA-001-book-and-pay.md` and `HAL-FEA-002-cancel-a-booking.md`: the hall rules that must not leak (20% deposit, $50 minimum, 48 hours, half the deposit back).
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. In the court bookings initiative, does a booking take a deposit, and what does someone get back if they cancel two hours before it starts?

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says there is no deposit. `grep -ciE 'no deposit|not take a deposit|paid in full|pays? (the )?(whole|full)' "$TURNS/1.md"` → 1 or more.
- Says nothing comes back. `grep -ciE 'no refund|nothing back|gets? nothing|not get anything' "$TURNS/1.md"` → 1 or more.
- Cites the court rules. `grep -c 'CRT-REQ-001' "$TURNS/1.md"` → 1 or more; `grep -c 'CRT-REQ-003' "$TURNS/1.md"` → 1 or more.
- Cites the court file. `grep -c 'CRT-FEA-001-book-and-cancel-a-court.md' "$TURNS/1.md"` → 1 or more.
- No hall IDs. `grep -c 'HAL-' "$TURNS/1.md"` → `0`.
- No hall rules. `grep -ciE '48[ -]hour|20 ?%|\$50|half' "$TURNS/1.md"` → `0`.
- (soft) Never says a renamed canonical term (Project, Epic, Question) outside code spans. `sed 's/`[^`]*`//g' "$TURNS/1.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- Says plainly there is no deposit (paid in full) and nothing comes back inside 24 hours.
- Does not compare with the hall Project or mention it.
