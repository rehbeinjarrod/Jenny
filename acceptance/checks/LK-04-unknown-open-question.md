---
id: LK-04
version: 6
skills: [lookup]
cursor-bench: false
repeat-at-gate: true
---

# LK-04 · Unknown points at the open Question

The Operator asks something the hall records do not settle. Jenny says it is not known, names the open Question that covers it and who it is waiting on, and invents nothing: no guessed answer, and least of all the court Project's rule for the same case.

## Start

Sample v7 as it is. No fixtures. The key relies on:

- `projects/hall-bookings/questions/HAL-Q-003-committee-cancels.md`: `HAL-Q-003`, open, on what happens to the deposit when the hall committee cancels a booking. It has no `Ask:` line: nobody has been asked yet.
- `projects/hall-bookings/questions/index.md`: lists `HAL-Q-003` as open.
- `projects/court-bookings/features/CRT-FEA-001-book-and-cancel-a-court.md`: `CRT-REQ-004`, the court rule for the same case (full refund plus a $20 credit), which must not leak.
- `veneer.md`: Question shown as Open item.

## Operator script

1. If the hall committee has to cancel someone's booking, what happens to their deposit?

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Points at the open Question. `grep -c 'HAL-Q-003' "$TURNS/1.md"` → 1 or more.
- Says it is not known. `grep -ciE 'not (yet )?(known|settled|decided|answered)|unknown|open item|no answer' "$TURNS/1.md"` → 1 or more.
- Cites where the Question is. `grep -cE 'questions/(HAL-Q-003-committee-cancels|index)\.md' "$TURNS/1.md"` → 1 or more.
- Nothing invented from the court Project. `grep -ciE '\$20|credit|CRT-' "$TURNS/1.md"` → `0`.
- No guessed answer in the gap. `sed -n '/Not known yet/,$p' "$TURNS/1.md" | grep -ciE 'probabl|likely|might|could|perhaps|possib|option|for example|such as|e\.g\.|credit|rebook|another date'` → `0`.
- Says who the gap is waiting on. `sed -n '/Not known yet/,$p' "$TURNS/1.md" | grep -ciE 'waiting on|not (been )?asked|nobody|no one'` → 1 or more.
- (soft) Never says a renamed canonical term (Project, Epic, Question) outside code spans. `sed 's/`[^`]*`//g' "$TURNS/1.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- No guessed answer, not even hedged ("probably a full refund").
- May say the 48-hour rule covers only cancellations by the hirer, citing it, as long as it does not stretch it to this case.
