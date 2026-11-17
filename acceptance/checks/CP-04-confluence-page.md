---
id: CP-04
version: 6
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# CP-04 · A Confluence page read through the MCP, kept as the parts used

The Operator gives Jenny the URL of the hall committee's Confluence page of hire terms and says to capture it. Jenny reads it through the Atlassian MCP and proposes a batch as for any Capture: one point says again what an active Requirement says, four are new. On confirm, the Source holds the parts used word for word, with the page's URL, its version and the date read; the page's contact line stays out.

## Start

Sample v7 as it is. MCP stand-in: `https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4521987/Hall+hire+terms` → `confluence/hall-hire-terms-v1.md` (page version 3, last updated 2026-11-05 by Margaret Osei, own organisation: the deposit rule again; guests expected; at most 120 guests; terms agreed before the deposit; tables and chairs set out for $20; a contact line). The key relies on:

- `projects/hall-bookings/features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-001` (confirmed only once the deposit is paid), the duplicate.
- `projects/hall-bookings/`: highest IDs `HAL-SRC-005`, `HAL-REQ-013`, so the new ones are `HAL-SRC-006` and `HAL-REQ-014` to `HAL-REQ-017`. Nothing active there covers guest numbers, agreeing to terms or setting out tables.
- `projects/hall-bookings/project.md`: Margaret Osei is a Stakeholder.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Capture this Confluence page please: https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4521987/Hall+hire+terms
2. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- Read the page: its points are in the batch. Each → 1 or more: `grep -c '120' "$TURNS/1.md"`, `grep -cF '$20' "$TURNS/1.md"`, `grep -ci 'guests' "$TURNS/1.md"`.
- Labels the duplicate against `HAL-REQ-001`. `grep -ciw 'duplicate' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-REQ-001' "$TURNS/1.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `H="$WS/projects/hall-bookings"`, `U='https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4521987/Hall+hire+terms'`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- One Source, a Confluence page from Margaret with the URL, page version and date read. `ls "$H"/sources/HAL-SRC-006-*.md | wc -l` → `1`; each → `1`: `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Kind: Confluence page$'`, `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Owner: Margaret Osei$'`, `cat "$H"/sources/HAL-SRC-006-*.md | grep -cxF "URL: $U"`, `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Page version: 3$'`, `cat "$H"/sources/HAL-SRC-006-*.md | grep -cE '^Read: [0-9]{4}-[0-9]{2}-[0-9]{2}$'`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Previous reading:'` → `0`; `grep -c 'HAL-SRC-006' "$H/sources/index.md"` → 1 or more.
- The parts used, word for word; the parts not used left out. Each → `1`: `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'The hall holds no more than 120 guests, so a booking for more than 120 cannot be made.'`, `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'the caretaker sets out the tables and chairs before the booking starts, for a $20 fee.'`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c 'committee@riverbend-hall.example'` → `0`.
- Four new Requirements, each citing the page. `grep -rhE '^- \*\*HAL-REQ-01[4-7]\*\* .* · Source: HAL-SRC-006 · Status: active$' "$H" | wc -l` → `4`; `grep -rhE '^- \*\*HAL-REQ-01[4-7]\*\* ' "$H" | grep -c '120'` → `1`; `grep -rhE '^- \*\*HAL-REQ-01[4-7]\*\* ' "$H" | grep -cF '$20'` → `1`; the fee sits on the set-out Requirement, not one of its own: `grep -rhE '^- \*\*HAL-REQ-01[4-7]\*\* ' "$H" | grep -F '$20' | grep -ci 'tables'` → `1`; `grep -rc 'HAL-REQ-018' "$H" | grep -vc ':0$'` → `0`.
- The duplicate is left alone, as a log note. `grep -cxF -- '- **HAL-REQ-001** A booking is confirmed only once its deposit has been paid. · Source: HAL-SRC-001 · Status: active' "$H/features/HAL-FEA-001-book-and-pay.md"` → `1`; `git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/log | grep '^+' | grep 'HAL-REQ-001' | grep -ci 'duplicate'` → 1 or more.
- No Feature created. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/hall-bookings/features'` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox` → empty.

## By eye

- The batch says the page was read through the MCP and names its version, and item 1 is the Source.
- The heading and the contact line are listed in one line as parts not used.
