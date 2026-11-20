---
id: SL-03
version: 3
skills: [slice]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# SL-03 · A Feature across two Milestones is flagged, and the slice keeps within Milestones

The hall Project has a story map. The Operator asks Jenny to slice it, putting seeing which dates are free and choosing the start and finish times in one Feature. Those two Requirements sit in different Milestones on the map, so the Feature would straddle them: Jenny flags it with a re-slice of one Feature per Milestone, before anything is written, and proposes the re-slice instead. The Operator takes it and renames the Feature holding `HAL-REQ-015`; Jenny shows the batch again with the new title and still writes nothing. After confirm, no Feature holds Requirements of two Milestones, each Milestone's members list its Features in place of "Not sliced yet.", the map is unchanged but for its enablers, which become Technical Enablers and Enabler Stories, and everything lands in one commit.

## Start

Sample v7, then after install the mapped state laid over it from the frozen fixture `acceptance/fixtures/storymap/mapped/` (CP-10's result), committed as `[2026-11-16] capture | HAL-SRC-006 Story map session of 2026-11-16`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/storymap/mapped"; cp -r "$F/hall-bookings/." "$H/" && cat "$F/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-16] capture | HAL-SRC-006 Story map session of 2026-11-16"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `storymap.md`: under the step "Find a free date", `HAL-REQ-014` (see which dates the main hall is free) in `HAL-MIL-001` (Walking skeleton (hirers), internal) and `HAL-REQ-015` (choose a start and finish time) in `HAL-MIL-002` (First online bookings). Also `HAL-REQ-016` in `HAL-MIL-001`; `HAL-REQ-001`, `HAL-REQ-005` and `HAL-REQ-011` in `HAL-MIL-002`. `## Not on the map` reads `None.`
- `milestones/HAL-MIL-001-walking-skeleton-hirers.md` and `milestones/HAL-MIL-002-first-online-bookings.md`, each with `## Members` reading `Not sliced yet.`
- `features/HAL-FEA-001-book-and-pay.md` (holds `HAL-REQ-001`; its Epic `HAL-EPC-001` is handed off) and `features/HAL-FEA-002-cancel-a-booking.md` (holds `HAL-REQ-005`; no Epic yet). So `HAL-MIL-002`'s members include both.
- `requirements/unplaced.md`: `HAL-REQ-008` to `HAL-REQ-016`.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Slice the hall bookings initiative. Put seeing which dates are free and choosing the start and finish times together in one Feature.
2. Keep them apart, but call the new Feature that holds HAL-REQ-015 "Pick the booking times".
3. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`, and after turn 2 on `$TURNS/2.md` where a line says so.

- Nothing written, after each turn. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Turn 1, the two Requirements asked for are named. `grep -c 'HAL-REQ-014' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-REQ-015' "$TURNS/1.md"` → 1 or more.
- Turn 1, flagged as across both Milestones. `grep -c 'HAL-MIL-001' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-MIL-002' "$TURNS/1.md"` → 1 or more; `grep -ci 'milestone' "$TURNS/1.md"` → 1 or more.
- Turn 1, a re-slice suggested. `grep -ciE 're-?slice' "$TURNS/1.md"` → 1 or more.
- Turn 2, the batch again. `grep -ci 'nothing is written yet' "$TURNS/2.md"` → 1 or more; `grep -c 'HAL-REQ-014' "$TURNS/2.md"` → 1 or more; `grep -c 'HAL-FEA-002' "$TURNS/2.md"` → 1 or more.
- Turn 2, the amend shown. `grep -ci 'pick the booking times' "$TURNS/2.md"` → 1 or more.
- No leak-trap items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 3. `P="$WS/projects/hall-bookings"`.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] slice \| '` → `1`; `grep -cxF "## $(git -C "$WS" log -1 --format=%s)" "$P"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only slicing files changed, Milestones included. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(features/[^/]+\.md|epics/[^/]+/epic\.md|milestones/HAL-MIL-[0-9]{3}-[^/]+\.md|storymap\.md|requirements/unplaced\.md|index\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- The map is unchanged outside `## Enablers`. `diff <(git -C "$WS" show "$BASE":projects/hall-bookings/storymap.md | awk '/^## /{s=($0=="## Enablers")} !s') <(awk '/^## /{s=($0=="## Enablers")} !s' "$P/storymap.md")` → empty.
- Both Requirements asked for are each in exactly one Feature. `for r in HAL-REQ-014 HAL-REQ-015; do grep -l "^- \*\*$r\*\*" "$P"/features/HAL-FEA-*.md | wc -l; done | sort -u` → `1`.
- They are in different Features. `[ "$(grep -l '^- \*\*HAL-REQ-014\*\*' "$P"/features/HAL-FEA-*.md)" != "$(grep -l '^- \*\*HAL-REQ-015\*\*' "$P"/features/HAL-FEA-*.md)" ] && echo apart` → `apart`.
- No Feature straddles two Milestones, and each Milestone's members are exactly its Features. `python3 "$REPO/acceptance/headless/graders/SL-03/milestones.py" "$P"` → empty. The script prints each Feature holding Requirements of two Milestones, and each Milestone whose `## Members` does not list exactly the Features holding its Requirements on the map, or still reads `Not sliced yet.` beside them.
- Both Milestones now list Features. `grep -lx 'Not sliced yet.' "$P"/milestones/*.md | wc -l` → `0`.
- The amend is written: the Feature holding `HAL-REQ-015` has the new title. `grep -l '^- \*\*HAL-REQ-015\*\*' "$P"/features/HAL-FEA-*.md | xargs -r head -1 | grep -ci 'pick the booking times'` → `1`.
- No pain point recorded. `grep -l '^Pain point:' "$P"/epics/*/epic.md "$P"/features/*.md | wc -l` → `0`.
- Every Feature has exactly one Epic besides its Technical Enablers. `for f in "$P"/features/HAL-FEA-*.md; do grep -lx "Feature: $(basename "$f" | cut -c1-11)" "$P"/epics/*/epic.md | xargs -r grep -Lx 'Technical Enabler: yes' | wc -l; done | sort -u` → `1`.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- Turn 1 says in plain words why the two cannot share a Feature: they sit in different Milestones on the map, so the Feature would need a second Epic or hold back the Walking skeleton.
- Turn 1 says how to deliver them together if the Operator wants that: move a card to the other Milestone on the map first.
- Each proposed Milestone item lists its Features as `- <FEA ID> · <title>`, with `HAL-FEA-001` and `HAL-FEA-002` under `HAL-MIL-002`.
- The batch warns that `HAL-REQ-008` to `HAL-REQ-010`, `HAL-REQ-012` and `HAL-REQ-013` are not on the map, and goes ahead.
- Turn 2 shows the batch in full under the same "Slice …" heading, with only the renamed Feature (and lines citing its title or slug) changed.
