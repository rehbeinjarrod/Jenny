---
id: CP-10
version: 3
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# CP-10 · A story map session pasted into the template becomes the map, its Milestones and Questions in one commit

The Operator has run a story mapping session for the hall and asks for the paste template. Jenny shows it and writes nothing. The Operator pastes the filled template back: two activities, four steps, two release lines (a Walking skeleton for hirers and First online bookings), two enabler cards, and engineers' notes holding a risk and an idea. Three cards say again what active Requirements say. Jenny proposes one batch; on the yes she writes the Source, the new Requirements, `storymap.md` placing every card by an ID, two Milestone records and three Questions, in one commit.

## Start

Sample v7 as it is. Fixture: `acceptance/fixtures/storymap/session-template.md` (the filled paste template: cards for free dates, start and finish times and booking with a card deposit, which are new; the deposit-before-confirmation rule, the 48-hour cancellation refund and the caretaker's 6 pm list, which are duplicates; enablers "Card payment account with the bank" and "Email sending service (3 days)"; release lines Walking skeleton (hirers), with no outcome, metric or target, and First online bookings, target 2027-03-01 set by Margaret Osei). The key relies on:

- `projects/hall-bookings/`: highest IDs `HAL-SRC-005`, `HAL-REQ-013`, `HAL-Q-013`, no `MIL` IDs, and no `storymap.md`; so the new ones are `HAL-SRC-006`, `HAL-REQ-014` on, `HAL-MIL-001`, `HAL-MIL-002`, and `HAL-Q-014` on.
- `features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-001` (confirmed only once the deposit is paid). `features/HAL-FEA-002-cancel-a-booking.md`: `HAL-REQ-005` (whole deposit back with 48 hours' notice). `requirements/unplaced.md`: `HAL-REQ-011` (the caretaker is emailed the next day's bookings at 6 pm).
- `project.md`: Margaret Osei (Stakeholder) in People.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. I've just run a story mapping session for the hall bookings. Give me the paste template.
2. Here it is, filled in: <paste: storymap/session-template.md>
3. Yes, write it.

## Key at proposal

Graded after turn 1 (on `$TURNS/1.md`) and turn 2 (on `$TURNS/2.md`).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/<n>.md"` → `0`.
- The template shows release lines and the enabler tag. `grep -c -- '--- ' "$TURNS/1.md"` → 1 or more; `grep -c '\[enabler\]' "$TURNS/1.md"` → 1 or more.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/2.md"` → 1 or more.
- Places the repeated cards by their existing IDs. Each → 1 or more: `grep -c 'HAL-REQ-001' "$TURNS/2.md"`, `grep -c 'HAL-REQ-005' "$TURNS/2.md"`, `grep -c 'HAL-REQ-011' "$TURNS/2.md"`.
- Proposes both Milestones. `grep -c 'HAL-MIL-001' "$TURNS/2.md"` → 1 or more; `grep -c 'HAL-MIL-002' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 3. `H="$WS/projects/hall-bookings"`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- The session is a frozen Source, word for word. `ls "$H"/sources/HAL-SRC-006-*.md | wc -l` → `1`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Kind: story map session$'` → `1`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'Card payment account with the bank [enabler]'` → `1`; `grep -c 'HAL-SRC-006' "$H/sources/index.md"` → 1 or more.
- New cards become Requirements citing the session. `grep -rhE '^- \*\*HAL-REQ-0(1[4-9]|2[0-9])\*\* .* · Source: HAL-SRC-006 · Status: active$' "$H" | wc -l` → 3 or more.
- No duplicates and no enabler Requirements. `git -C "$WS" diff "$BASE" HEAD | grep -E '^\+- \*\*HAL-REQ-' | grep -ciE 'only once|48 hours|6 pm|payment account|email sending'` → `0`.
- The map: backbone headings, sections, and the repeated cards by their existing IDs. Each → `1`: `grep -cx '## Book the hall' "$H/storymap.md"`, `grep -cx '## Manage a booking' "$H/storymap.md"`, `grep -cx '### Find a free date' "$H/storymap.md"`, `grep -cx '## Enablers' "$H/storymap.md"`, `grep -cx '## Not on the map' "$H/storymap.md"`, `grep -c 'HAL-REQ-001 (' "$H/storymap.md"`, `grep -c 'HAL-REQ-005 (' "$H/storymap.md"`, `grep -c 'HAL-REQ-011 (' "$H/storymap.md"`.
- Card lines grouped by Milestone, one per Milestone in each step. `grep -cE '^- HAL-MIL-00[12]: HAL-REQ-' "$H/storymap.md"` → `6`.
- Both enablers held on the map with no ID, and nothing yet off the map. `sed -n '/^## Enablers$/,/^## Not on the map$/p' "$H/storymap.md" | grep -c '^- \*\*'` → `2`; `sed -n '/^## Not on the map$/,$p' "$H/storymap.md" | grep -c '^- '` → `0`.
- Two Milestone records: one internal, one with Margaret's target, neither sliced. `ls "$H"/milestones/ | wc -l` → `2`; `ls "$H"/milestones/HAL-MIL-00[12]-*.md | wc -l` → `2`; `grep -l '^Internal: yes$' "$H"/milestones/*.md | wc -l` → `1`; `grep -hx 'Target: 2027-03-01 set by Margaret Osei' "$H"/milestones/*.md | wc -l` → `1`; `grep -lx 'Not sliced yet.' "$H"/milestones/*.md | wc -l` → `2`.
- Three new Questions: the Walking skeleton's missing parts, the risk and the idea. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- projects/hall-bookings/questions | wc -l` → `3`; `grep -lE '^Affects: .*HAL-MIL-00[12]' "$H"/questions/*.md | wc -l` → `1`; `cat "$H"/questions/HAL-Q-01[4-9]-*.md | grep -ciE 'bank|card payment'` → 1 or more; `cat "$H"/questions/HAL-Q-01[4-9]-*.md | grep -ci 'council'` → 1 or more.
- The card estimate is dropped from every record but the Source and the log. `git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings ':!projects/hall-bookings/sources' ':!projects/hall-bookings/log' | grep '^+' | grep -ci '3 days'` → `0`.
- The map is linked from the Project index. `grep -c 'storymap.md' "$H/index.md"` → 1 or more.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep '^+' | grep -v '^+>' | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics projects/court-bookings veneer.md workspace.md outbox` → empty.

## By eye

- Turn 1 is the template in a code block with a few plain lines on how to fill it in, and nothing else proposed.
- The duplicates say they are placed on the map by their existing IDs and write no new Requirement.
- Each enabler has a proposed kind, `Enables:` the Requirements of the business cards in its step from its band down, and `Depends on: none`: the card payment account a Technical Enabler for `HAL-REQ-016` and `HAL-REQ-001`, the email sending service an Enabler Story for `HAL-REQ-011`.
- The estimate "(3 days)" is named as not used.
