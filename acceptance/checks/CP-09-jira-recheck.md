---
id: CP-09
version: 4
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# CP-09 · A re-check of a handed-off Epic proposes only what changed, and engineer pushback leaves the Decision in force

`HALL-12` was checked on 2026-11-12, as CP-06 leaves it: the log names comments 10231, 10235 and 10238 as read. Since then Priya has posted one new comment on `HALL-14`, the same day: a `Business question` pushing back on the deposit Decision `HAL-ANS-001` ($50 minimum, more than a one-hour member booking's fee). The Operator checks again. Jenny proposes only the new comment: a new Source holding it alone, and a Question with `Affects: HAL-ANS-001`, building on a guess. `HAL-ANS-001` stays in force, and no reply goes out, because nothing was answered.

Grader: `acceptance/headless/graders/CP-09.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

Sample v7, then after install the first check's records laid over it from the frozen fixture `acceptance/fixtures/jira/after-check/`, committed as `[2026-11-12] capture | HAL-EPC-001 handed-off Epic check`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/jira/after-check"; cp -r "$F/hall-bookings/." "$H/" && cp -r "$F/outbox" "$WS/" && cat "$F/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-12] capture | HAL-EPC-001 handed-off Epic check"
```

MCP stand-in: `https://example.atlassian.net/browse/HALL-12` → `jira/hall-12-v2.md` (the first check's three comments unchanged, plus comment 10247 on `HALL-14`, created 2026-11-12).

The key relies on, in `projects/hall-bookings/` after the overlay:

- `log/2026-11.md`: `## [2026-11-12] capture | HAL-EPC-001 handed-off Epic check`, with `Read HALL-12, HALL-13, HALL-14; comments 10231, 10235, 10238`.
- `sources/HAL-SRC-006-jira-hall-12-check.md`: the first check's comments 10231 and 10238. `sources/HAL-SRC-007-…`: the Operator's typed note.
- `questions/HAL-Q-014-…` and `questions/HAL-Q-015-…`: both answered (`HAL-ANS-005`, `HAL-ANS-004`).
- `questions/HAL-Q-001-deposit-amount.md`: `HAL-ANS-001`, the deposit is 20% of the hire fee with a minimum of $50, active.
- `project.md`: Priya Shah (engineer) in People.
- `outbox/HALL-13-reply-HAL-ANS-005.md`: the first check's reply, the only outbox file.
- Highest IDs `HAL-SRC-007`, `HAL-Q-015`, `HAL-ANS-005`, so the new ones are `HAL-SRC-008` and `HAL-Q-016`.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Check the book and pay spec.
2. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`.

- Nothing written, nothing new in the outbox. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`; `ls "$WS/outbox" | wc -l` → `1`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- The pushback is a new Question on the Decision. `grep -c 'HAL-Q-016' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-ANS-001' "$TURNS/1.md"` → 1 or more.
- Only what changed: the comments seen at the last check are not proposed again. `grep -ciE 'same day|twice' "$TURNS/1.md"` → `0`; `grep -ci '30 minutes' "$TURNS/1.md"` → `0`.
- No reply: nothing is answered. `grep -ciE 'outbox/|-reply-' "$TURNS/1.md"` → `0`.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `H="$WS/projects/hall-bookings"`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the check's log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| HAL-EPC-001 handed-off Epic check$'` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → 1 or more (2 when the run falls on 2026-11-12).
- The new Source holds the new comment alone. `ls "$H"/sources/HAL-SRC-008-*.md | wc -l` → `1`; `cat "$H"/sources/HAL-SRC-008-*.md | grep -c '^Kind: Jira item$'` → `1`; `cat "$H"/sources/HAL-SRC-008-*.md | grep -cF 'Should the deposit be capped at the hire fee?'` → `1`; `cat "$H"/sources/HAL-SRC-008-*.md | grep -ciE 'same day|30 minutes'` → `0`.
- The earlier check's records are untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- 'projects/hall-bookings/sources/HAL-SRC-006-*' 'projects/hall-bookings/sources/HAL-SRC-007-*' 'projects/hall-bookings/questions/HAL-Q-014-*' 'projects/hall-bookings/questions/HAL-Q-015-*' projects/hall-bookings/project.md` → empty.
- The pushback is one new Question on the Decision, building on a guess. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- projects/hall-bookings/questions | wc -l` → `1`; each → `1`: `cat "$H"/questions/HAL-Q-016-*.md | grep -cE '^Affects: .*HAL-ANS-001'`, `cat "$H"/questions/HAL-Q-016-*.md | grep -c '^Building on a guess: yes$'`, `cat "$H"/questions/HAL-Q-016-*.md | grep -c '^Raised from: HAL-SRC-008$'`, `cat "$H"/questions/HAL-Q-016-*.md | grep -c '^Status: open$'`; `grep 'HAL-Q-016' "$H/questions/index.md" | grep -c '^| ! |'` → `1`.
- The Decision stays in force. `git -C "$WS" diff --name-only "$BASE" HEAD -- 'projects/hall-bookings/questions/HAL-Q-001-*'` → empty; `grep -rhE '^- \*\*HAL-ANS-001\*\* .* · Status: active$' "$H/questions" | wc -l` → `1`.
- No new Answer, Requirement or reply. `git -C "$WS" diff "$BASE" HEAD | grep -cE '^\+- \*\*HAL-(ANS|REQ)-'` → `0`; `git -C "$WS" diff --name-only "$BASE" HEAD -- outbox` → empty.
- This check's log entry names the new comment. `git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/log | grep '^+' | grep -c '10247'` → 1 or more.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics projects/hall-bookings/features projects/court-bookings veneer.md workspace.md` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep '^+' | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.

## By eye

- Turn 1 names the last check (2026-11-12) and says three comments were seen already, without restating them.
- The pushback item says `HAL-ANS-001` stays in force until `HAL-Q-016` is answered, and that the delivery team caps the deposit at the hire fee meanwhile.
- The new Question is Priya's point asked plainly, not a new Decision.
