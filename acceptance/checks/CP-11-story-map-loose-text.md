---
id: CP-11
version: 2
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# CP-11 · Loose notes from a story mapping session get questions about the gaps before any batch

The Operator pastes rough notes from a story mapping session, not in the paste template's shape: activities and cards in prose, one release and its target date, an enabler, and two cards with no release line. Jenny asks about the gaps (which release each card falls in, at least) and proposes nothing. Once the Operator answers, she proposes the batch, with the Milestones and Margaret's target, and still writes nothing.

## Start

Sample v7 as it is. Fixture: `acceptance/fixtures/storymap/session-loose.md` (the Operator's notes: booking cards and managing cards, Margaret wanting hirers booking and paying online by 1 March 2027, Ravi's card payment account needed first, and a text reminder and a photo gallery with no release line). The key relies on:

- `projects/hall-bookings/`: no `storymap.md` and no `MIL` IDs, so the first Milestone is `HAL-MIL-001`.
- `project.md`: Margaret Osei (Stakeholder) in People.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Here are my notes from today's story mapping session for the hall, capture them: <paste: storymap/session-loose.md>
2. Free date, start and finish times, paying the deposit by card and the bank account are in the first release, called First online bookings. Cancelling, Alan's list and the text reminder go in a second release called Later, with no date yet. Leave out the photo gallery. The order is as I wrote it, and every card is for hirers except Alan's list, which is for the caretaker.

## Key at proposal

Graded after turn 1 (on `$TURNS/1.md`) and turn 2 (on `$TURNS/2.md`).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/<n>.md"` → `0`.
- Turn 1 asks about the gaps and proposes no batch yet. `grep -ciE 'release' "$TURNS/1.md"` → 1 or more; `grep -ciE 'reminder|gallery' "$TURNS/1.md"` → 1 or more; `grep -c '?' "$TURNS/1.md"` → 1 or more; `grep -c 'Capture: ' "$TURNS/1.md"` → `0`; `grep -c 'HAL-MIL-' "$TURNS/1.md"` → `0`; `grep -cE 'HAL-REQ-0(1[4-9]|2[0-9])' "$TURNS/1.md"` → `0`.
- Turn 2 proposes the batch with its Milestones and Margaret's target. `grep -c 'Nothing is written yet' "$TURNS/2.md"` → 1 or more; `grep -c 'HAL-MIL-001' "$TURNS/2.md"` → 1 or more; `grep -c 'HAL-MIL-002' "$TURNS/2.md"` → 1 or more; `grep -c '2027-03-01' "$TURNS/2.md"` → 1 or more; `grep -ci 'enabler' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 2.

- No commit, no file changes. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- Turn 1 is one numbered list of gaps, each naming the cards it is about, with no records proposed.
- The card payment account is held as an enabler, not proposed as a Requirement.
- The photo gallery is listed as not used, and the parked `HAL-Q-005` (photo gallery) may be mentioned.
