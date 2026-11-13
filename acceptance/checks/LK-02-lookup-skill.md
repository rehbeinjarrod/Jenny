---
id: LK-02
version: 6
skills: [lookup]
cursor-bench: false
repeat-at-gate: true
---

# LK-02 · The same question through `/lookup`

LK-01's question, asked through `/lookup`. Same answer and citations as LK-01, laid out in the fixed answer shape: in short, what it is based on, and what is not known yet.

## Start

Sample v7 as it is. No fixtures. The key relies on:

- `projects/hall-bookings/features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-002` (deposit 20% of the hire fee, minimum $50) and `HAL-REQ-003` (main hall $30 an hour for members, $45 for non-members).
- `projects/court-bookings/`: the leak-trap Project, whose IDs start `CRT-`.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. /lookup How much deposit does a non-member pay to book the main hall for three hours?

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- The fixed answer shape, three labelled parts. `grep -cE '^\*\*(In short|Based on|Not known yet)\*\*' "$TURNS/1.md"` → `3`.
- The right amount. `grep -c '\$50' "$TURNS/1.md"` → 1 or more.
- Not the 20% figure as the deposit. `grep -ciE '(deposit (is|of)|pays?( a)?) \$27|\$27 deposit' "$TURNS/1.md"` → `0`.
- The amount is the short answer. `sed -n '/^\*\*In short\*\*/,/^\*\*Based on\*\*/p' "$TURNS/1.md" | grep -c '\$50'` → 1 or more.
- Cites both Requirements. `grep -c 'HAL-REQ-002' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-REQ-003' "$TURNS/1.md"` → 1 or more.
- Cites the file. `grep -c 'features/HAL-FEA-001-book-and-pay.md' "$TURNS/1.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.
- (soft) Never says a renamed canonical term (Project, Epic, Question) outside code spans. `sed 's/`[^`]*`//g' "$TURNS/1.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- The answer matches LK-01's in substance.
- "Not known yet" says plainly when nothing is open on this point, rather than padding.
