---
id: SL-04
version: 2
skills: [slice]
cursor-bench: false
routing: false
inputs: [acceptance/headless/graders/SL-03/milestones.py]
promise: false
---

# SL-04 · Slicing a mapped Project warns about Requirements not on the map, and goes ahead

The hall Project has a story map, and a text-reminder Requirement captured since then sits under `## Not on the map`. The Operator asks Jenny to slice the Project. Jenny's proposal names the Requirements the map does not hold, the text reminder among them, with a warning that no Milestone counts them, and slices all the same. After confirm, the Requirements on the map are in Features within their Milestones, each Milestone's members list its Features, the map is unchanged but for its enablers, which become Technical Enablers and Enabler Stories, and everything lands in one commit.

## Start

Sample v7, then after install the mapped state laid over it from the frozen fixture `acceptance/fixtures/storymap/mapped/` (CP-10's result), committed as `[2026-11-16] capture | HAL-SRC-006 Story map session of 2026-11-16`, then the text reminder from the frozen fixture `acceptance/fixtures/storymap/off-map/` (CP-12's result), committed as `[2026-11-17] capture | HAL-SRC-007 Operator's note of Margaret on a text reminder`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/storymap"; cp -r "$F/mapped/hall-bookings/." "$H/" && cat "$F/mapped/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-16] capture | HAL-SRC-006 Story map session of 2026-11-16" && cp -r "$F/off-map/hall-bookings/." "$H/" && cat "$F/off-map/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-17] capture | HAL-SRC-007 Operator's note of Margaret on a text reminder"
```

The key relies on, in `projects/hall-bookings/` after the overlays:

- `storymap.md`: `HAL-REQ-014` and `HAL-REQ-016` in `HAL-MIL-001` (Walking skeleton (hirers), internal); `HAL-REQ-001`, `HAL-REQ-005`, `HAL-REQ-011` (the caretaker's 6 pm list) and `HAL-REQ-015` in `HAL-MIL-002` (First online bookings). `## Not on the map` lists `HAL-REQ-017` (a text reminder the day before a booking).
- `requirements/unplaced.md`: `HAL-REQ-008` to `HAL-REQ-017`. Of these, `HAL-REQ-008`, `HAL-REQ-009`, `HAL-REQ-010`, `HAL-REQ-012`, `HAL-REQ-013` and `HAL-REQ-017` are not on the map.
- `milestones/`: `HAL-MIL-001` and `HAL-MIL-002`, each with `## Members` reading `Not sliced yet.`
- `features/HAL-FEA-001-book-and-pay.md` (holds `HAL-REQ-001`; its Epic is handed off) and `features/HAL-FEA-002-cancel-a-booking.md` (holds `HAL-REQ-005`; no Epic yet).
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Slice the hall bookings initiative.
2. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more.
- Warns about the Requirement under Not on the map. `grep -c 'HAL-REQ-017' "$TURNS/1.md"` → 1 or more; `grep -ci 'not on the map' "$TURNS/1.md"` → 1 or more.
- No leak-trap items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `P="$WS/projects/hall-bookings"`.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] slice \| '` → `1`; `grep -cxF "## $(git -C "$WS" log -1 --format=%s)" "$P"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only slicing files changed, Milestones included. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(features/[^/]+\.md|epics/[^/]+/epic\.md|milestones/HAL-MIL-[0-9]{3}-[^/]+\.md|storymap\.md|requirements/unplaced\.md|index\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- The slice went ahead: the caretaker's list is in a Feature. `grep -l '^- \*\*HAL-REQ-011\*\*' "$P"/features/HAL-FEA-*.md | wc -l` → `1`; `grep -c 'HAL-REQ-011' "$P/requirements/unplaced.md"` → `0`.
- The map is unchanged outside `## Enablers`, the text reminder still under Not on the map. `diff <(git -C "$WS" show "$BASE":projects/hall-bookings/storymap.md | awk '/^## /{s=($0=="## Enablers")} !s') <(awk '/^## /{s=($0=="## Enablers")} !s' "$P/storymap.md")` → empty.
- Every Requirement line is kept, each in exactly one place, byte for byte. `diff <(git -C "$WS" grep -h '^- \*\*HAL-REQ-' "$BASE" -- projects/hall-bookings/features projects/hall-bookings/requirements | sort) <(grep -rh '^- \*\*HAL-REQ-' "$P"/features "$P"/requirements | sort)` → empty.
- No Feature straddles two Milestones, and each Milestone's members are exactly its Features. `python3 "$REPO/acceptance/headless/graders/SL-03/milestones.py" "$P"` → empty. The script prints each Feature holding Requirements of two Milestones, and each Milestone whose `## Members` does not list exactly the Features holding its Requirements on the map, or still reads `Not sliced yet.` beside them.
- First online bookings lists its Features. `grep -cx 'Not sliced yet.' "$P/milestones/HAL-MIL-002-first-online-bookings.md"` → `0`.
- Every Feature has exactly one Epic besides its Technical Enablers. `for f in "$P"/features/HAL-FEA-*.md; do grep -lx "Feature: $(basename "$f" | cut -c1-11)" "$P"/epics/*/epic.md | xargs -r grep -Lx 'Technical Enabler: yes' | wc -l; done | sort -u` → `1`.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- The warning names each Requirement not on the map with a short title, `HAL-REQ-017` and those captured before the map alike, and says the Operator can map them first with a later story map session.
- The warning does not hold the slice up: the batch is whole, and the reply asks only for the usual yes.
- Each proposed Milestone item lists its Features as `- <FEA ID> · <title>`.
