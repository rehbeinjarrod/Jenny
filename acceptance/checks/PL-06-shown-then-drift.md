---
id: PL-06
version: 3
skills: [plan]
cursor-bench: false
routing: true
inputs: []
promise: false
---

# PL-06 · A Plan marked shown, then a new Plan reports drift against it

The hall Project has a committed `plans/plan-v1/`, never shown. The Operator says it went to Margaret. Jenny proposes one `Shown:` line appended to the Plan's `plan.md`, and on confirm commits only that and the log. Then the Operator gives a week more of Throughput and new Story counts and asks for a new Plan. Jenny's proposal quotes the Drift script: dates moved since plan-v1, shown to Margaret, and the inputs that changed. Nothing more is written.

## Start

Sample v7, then after install the mapped state from `acceptance/fixtures/storymap/mapped/` and the sliced state from `acceptance/fixtures/plan/` laid over it, committed as `[2026-11-17] slice | Slice Community hall bookings`, then the committed Plan from `acceptance/fixtures/plan-shown/`, committed as `[2026-11-18] plan | plan-v1 Community hall bookings`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/storymap/mapped/hall-bookings/." "$H/" && cat "$F/storymap/mapped/log-entry.md" >> "$H/log/2026-11.md" && cp -r "$F/plan/hall-bookings/." "$H/" && cat "$F/plan/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-17] slice | Slice Community hall bookings" && cp -r "$F/plan-shown/hall-bookings/." "$H/" && cat "$F/plan-shown/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-18] plan | plan-v1 Community hall bookings"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `plans/plan-v1/plan.md`: no `Shown:` line. `plans/plan-v1/inputs.json`: twelve weeks from 2026-08-24 to 2026-11-09, `HAL-EPC-001` 6 open and 5 done, read 2026-11-18, `HAL-EPC-002` range 5 to 9.
- `epics/HAL-EPC-001-book-and-pay/epic.md` handed off; `epics/HAL-EPC-002-cancel-a-booking/epic.md` depends on it.
- `project.md` People: Margaret Osei, Stakeholder. `veneer.md`: Project shown as Initiative, Epic as Spec.

## Operator script

1. plan-v1 of the hall bookings initiative went to Margaret Osei today.
2. Yes, write it.
3. Make a new plan for the hall bookings initiative. Stories finished each week, by the Monday of the week: 2026-08-24: 2, 2026-08-31: 3, 2026-09-07: 1, 2026-09-14: 4, 2026-09-21: 2, 2026-09-28: 3, 2026-10-05: 0, 2026-10-12: 2, 2026-10-19: 3, 2026-10-26: 2, 2026-11-02: 4, 2026-11-09: 2, 2026-11-16: 3. HAL-EPC-001 now has 3 open and 8 done Stories. Ravi says HAL-EPC-002 will still take 5 to 9 Stories.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md` and after turn 3 on `$TURNS/3.md`.

After turn 1:

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- Shows the line to append. `grep -cE 'Shown: [0-9]{4}-[0-9]{2}-[0-9]{2} to Margaret Osei' "$TURNS/1.md"` → 1 or more.

After turn 3:

- Nothing written since the Shown commit. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/3.md"` → 1 or more.
- Names the new Plan version. `grep -c 'plan-v2' "$TURNS/3.md"` → 1 or more.
- Measures drift against plan-v1 as shown to Margaret: one line names plan-v1 and when and to whom it was shown, in any wording around them. `grep 'plan-v1' "$TURNS/3.md" | grep -ciE 'shown [0-9]{4}-[0-9]{2}-[0-9]{2} to Margaret Osei'` → 1 or more.
- Names the Story counts that changed. `grep -cE '6 open, 5 done.*→.*3 open, 8 done' "$TURNS/3.md"` → 1 or more.
- Names the week of Throughput added. `grep -c 'added 2026-11-16: 3' "$TURNS/3.md"` → 1 or more.
- Names each Milestone in the drift. Each → 1 or more: `grep -c 'HAL-MIL-001' "$TURNS/3.md"`, `grep -c 'HAL-MIL-002' "$TURNS/3.md"`.

## Key at write

Graded after turn 3. `P="$WS/projects/hall-bookings/plans/plan-v1"`.

- One commit, the Shown one. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] plan \| Shown plan-v1 to Margaret Osei$'` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only `plan.md` and the log changed. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD | sort) <(printf 'projects/hall-bookings/%s\n' "log/$(date +%Y-%m).md" plans/plan-v1/plan.md | sort)` → empty.
- `plan.md` gained one line, the `Shown:` line dated today, and lost none. `[ "$(git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/plans/plan-v1/plan.md | grep -E '^[+-]' | grep -vE '^(\+\+\+|---) ')" = "+Shown: $(date +%F) to Margaret Osei" ] && echo one` → `one`.
- No plan-v2 folder. `ls "$WS/projects/hall-bookings/plans"` → `plan-v1`.

## By eye

- Turn 1 asks nothing it can take from the Operator's words: the version, Margaret and today.
- Turn 3 quotes the drift in shown names (Specs, not Epics) with the dates as the script gave them.
