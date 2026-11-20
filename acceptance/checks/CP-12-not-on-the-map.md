---
id: CP-12
version: 2
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# CP-12 · A Capture into a mapped Project lists its new Requirement under Not on the map

The hall Project has a story map from the session of 2026-11-16. The Operator types a note outside any session: hirers should get a text reminder the day before their booking. Jenny proposes the new Requirement and says it goes under `## Not on the map`. On the yes, the map gains that one line and nothing else on it changes.

## Start

Sample v7, then after install the mapped state laid over it from the frozen fixture `acceptance/fixtures/storymap/mapped/` (CP-10's result), committed as `[2026-11-16] capture | HAL-SRC-006 Story map session of 2026-11-16`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/storymap/mapped"; cp -r "$F/hall-bookings/." "$H/" && cat "$F/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-16] capture | HAL-SRC-006 Story map session of 2026-11-16"
```

Fixture: `acceptance/fixtures/storymap/typed-note-reminder.md` (the Operator's note: Margaret wants a text reminder the day before a booking, with its start time).

The key relies on, in `projects/hall-bookings/` after the overlay:

- `storymap.md`: two activities, Milestones `HAL-MIL-001` and `HAL-MIL-002`, two enablers, and `## Not on the map` reading `None.`
- Highest IDs `HAL-SRC-006`, `HAL-REQ-016`, `HAL-Q-016`, so the new ones are `HAL-SRC-007` and `HAL-REQ-017`. Nothing active covers a text reminder.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Capture this: <paste: storymap/typed-note-reminder.md>
2. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- The new Requirement goes off the map. `grep -c 'HAL-REQ-017' "$TURNS/1.md"` → 1 or more; `grep -ci 'not on the map' "$TURNS/1.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `H="$WS/projects/hall-bookings"`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| '` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- The new Requirement cites the note. `grep -rhE '^- \*\*HAL-REQ-017\*\* .* · Source: HAL-SRC-007 · Status: active$' "$H" | wc -l` → `1`; `grep -rhE '^- \*\*HAL-REQ-017\*\* ' "$H" | grep -ciE '\btext'` → `1`; `grep -rhE '^- \*\*HAL-REQ-017\*\* ' "$H" | grep -ci 'day before'` → `1`; `grep -rhE '^- \*\*HAL-REQ-017\*\* ' "$H" | grep -ci 'start time'` → `1`.
- It is listed under Not on the map. `sed -n '/^## Not on the map$/,$p' "$H/storymap.md" | grep -cE '^- HAL-REQ-017( · .*)?$'` → `1`; `sed -n '/^## Not on the map$/,$p' "$H/storymap.md" | grep -cx 'None.'` → `0`.
- Nothing else on the map changes. `git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/storymap.md | grep -E '^[-+]' | grep -vE '^(\+\+\+|---) ' | grep -vcE '^\+- HAL-REQ-017( · .*)?$|^-None\.$|^[-+]$'` → `0`.
- Milestones untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/milestones` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep '^+' | grep -v '^+>' | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics projects/court-bookings veneer.md workspace.md outbox` → empty.

## By eye

- The proposal names the Requirement's place as `## Not on the map` in `storymap.md`, in the indexes and log item.
- The Requirement is placed in `requirements/unplaced.md` or a fitting Feature, as any Capture places it.
