---
id: CP-03
version: 9
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# CP-03 · Meeting notes: the planted conflict becomes a Question

The Operator drops in committee meeting notes. One point contradicts an active Requirement (non-members booking six months ahead, not three): Jenny raises a Question citing both Sources and leaves the Requirement as it is. Another point answers an open Question with a Decision that rests on a third-party code of practice: Jenny asks or confirms its owner, keeps the code's location and its own words, and copies none of the code's text.

## Start

Sample v7 as it is. Fixture: `acceptance/fixtures/capture/meeting-notes.md` (the conflict; a quoted paragraph from an invented third-party code of practice, section 3.4; the committee's call on what a hirer gets back when the committee cancels). The key relies on:

- `projects/hall-bookings/features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-004` (members six months ahead, non-members three), from `HAL-SRC-001`: the Requirement in conflict.
- `projects/hall-bookings/questions/HAL-Q-003-committee-cancels.md`: `HAL-Q-003`, open, `Affects: HAL-REQ-005, HAL-REQ-007`: the Question the notes answer.
- `projects/hall-bookings/features/HAL-FEA-002-cancel-a-booking.md`: `HAL-REQ-005` and `HAL-REQ-007`, which the Answer leaves unchanged.
- `projects/hall-bookings/project.md`: Margaret Osei is a Stakeholder.
- `projects/hall-bookings/`: highest IDs `HAL-SRC-005`, `HAL-REQ-013`, `HAL-Q-013`, `HAL-ANS-003`, so the new Source is `HAL-SRC-006`, the conflict Question `HAL-Q-014` and the Answer `HAL-ANS-004`.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Here are the notes from yesterday's hall committee, capture them: <paste: capture/meeting-notes.md>
2. Margaret Osei owns the decision on what happens when we cancel.
3. Yes, write it.

## Key at proposal

Graded after turn 1 (on `$TURNS/1.md`) and again after turn 2 (on `$TURNS/2.md`).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/<n>.md"` → 1 or more.
- Labels the conflict against `HAL-REQ-004`. `grep -ci 'conflict' "$TURNS/<n>.md"` → 1 or more; `grep -c 'HAL-REQ-004' "$TURNS/<n>.md"` → 1 or more.
- Matches the open Question. `grep -c 'HAL-Q-003' "$TURNS/<n>.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/<n>.md"` → `0`.
- After turn 2 only: the owner is in the batch. `grep -c 'Margaret Osei' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 3. `H="$WS/projects/hall-bookings"`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- Nothing overwritten: the Requirement in conflict stands as it was. `grep -cxF -- '- **HAL-REQ-004** Members can book up to six months ahead; non-members up to three months ahead. · Source: HAL-SRC-001 · Status: active' "$H/features/HAL-FEA-001-book-and-pay.md"` → `1`; `git -C "$WS" diff "$BASE" HEAD | grep -E '^[-+]- (~~)?\*\*HAL-REQ-004\*\*'` → empty.
- The conflict is a Question citing both Sources. `grep -lE '^Affects: .*HAL-REQ-004' "$H"/questions/HAL-Q-014-*.md | xargs -r grep -l 'HAL-SRC-001' | xargs -r grep -l 'HAL-SRC-006' | wc -l` → `1`; `cat "$H"/questions/HAL-Q-014-*.md | grep -cE '^Status: (open|parked)$'` → `1`; `cat "$H"/questions/HAL-Q-014-*.md | grep -cE '^(Impact|Uncertainty|Score|Score reason): .+'` → `4`; `grep -c 'HAL-Q-014' "$H/questions/index.md"` → 1 or more.
- The Answer, a Decision owned by Margaret. `grep -cE '^- \*\*HAL-ANS-004\*\* .* · Kind: decision · Owner: Margaret Osei · .*Source: HAL-SRC-006 · Status: active$' "$H/questions/HAL-Q-003-committee-cancels.md"` → `1`; `grep -c '^Status: answered$' "$H/questions/HAL-Q-003-committee-cancels.md"` → `1`.
- The Question's wording kept. `head -1 "$H/questions/HAL-Q-003-committee-cancels.md"` → `# HAL-Q-003 · What happens to the hirer's deposit when the hall committee cancels a booking?`
- One Requirement from the Answer. `grep -rhE '^- \*\*HAL-REQ-[0-9]{3}\*\* .* · Source: HAL-ANS-004 · Status: active$' "$H" | wc -l` → `1`.
- The Requirements in `Affects:` left unchanged. Each → `1`: `grep -cxF -- '- **HAL-REQ-005** A hirer who cancels at least 48 hours before the booking starts gets the whole deposit back. · Source: HAL-SRC-001 · Status: active' "$H/features/HAL-FEA-002-cancel-a-booking.md"`, `grep -cxF -- '- **HAL-REQ-007** A hirer who cancels less than 48 hours before the booking starts gets half the deposit back. · Source: HAL-ANS-003 · Status: active' "$H/features/HAL-FEA-002-cancel-a-booking.md"`.
- Own words kept word for word; third-party text never copied, its location kept. `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'non-members can book up to six months ahead, the same as members'` → `1`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'The committee agreed to follow the Code: if we cancel a booking, the hirer gets the whole deposit back within seven days.'` → `1`; `git -C "$WS" diff "$BASE" HEAD | grep -ciE 'every sum paid|paid towards that hire|withdraws a confirmed hire|within its control|original method of payment'` → `0`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '3\.4'` → 1 or more.
- No Feature created. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/hall-bookings/features'` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox` → empty.

## By eye

- The conflict item says plainly that `HAL-REQ-004` stays active until the new open item is answered, and offers the override.
- The Answer says in its own words what the code of practice asks (a full refund within seven days when the venue cancels) and names it by title and section.
- For each of `HAL-REQ-005` and `HAL-REQ-007` the batch says "unchanged".
- The owner was asked for, or Margaret proposed with the reason; never assumed silently.
