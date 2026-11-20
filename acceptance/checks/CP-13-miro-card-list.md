---
id: CP-13
version: 1
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# CP-13 · A Miro CSV export is slotted into the paste template before any batch

The Operator drops in a Miro CSV export of the hall's story map wall instead of the paste template. Jenny says Miro keeps no order, shows the cards (the two tagged `enabler` as `[enabler]`) and asks where each goes, proposing nothing. The Operator places every card but the photo gallery: Jenny still proposes nothing and asks about it. Once the Operator sets it aside, she shows the filled template and the batch; on the yes she writes the same map CP-10 writes, with no photo gallery, in one commit.

## Start

Sample v7 as it is. Fixture: `acceptance/fixtures/storymap/miro-cards.csv` (a Miro CSV export, `Text,Description,Tags`, rows in no useful order: the activity and step stickies, the cards of CP-10's session with user groups as tags, "Card payment account with the bank" and "Email sending service" tagged `enabler`, the latter with the description "3 days", and "Photo gallery of the hall" with no tag). The key relies on:

- `projects/hall-bookings/`: highest IDs `HAL-SRC-005`, `HAL-REQ-013`, `HAL-Q-013`, no `MIL` IDs, and no `storymap.md`; so the new ones are `HAL-SRC-006`, `HAL-REQ-014` on, `HAL-MIL-001`, `HAL-MIL-002`, and `HAL-Q-014` on.
- `features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-001` (confirmed only once the deposit is paid). `features/HAL-FEA-002-cancel-a-booking.md`: `HAL-REQ-005` (whole deposit back with 48 hours' notice). `requirements/unplaced.md`: `HAL-REQ-011` (the caretaker is emailed the next day's bookings at 6 pm).
- `project.md`: Margaret Osei (Stakeholder) in People.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Here's the Miro export from today's story mapping session for the hall, 2026-11-16, with Margaret Osei, Ravi Kumar and Dana Wells. Hirers book and pay for the main hall online, so the committee stops taking bookings by phone. <paste: storymap/miro-cards.csv>
2. The activities are Book the hall, then Manage a booking. Book the hall has the steps Find a free date, then Book and pay; Manage a booking has Cancel, then Caretaker's list. The release lines, top first, are Walking skeleton (hirers), with nothing else known yet, then First online bookings: outcome hirers book and pay online instead of phoning the committee, metric half of all bookings made online in the first month, target 2027-03-01 set by Margaret Osei. Find a free date: seeing free dates in the Walking skeleton, choosing start and finish times in First online bookings. Book and pay: booking and paying the deposit by card, then the card payment account, in the Walking skeleton; confirmed only once the deposit is paid in First online bookings. Cancel: the 48 hours' notice card, First online bookings. Caretaker's list: the 6 pm email, then the email sending service, First online bookings. Within each band, the order is as I've said it.
3. Set the photo gallery aside.
4. Yes, write it.

## Key at proposal

Graded after turns 1, 2 and 3 (on `$TURNS/1.md`, `$TURNS/2.md` and `$TURNS/3.md`).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/<n>.md"` → `0`.
- Turn 1 says the order is not kept, keeps the enabler tags, and asks. `grep -ciE "(not|no|n't)[a-z' ]{0,20}(keep|kept)[a-z' ]{0,30}order|order[a-z' ]{0,20}(not|n't|isn't) (kept|keep)|unordered" "$TURNS/1.md"` → 1 or more; `grep -c '\[enabler\]' "$TURNS/1.md"` → 1 or more; `grep -c '?' "$TURNS/1.md"` → 1 or more.
- Turns 1 and 2 propose no batch. Each → `0`: `grep -c 'Capture: ' "$TURNS/1.md"`, `grep -c 'HAL-MIL-' "$TURNS/1.md"`, `grep -cE 'HAL-REQ-0(1[4-9]|2[0-9])' "$TURNS/1.md"`, `grep -c 'Capture: ' "$TURNS/2.md"`, `grep -c 'HAL-MIL-' "$TURNS/2.md"`, `grep -cE 'HAL-REQ-0(1[4-9]|2[0-9])' "$TURNS/2.md"`.
- Turn 2 asks about the card with no place. `grep -ci 'gallery' "$TURNS/2.md"` → 1 or more; `grep -c '?' "$TURNS/2.md"` → 1 or more.
- Turn 3 shows the filled template with its enablers, and the batch. `grep -c '\[enabler\]' "$TURNS/3.md"` → 1 or more; `grep -c 'Nothing is written yet' "$TURNS/3.md"` → 1 or more; `grep -c 'HAL-MIL-001' "$TURNS/3.md"` → 1 or more; `grep -c 'HAL-MIL-002' "$TURNS/3.md"` → 1 or more.
- Turn 3 places the repeated cards by their existing IDs. Each → 1 or more: `grep -c 'HAL-REQ-001' "$TURNS/3.md"`, `grep -c 'HAL-REQ-005' "$TURNS/3.md"`, `grep -c 'HAL-REQ-011' "$TURNS/3.md"`.

## Key at write

Graded after turn 4. `H="$WS/projects/hall-bookings"`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- The Source keeps the filled template, with the enabler tag, and the list as given. `ls "$H"/sources/HAL-SRC-006-*.md | wc -l` → `1`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Kind: story map session$'` → `1`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'Card payment account with the bank [enabler]'` → 1 or more; `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'Text,Description,Tags'` → 1 or more.
- New cards become Requirements citing the session. `grep -rhE '^- \*\*HAL-REQ-0(1[4-9]|2[0-9])\*\* .* · Source: HAL-SRC-006 · Status: active$' "$H" | wc -l` → 3 or more.
- No duplicates, no enabler Requirements, and nothing for the set-aside card. `git -C "$WS" diff "$BASE" HEAD | grep -E '^\+- \*\*HAL-REQ-' | grep -ciE 'only once|48 hours|6 pm|payment account|email sending|gallery'` → `0`.
- The map: backbone headings, sections, and the repeated cards by their existing IDs. Each → `1`: `grep -cx '## Book the hall' "$H/storymap.md"`, `grep -cx '## Manage a booking' "$H/storymap.md"`, `grep -cx '### Find a free date' "$H/storymap.md"`, `grep -cx '## Enablers' "$H/storymap.md"`, `grep -cx '## Not on the map' "$H/storymap.md"`, `grep -c 'HAL-REQ-001 (' "$H/storymap.md"`, `grep -c 'HAL-REQ-005 (' "$H/storymap.md"`, `grep -c 'HAL-REQ-011 (' "$H/storymap.md"`.
- Card lines grouped by Milestone, one per Milestone in each step. `grep -cE '^- HAL-MIL-00[12]: HAL-REQ-' "$H/storymap.md"` → `6`.
- Both enablers held on the map, and nothing off it: the set-aside card is not there. `sed -n '/^## Enablers$/,/^## Not on the map$/p' "$H/storymap.md" | grep -c '^- \*\*'` → `2`; `sed -n '/^## Not on the map$/,$p' "$H/storymap.md" | grep -c '^- '` → `0`.
- One new Question, the Walking skeleton's missing parts. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- projects/hall-bookings/questions | wc -l` → `1`; `grep -lE '^Affects: .*HAL-MIL-00[12]' "$H"/questions/*.md | wc -l` → `1`.
- The map is linked from the Project index. `grep -c 'storymap.md' "$H/index.md"` → 1 or more.
- Two Milestone records: one internal, one with Margaret's target. `ls "$H"/milestones/ | wc -l` → `2`; `ls "$H"/milestones/HAL-MIL-00[12]-*.md | wc -l` → `2`; `grep -l '^Internal: yes$' "$H"/milestones/*.md | wc -l` → `1`; `grep -hx 'Target: 2027-03-01 set by Margaret Osei' "$H"/milestones/*.md | wc -l` → `1`.
- The card's description, an estimate, stays out of every record but the Source and the log. `git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings ':!projects/hall-bookings/sources' ':!projects/hall-bookings/log' | grep '^+' | grep -ci '3 days'` → `0`.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep '^+' | grep -v '^+>' | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics projects/court-bookings veneer.md workspace.md outbox` → empty.

## By eye

- Turn 1 says plainly that Miro keeps no order, lists every card (activities and steps among them) under `Not placed yet:`, and asks one numbered list of questions; any step it suggests is in a question, not in the template.
- Turn 2 shows the template with every card but the photo gallery placed, and asks only about the gallery.
- Turn 3 lists the photo gallery as not used.
