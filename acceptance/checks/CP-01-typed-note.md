---
id: CP-01
version: 7
skills: [capture]
cursor-bench: false
repeat-at-gate: false
---

# CP-01 · A typed note, amended by number, nothing written before confirm

The Operator pastes a note they typed and says to capture it. Jenny names the hall Project and why, then proposes a numbered batch: the Source kept word for word, two Requirements split from one two-need sentence, and a scored Question. The Operator rewords item 2 by number; the batch changes. Nothing is written until the yes, then it is one commit.

## Start

Sample v7 as it is. Fixture: `acceptance/fixtures/capture/typed-note.md` (the Operator's own note: one sentence holding two needs for the confirmation email, a calendar link and a map; and one unknown, whether hirers may bring their own drinks). The key relies on:

- `projects/hall-bookings/`: highest IDs `HAL-SRC-005`, `HAL-REQ-013`, `HAL-Q-013`, so the new ones are `HAL-SRC-006`, `HAL-REQ-014`, `HAL-REQ-015`, `HAL-Q-014`. Nothing active there covers a calendar link, a map or drinks.
- `projects/court-bookings/`: untouched.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Capture this: <paste: capture/typed-note.md>
2. Reword 2 as: The confirmation email has a button that adds the booking to the hirer's calendar.
3. Yes, write it.

## Key at proposal

Graded after turn 1 (on `$TURNS/1.md`) and again after turn 2 (on `$TURNS/2.md`).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/<n>.md"` → 1 or more.
- Names the hall Project. `grep -ci 'hall' "$TURNS/<n>.md"` → 1 or more; `grep -c 'CRT-' "$TURNS/<n>.md"` → `0`.
- Proposes both needs and the unknown. Each → 1 or more: `grep -ci 'calendar' "$TURNS/<n>.md"`, `grep -ciw 'map' "$TURNS/<n>.md"`, `grep -ciwE 'drinks?' "$TURNS/<n>.md"`.
- Proposes scores for the new Question. `grep -ci 'impact' "$TURNS/<n>.md"` → 1 or more; `grep -ci 'uncertainty' "$TURNS/<n>.md"` → 1 or more.
- (soft) Never says a renamed canonical term (Project, Epic, Question) outside code spans. `sed 's/`[^`]*`//g' "$TURNS/<n>.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.
- After turn 1 only: not yet reworded. `grep -c 'button that adds the booking' "$TURNS/1.md"` → `0`.
- After turn 2 only: the amend took. `grep -c 'button that adds the booking' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 3. `H="$WS/projects/hall-bookings"`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- Only capture's files changed, and no Feature created. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(index\.md|sources/(index|HAL-SRC-006-[a-z0-9-]+)\.md|requirements/unplaced\.md|features/(index|HAL-FEA-00[12]-[a-z0-9-]+)\.md|questions/(index|HAL-Q-014-[a-z0-9-]+)\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty; `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/hall-bookings/features'` → empty.
- The Source, word for word, as a typed note. `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'add the booking to their calendar and show a map to the hall'` → `1`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Kind: typed note$'` → `1`; `grep -c 'HAL-SRC-006' "$H/sources/index.md"` → 1 or more.
- Two Requirements from the one sentence, each citing the Source. `grep -rhE '^- \*\*HAL-REQ-01(4|5)\*\* .* · Source: HAL-SRC-006 · Status: active$' "$H" | wc -l` → `2`.
- The amended wording is the one written. `grep -rhE '^- \*\*HAL-REQ-01(4|5)\*\* ' "$H" | grep -c 'button that adds the booking'` → `1`; `grep -rhE '^- \*\*HAL-REQ-01(4|5)\*\* ' "$H" | grep -ciw 'map'` → `1`.
- The new Question, scored. `ls "$H"/questions/HAL-Q-014-*.md | wc -l` → `1`; `cat "$H"/questions/HAL-Q-014-*.md | grep -cE '^(Impact|Uncertainty|Score|Score reason): .+'` → `4`; `f=$(ls "$H"/questions/HAL-Q-014-*.md); i=$(sed -n 's/^Impact: //p' "$f"); u=$(sed -n 's/^Uncertainty: //p' "$f"); s=$(sed -n 's/^Score: //p' "$f"); [ "$((i*u))" = "$s" ] && echo ok` → `ok`; `cat "$H"/questions/HAL-Q-014-*.md | grep -cE '^Status: (open|parked)$'` → `1`; `cat "$H"/questions/HAL-Q-014-*.md | grep -c '^Raised from: HAL-SRC-006$'` → `1`; `grep -c 'HAL-Q-014' "$H/questions/index.md"` → 1 or more.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox` → empty.
- (soft) Reply after writing never says a renamed canonical term. `sed 's/`[^`]*`//g' "$TURNS/3.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## By eye

- The Project guess comes with a reason (the hall, Ravi) and sits above the numbered items.
- Item 1 is the Source; the items follow the order of the note.
- The batch is shown again in full after the amend, under the same heading.
- The Question's score reason is one plain line; a Score of 1 or 2 is proposed as parked.
