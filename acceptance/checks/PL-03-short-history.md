---
id: PL-03
version: 2
skills: [plan]
cursor-bench: false
routing: true
inputs: []
promise: false
---

# PL-03 · "When will it land?" with no Plan, then too little history for any date

The hall Project is sliced as in PL-01 and has no Plan. The Operator asks, in Veneer words, when a Milestone will land. Jenny says there is no Plan yet and asks for Throughput. The Operator types only four weeks. Jenny runs the Forecast, finds under 5 weeks of history, gives no date, says why, and writes nothing.

## Start

As PL-01: Sample v7, then after install the mapped state from `acceptance/fixtures/storymap/mapped/` and the sliced state from `acceptance/fixtures/plan/` laid over it, committed as `[2026-11-17] slice | Slice Community hall bookings`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/storymap/mapped/hall-bookings/." "$H/" && cat "$F/storymap/mapped/log-entry.md" >> "$H/log/2026-11.md" && cp -r "$F/plan/hall-bookings/." "$H/" && cat "$F/plan/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-17] slice | Slice Community hall bookings"
```

The key relies on, in `projects/hall-bookings/` after the overlay: `milestones/HAL-MIL-002-first-online-bookings.md` (First online bookings, `Target: 2027-03-01 set by Margaret Osei`), and no `plans/` folder. `veneer.md`: Project shown as Initiative.

## Operator script

1. When will first online bookings land on the hall initiative?
2. Stories finished each week, by the Monday of the week: 2026-10-26: 2, 2026-11-02: 3, 2026-11-09: 1, 2026-11-16: 2. HAL-EPC-001 has 6 open and 5 done Stories, and Ravi says HAL-EPC-002 will take 5 to 9 Stories.

## Key at proposal

Graded after turns 1 and 2, on `$TURNS/1.md` and `$TURNS/2.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- No forecast date before there is a Plan: the only date is the Milestone's own target. `grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' "$TURNS/1.md" | grep -vx '2027-03-01' | wc -l` → `0`.
- Goes to the plan skill: says there is no Plan yet. `grep -ciE 'no plan|plan yet|make a plan|a plan for' "$TURNS/1.md"` → 1 or more.
- Asks for weekly Throughput. `grep -ciE 'throughput|stories (were )?finished|finished each week' "$TURNS/1.md"` → 1 or more.
- No date from too little history: only the typed weeks or the target. `grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' "$TURNS/2.md" | grep -vxE '2026-10-26|2026-11-02|2026-11-09|2026-11-16|2027-03-01' | wc -l` → `0`.
- Says why: 5 or more weeks are needed, in any wording ("needs 5 or more", "at least 5 weeks"). `grep -ciE '(5|five) or more|(5|five) (or more )?weeks' "$TURNS/2.md"` → 1 or more.
- Proposes no batch. `grep -c 'Nothing is written yet' "$TURNS/2.md"` → `0`.

## Key at write

Graded after turn 2.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- Turn 1 does not answer from the Milestone record alone, as `lookup` would.
- Turn 2 says how many weeks the Forecast counted, and asks for more.
