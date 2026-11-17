---
id: CP-07
version: 4
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# CP-07 · A Sign-off read-back: ticks and pushback give a Sign-off entry and a Question, and the Decision stays in force

Margaret's Sign-off view of the hall's book-and-pay Epic was published to Confluence. On the page she ticked the cleaning-fee Decision, left the late-finish Decision unticked and wrote why she does not agree, and answered one of her calls (cash deposits). The Operator asks Jenny to capture the page. Jenny proposes one batch: a new Source for the reading, a `HAL-SO-002` entry added to `signoffs.md`, a new Question for the pushback with `Affects: HAL-ANS-004`, flagged as building on a guess because the delivery team already builds to midnight, and an Answer to the cash deposits Question. The late-finish Decision stays active.

## Start

Sample v7, then after install the two overlays below, committed as `Overlay: HAL-EPC-001 pack v2, Margaret's view published`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/signoff/hall-bookings/." "$H/" && cp -r "$F/signoff-readback/hall-bookings/." "$H/" && cat "$F/signoff-readback/log-entries.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 pack v2, Margaret's view published"
```

MCP stand-in: `https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4530112/Book+and+pay+Margaret+Osei+s+calls` → `confluence/signoff-margaret-ticked.md` (page version 2, last updated 2026-11-12 by Margaret Osei).

The key relies on, in `projects/hall-bookings/` after the overlays:

- `epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret.md`: Margaret's view from `pack-v2.md`, with checkboxes on `HAL-ANS-004` (a booking can run until midnight, owner Ravi Kumar, engineer) and `HAL-ANS-005` (no cleaning fee, owner Margaret Osei); `HAL-ANS-001` already agreed; her calls `HAL-Q-004` (cash deposits) and `HAL-Q-013` (meeting room).
- `log/2026-11.md`: the view and its publish, the publish naming the page URL above.
- `epics/HAL-EPC-001-book-and-pay/signoffs.md`: `HAL-SO-001`, Margaret agreed `HAL-ANS-001`.
- `epics/HAL-EPC-001-book-and-pay/epic.md`: handed off (a `Tech face:` line).
- `questions/HAL-Q-009-late-finish.md`: `HAL-ANS-004`, active. `questions/HAL-Q-004-cash-deposits.md`: chasing, `Ask: Margaret Osei`, no Answer.
- Highest IDs `HAL-SRC-006`, `HAL-Q-013`, `HAL-ANS-005`, `HAL-SO-001`, so the new ones are `HAL-SRC-007`, `HAL-Q-014`, `HAL-ANS-006` and `HAL-SO-002`.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Capture Margaret's sign-off page: https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4530112/Book+and+pay+Margaret+Osei+s+calls
2. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- Proposes the Sign-off entry. `grep -c 'HAL-SO-002' "$TURNS/1.md"` → 1 or more.
- Names the tick and the pushback. Each → 1 or more: `grep -c 'HAL-ANS-005' "$TURNS/1.md"`, `grep -c 'HAL-ANS-004' "$TURNS/1.md"`, `grep -c 'HAL-Q-014' "$TURNS/1.md"`.
- Answers her call. `grep -c 'HAL-Q-004' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-ANS-006' "$TURNS/1.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `H="$WS/projects/hall-bookings"`, `E="$H/epics/HAL-EPC-001-book-and-pay"`, `U='https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4530112/Book+and+pay+Margaret+Osei+s+calls'`, `so() { awk '/^## HAL-SO-002 /{f=1; print; next} /^## /{f=0} f' "$E/signoffs.md"; }` (the new entry).

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- `signoffs.md` is only added to. `git -C "$WS" diff "$BASE" HEAD -- 'projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoffs.md' | grep -cE '^-([^-]|$)'` → `0`; `grep -c '^## HAL-SO-001 · Margaret Osei (Stakeholder) · 2026-11-10$' "$E/signoffs.md"` → `1`.
- One new entry, in the record shape. `grep -cE '^## HAL-SO-002 · Margaret Osei \(Stakeholder\) · [0-9]{4}-[0-9]{2}-[0-9]{2}$' "$E/signoffs.md"` → `1`; `grep -c '^## HAL-SO-' "$E/signoffs.md"` → `2`.
- The entry names the pack, the view and the page. `so | grep -cxF "Pack: pack-v2.md · View: signoff-view-v1-margaret.md · Where: $U"` → `1`.
- The tick is agreement; the pushback is not, and points at its Question. `so | grep -cx 'Agreed: HAL-ANS-005'` → `1`; `so | grep -cx 'Not agreed: HAL-ANS-004 → HAL-Q-014'` → `1`; `so | grep -cx 'Source: HAL-SRC-007'` → `1`.
- Only the new ticks: the Decision agreed before is not recorded again. `so | grep -c 'HAL-ANS-001'` → `0`.
- The reading is a new Source. `ls "$H"/sources/HAL-SRC-007-*.md | wc -l` → `1`; each → `1`: `cat "$H"/sources/HAL-SRC-007-*.md | grep -c '^Kind: Confluence page$'`, `cat "$H"/sources/HAL-SRC-007-*.md | grep -cxF "URL: $U"`, `cat "$H"/sources/HAL-SRC-007-*.md | grep -c '^Page version: 2$'`; `cat "$H"/sources/HAL-SRC-007-*.md | grep -ciF 'finish by 11 pm'` → 1 or more; `grep -c 'HAL-SRC-007' "$H/sources/index.md"` → 1 or more.
- The pushback is a Question on the Decision, building on a guess. `ls "$H"/questions/HAL-Q-014-*.md | wc -l` → `1`; each → `1`: `cat "$H"/questions/HAL-Q-014-*.md | grep -cE '^Affects: .*HAL-ANS-004'`, `cat "$H"/questions/HAL-Q-014-*.md | grep -c '^Building on a guess: yes$'`, `cat "$H"/questions/HAL-Q-014-*.md | grep -c '^Raised from: HAL-SRC-007$'`, `cat "$H"/questions/HAL-Q-014-*.md | grep -cE '^Status: open$'`; `grep 'HAL-Q-014' "$H/questions/index.md" | grep -c '^| ! |'` → `1`.
- The Decision stays in force. `git -C "$WS" diff --name-only "$BASE" HEAD -- 'projects/hall-bookings/questions/HAL-Q-009-*'` → empty; `grep -rhE '^- \*\*HAL-ANS-004\*\* .* · Status: active$' "$H/questions" | wc -l` → `1`.
- Her reply to a call is a Decision she owns. `grep -hE '^- \*\*HAL-ANS-006\*\* .* · Kind: decision · Owner: Margaret Osei · Date: [0-9]{4}-[0-9]{2}-[0-9]{2} · Source: HAL-SRC-007 · Status: active$' "$H"/questions/HAL-Q-004-*.md | wc -l` → `1`; `grep -c '^Status: answered$' "$H"/questions/HAL-Q-004-*.md` → `1`.
- The view and the packs stay frozen; the Epic file is untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- 'projects/hall-bookings/epics' | grep -v '/signoffs\.md$'` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox projects/hall-bookings/questions/HAL-Q-013-meeting-room.md` → empty.

## By eye

- Turn 1 names the page as Margaret's view v1 and the Decisions on it: `HAL-ANS-005` ticked, `HAL-ANS-004` pushed back on, and `HAL-ANS-001` agreed already.
- The pushback item says `HAL-ANS-004` stays in force while the new open item is settled, and that the delivery team builds to midnight meanwhile.
- The new open item's wording is Margaret's point (finish by 11 pm, because of the neighbours) as a plain question, not a new Decision.
- The meeting room call (`HAL-Q-013`), which she did not answer, is named as still open, with no deadline set on her.
