---
id: CP-05
version: 3
skills: [capture]
cursor-bench: false
repeat-at-gate: false
---

# CP-05 · A re-read of a Confluence page proposes only what changed

The hall hire terms page was captured at version 3 as `HAL-SRC-006`. The committee has since updated it: the guest limit dropped from 120 to 100, a kitchen rule is new, and the part on setting out tables and chairs is gone. The Operator says to re-read it. Jenny finds `HAL-SRC-006` by its URL and proposes only the changes: a new Source naming its previous reading, the limit's Requirement withdrawn and replaced, one new Requirement, and a "withdraw?" item for the Requirement whose text has gone. The Operator says to withdraw that one, then confirms. `HAL-SRC-006` stays exactly as it was.

## Start

Sample v7. MCP stand-in: `https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4521987/Hall+hire+terms` → `confluence/hall-hire-terms-v2.md` (page version 4, last updated 2026-11-12 by Margaret Osei).

After install, lay the first reading over the sample, from the frozen fixture `acceptance/fixtures/confluence/after-v1/` (a first reading as CP-04 makes it, at page version 3, with all four Requirements left in `unplaced.md`): `H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/confluence/after-v1"; cp "$F/HAL-SRC-006-confluence-hall-hire-terms.md" "$H/sources/" && cat "$F/sources-index-row.md" >> "$H/sources/index.md" && cat "$F/unplaced-lines.md" >> "$H/requirements/unplaced.md" && cat "$F/log-entry.md" >> "$H/log/2026-11.md"`, then commit as `[2026-11-11] capture | HAL-SRC-006 Confluence page: Hall hire terms`. The key relies on:

- `projects/hall-bookings/sources/HAL-SRC-006-confluence-hall-hire-terms.md`: the first reading, with the page's URL and `Page version: 3`.
- `projects/hall-bookings/requirements/unplaced.md`: from `HAL-SRC-006`, `HAL-REQ-014` (guests expected) and `HAL-REQ-016` (terms agreed before the deposit), unchanged on the page; `HAL-REQ-015` (at most 120 guests), changed; `HAL-REQ-017` (tables and chairs for $20), gone.
- `projects/hall-bookings/`: highest IDs `HAL-SRC-006`, `HAL-REQ-017`, so the new ones are `HAL-SRC-007`, `HAL-REQ-018` and `HAL-REQ-019`.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Re-read https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4521987/Hall+hire+terms
2. The tables and chairs one has gone from the page, so withdraw it.
3. Yes, write it.

## Key at proposal

Graded after turn 1 (on `$TURNS/1.md`) and again after turn 2 (on `$TURNS/2.md`).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/<n>.md"` → 1 or more.
- Finds the earlier reading. `grep -c 'HAL-SRC-006' "$TURNS/<n>.md"` → 1 or more.
- Proposes the changed limit against `HAL-REQ-015`. `grep -c 'HAL-REQ-015' "$TURNS/<n>.md"` → 1 or more; `grep -c '100' "$TURNS/<n>.md"` → 1 or more.
- Proposes the new kitchen point. `grep -ci 'kitchen' "$TURNS/<n>.md"` → 1 or more.
- Weighs the Requirement whose text has gone. `grep -c 'HAL-REQ-017' "$TURNS/<n>.md"` → 1 or more.
- After turn 1 only: asks rather than withdraws. `grep -ciF 'withdraw?' "$TURNS/1.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/<n>.md"` → `0`.
- (soft) Never says a renamed canonical term (Project, Epic, Question) outside code spans. `sed 's/`[^`]*`//g' "$TURNS/<n>.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## Key at write

Graded after turn 3. `H="$WS/projects/hall-bookings"`, `U='https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4521987/Hall+hire+terms'`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- The first Source is unchanged. `git -C "$WS" diff --name-only "$BASE" HEAD -- 'projects/hall-bookings/sources/HAL-SRC-006-*'` → empty; `ls "$H"/sources/HAL-SRC-006-*.md | wc -l` → `1`.
- The new reading is a new Source naming the previous one. `ls "$H"/sources/HAL-SRC-007-*.md | wc -l` → `1`; each → `1`: `cat "$H"/sources/HAL-SRC-007-*.md | grep -c '^Previous reading: HAL-SRC-006$'`, `cat "$H"/sources/HAL-SRC-007-*.md | grep -c '^Kind: Confluence page$'`, `cat "$H"/sources/HAL-SRC-007-*.md | grep -cxF "URL: $U"`, `cat "$H"/sources/HAL-SRC-007-*.md | grep -c '^Page version: 4$'`, `cat "$H"/sources/HAL-SRC-007-*.md | grep -cE '^Read: [0-9]{4}-[0-9]{2}-[0-9]{2}$'`; `grep -c 'HAL-SRC-007' "$H/sources/index.md"` → 1 or more.
- The new reading keeps the parts used, word for word. Each → `1`: `cat "$H"/sources/HAL-SRC-007-*.md | grep -cF 'the hall holds no more than 100 guests, so a booking for more than 100 cannot be made.'`, `cat "$H"/sources/HAL-SRC-007-*.md | grep -cF 'Hirers say when booking whether they will use the kitchen.'`; `cat "$H"/sources/HAL-SRC-007-*.md | grep -c 'committee@riverbend-hall.example'` → `0`.
- The changed limit: withdrawn and replaced, not rewritten. `grep -rhE '^- ~~\*\*HAL-REQ-015\*\* A booking for more than 120 guests cannot be made\. · Source: HAL-SRC-006 · Status: withdrawn~~ · Withdrawn [0-9]{4}-[0-9]{2}-[0-9]{2} · Reason: .+ · Replaced by: HAL-REQ-018$' "$H" | wc -l` → `1`; `grep -rhE '^- \*\*HAL-REQ-015\*\* ' "$H" | wc -l` → `0`; `grep -rhE '^- \*\*HAL-REQ-018\*\* .* · Source: HAL-SRC-007 · Status: active$' "$H" | grep -c '100'` → `1`.
- The new point is one new Requirement. `grep -rhE '^- \*\*HAL-REQ-019\*\* .* · Source: HAL-SRC-007 · Status: active$' "$H" | grep -ci 'kitchen'` → `1`.
- The gone text's Requirement withdrawn as the Operator said, with no replacement. `grep -rhE '^- ~~\*\*HAL-REQ-017\*\* .* · Status: withdrawn~~ · Withdrawn [0-9]{4}-[0-9]{2}-[0-9]{2} · Reason: .+$' "$H" | grep -vc 'Replaced by'` → `1`; `grep -rhE '^- \*\*HAL-REQ-017\*\* ' "$H" | wc -l` → `0`.
- Only the changes: the unchanged parts' Requirements are untouched, and only two Requirements are added. `git -C "$WS" diff "$BASE" HEAD | grep -E '^[-+]- (~~)?\*\*HAL-REQ-01[46]\*\*'` → empty; `git -C "$WS" diff "$BASE" HEAD | grep -cE '^\+- \*\*HAL-REQ-'` → `2`; `git -C "$WS" diff "$BASE" HEAD | grep -E '^[-+]- (~~)?\*\*HAL-REQ-001\*\*'` → empty.
- No Feature created. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/hall-bookings/features'` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox` → empty.
- (soft) Reply after writing never says a renamed canonical term. `sed 's/`[^`]*`//g' "$TURNS/3.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## By eye

- The batch names the page versions read (3, then 4) and lists the unchanged parts in one line, proposing nothing for them.
- The limit is proposed as "withdraw `HAL-REQ-015` and replace it with …", with the new wording in full.
- Turn 1 shows `HAL-REQ-017` as a "withdraw?" item that stays active unless the Operator says to withdraw it; after turn 2 it is a withdrawal, and the batch is shown again in full.
