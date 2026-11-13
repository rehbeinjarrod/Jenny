---
id: CP-02
version: 7
skills: [capture]
cursor-bench: false
repeat-at-gate: false
---

# CP-02 · A pasted email: one duplicate, one refines, kept word for word

The Operator pastes an email from the hall committee chair. One point says again what an active Requirement already says; the other narrows the door-code Requirement. Jenny labels them duplicate and refines. On confirm, the duplicate writes only a log note, the refined Requirement is withdrawn and replaced under a new ID, and the email is kept word for word.

## Start

Sample v7 as it is. Fixture: `acceptance/fixtures/capture/pasted-email.md` (Margaret Osei, own organisation: the deposit-before-confirmation rule again, and the door code made the side door's code for the booking's month). The key relies on:

- `projects/hall-bookings/features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-001` (confirmed only once the deposit is paid), the duplicate.
- `projects/hall-bookings/requirements/unplaced.md`: `HAL-REQ-008` (the confirmation email gives the door code), the one refined.
- `projects/hall-bookings/`: highest IDs `HAL-SRC-005`, `HAL-REQ-013`, so the new ones are `HAL-SRC-006` and `HAL-REQ-014`.
- `projects/hall-bookings/questions/HAL-Q-012-door-code-by-text.md`: chasing, `Affects: HAL-REQ-008`, so the refinement brings a proposed re-score or "score unchanged" for it.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Margaret sent this, capture it please: <paste: capture/pasted-email.md>
2. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- Labels the duplicate against `HAL-REQ-001`. `grep -ciw 'duplicate' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-REQ-001' "$TURNS/1.md"` → 1 or more.
- Labels the refinement against `HAL-REQ-008`. `grep -ciw 'refines' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-REQ-008' "$TURNS/1.md"` → 1 or more.
- Weighs the chasing Question that affects `HAL-REQ-008`. `grep -c 'HAL-Q-012' "$TURNS/1.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.
- (soft) Never says a renamed canonical term (Project, Epic, Question) outside code spans. `sed 's/`[^`]*`//g' "$TURNS/1.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## Key at write

Graded after turn 2. `H="$WS/projects/hall-bookings"`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- The email kept word for word, as a pasted email from Margaret. `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'The side door code changes on the first of every month'` → `1`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Kind: pasted email$'` → `1`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Owner: Margaret Osei$'` → `1`.
- The duplicate is left alone. `grep -cxF -- '- **HAL-REQ-001** A booking is confirmed only once its deposit has been paid. · Source: HAL-SRC-001 · Status: active' "$H/features/HAL-FEA-001-book-and-pay.md"` → `1`; `git -C "$WS" diff "$BASE" HEAD | grep -E '^\+- \*\*HAL-REQ-' | grep -ci 'deposit'` → `0`.
- The duplicate is a log note. `git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/log | grep '^+' | grep 'HAL-REQ-001' | grep -ci 'duplicate'` → 1 or more.
- The refined Requirement withdrawn, struck through, and replaced. `grep -rhE '^- ~~\*\*HAL-REQ-008\*\* .*~~ · Withdrawn [0-9]{4}-[0-9]{2}-[0-9]{2} · Reason: .+ · Replaced by: HAL-REQ-014' "$H" | wc -l` → `1`; `grep -rhE '^- \*\*HAL-REQ-008\*\* ' "$H" | wc -l` → `0`.
- The replacement cites the email. `grep -rhE '^- \*\*HAL-REQ-014\*\* .* · Source: HAL-SRC-006 · Status: active$' "$H" | wc -l` → `1`; `grep -rhE '^- \*\*HAL-REQ-014\*\* ' "$H" | grep -ci 'side door'` → `1`.
- The side-door code is one Requirement: the replacement holds the month, and nothing else is added. `grep -rhE '^- \*\*HAL-REQ-014\*\* ' "$H" | grep -ci 'month'` → `1`; `grep -rc 'HAL-REQ-015' "$H" | grep -vc ':0$'` → `0`.
- No Feature created. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/hall-bookings/features'` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox` → empty.
- (soft) Reply after writing never says a renamed canonical term. `sed 's/`[^`]*`//g' "$TURNS/2.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## By eye

- The refinement is proposed as "withdraw `HAL-REQ-008` and replace it with …", with the new wording in full: the side door's code for the booking's month, in one statement.
- The greeting and sign-off may be left out of the Source as parts not used; every sentence kept is exact.
