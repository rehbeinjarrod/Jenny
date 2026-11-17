---
id: PK-03
version: 3
skills: [pack]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PK-03 · An over-long pack is refused with a re-slice proposal

The Operator asks for the pack of an Epic covering 55 Requirements. The pack would pass 300 lines, and packs are never split, so Jenny stops before proposing anything, writes nothing, and proposes re-slicing the Feature instead.

## Start

Sample v7. Fixture: `acceptance/fixtures/pack/coaching/` (`CRT-FEA-003` Run coaching sessions with 55 Requirements, `CRT-REQ-009` to `CRT-REQ-063`, and its one Epic `CRT-EPC-002`, covering all 55). After install, lay it into the court Project and commit:

```sh
cd "$WS/projects/court-bookings" && F="$REPO/acceptance/fixtures/pack/coaching" && cp -r "$F/features" "$F/epics" . && sed -i "/CRT-FEA-002-see-which-courts-are-free.md) |/r $F/features-index-row.md" features/index.md && sed -i "/^- \[log\/\]/i $(cat "$F/index-line.md")" index.md && git -C "$WS" add -A && git -C "$WS" commit -qm "Add CRT-FEA-003 and CRT-EPC-002"
```

The key relies on `projects/court-bookings/epics/CRT-EPC-002-run-coaching-sessions/epic.md` covering 55 Requirements, `projects/hall-bookings/` (untouched), and `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. Write the pack for the coaching spec.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says why: the 300-line cap. `grep -c '300' "$TURNS/1.md"` → 1 or more.
- Proposes a re-slice. `grep -ciE 're-?slic' "$TURNS/1.md"` → 1 or more.
- No batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → `0`.
- No hall items. `grep -c 'HAL-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- The reply says packs are never split, so the way on is a re-slice of `CRT-FEA-003`, and suggests a seam (by sport, or by kind of session).
- It points at slicing again ("re-slice …") rather than offering a shorter pack.
