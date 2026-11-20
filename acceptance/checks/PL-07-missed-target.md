---
id: PL-07
version: 1
skills: [plan]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PL-07 · A Milestone likely to miss its target raises a Question to the Stakeholder who set it

The hall Project is sliced as in PL-01 and has no Plan. The Operator asks for a plan with slow Throughput, so `HAL-MIL-002` has well under half a chance of meeting the 2027-03-01 target Margaret set. Jenny's proposal says no earlier Plan was shown, so there is no drift to report, and proposes a Question to Margaret: move the date or cut scope, needed by the Milestone. After confirm, one commit adds the Plan folder and that Question.

## Start

As PL-01: Sample v7, then after install the mapped state from `acceptance/fixtures/storymap/mapped/` and the sliced state from `acceptance/fixtures/plan/` laid over it, committed as `[2026-11-17] slice | Slice Community hall bookings`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/storymap/mapped/hall-bookings/." "$H/" && cat "$F/storymap/mapped/log-entry.md" >> "$H/log/2026-11.md" && cp -r "$F/plan/hall-bookings/." "$H/" && cat "$F/plan/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-17] slice | Slice Community hall bookings"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `milestones/HAL-MIL-002-first-online-bookings.md`: members `HAL-FEA-001`, `HAL-FEA-002`, `Target: 2027-03-01 set by Margaret Osei`. `milestones/HAL-MIL-001-walking-skeleton-hirers.md`: `Target: none`.
- `questions/`: the highest ID is `HAL-Q-016`. No `plans/` folder.
- `project.md` People: Margaret Osei, Stakeholder. `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Make a plan for the hall bookings initiative. Stories finished each week, by the Monday of the week: 2026-08-24: 1, 2026-08-31: 0, 2026-09-07: 1, 2026-09-14: 0, 2026-09-21: 1, 2026-09-28: 1, 2026-10-05: 0, 2026-10-12: 1, 2026-10-19: 0, 2026-10-26: 1, 2026-11-02: 0, 2026-11-09: 1. HAL-EPC-001 has 6 open and 5 done Stories. Ravi says HAL-EPC-002 will take 5 to 9 Stories.
2. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- Says no earlier Plan was shown, so there is no drift. `grep -ciE 'nothing to measure drift|no plan version before plan-v1' "$TURNS/1.md"` → 1 or more.
- Proposes the Question to Margaret on the Milestone. Each → 1 or more: `grep -c 'HAL-Q-017' "$TURNS/1.md"`, `grep -c 'HAL-MIL-002' "$TURNS/1.md"`, `grep -c 'Margaret Osei' "$TURNS/1.md"`.

## Key at write

Graded after turn 2. `P="$WS/projects/hall-bookings/plans/plan-v1"`; `Q="$WS/projects/hall-bookings/questions"`; `` d() { sed 's/\[[0-9-]*\]//g' "$@" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | sort -u; } ``. `d` lists the dates in files, leaving out a bracketed log date.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] plan \| plan-v1 '` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- The Plan folder holds the six files, and `plan.md` is not marked shown. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/plans | sort) <(printf 'projects/hall-bookings/plans/plan-v1/%s\n' forecast.json gantt.mmd inputs.json operator-view.md plan.md stakeholder-view.md)` → empty; `grep -c '^Shown:' "$P/plan.md"` → `0`.
- The Forecast gives the Milestone under half a chance of meeting its target. `python3 -c 'import json,sys;m={x["milestone"]:x for x in json.load(open(sys.argv[1]))["milestones"]}["HAL-MIL-002"];print(m["target"], m["target_met_share"] < 0.5)' "$P/forecast.json"` → `2027-03-01 True`.
- One new Question, `HAL-Q-017`. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- projects/hall-bookings/questions | grep -c 'questions/HAL-Q-017-.*\.md$'` → `1`; `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- projects/hall-bookings/questions | wc -l` → `1`.
- The Question asks Margaret to move the date or cut scope, needed by the Milestone and raised from this Plan. Each → `1`: `grep -c '^Needed by: HAL-MIL-002$' "$Q"/HAL-Q-017-*.md`, `grep -c '^Raised from: plans/plan-v1$' "$Q"/HAL-Q-017-*.md`, `grep -c '^Status: open$' "$Q"/HAL-Q-017-*.md`, `grep -c '^Affects: .*HAL-MIL-002' "$Q"/HAL-Q-017-*.md`, `head -n 1 "$Q"/HAL-Q-017-*.md | grep -c 'Margaret Osei'`, `head -n 1 "$Q"/HAL-Q-017-*.md | grep -ci 'scope'`.
- The Question is in the index. `grep -c 'HAL-Q-017' "$Q/index.md"` → `1`.
- The Stakeholder view puts the Milestone under At risk. `sed -n '/^## At risk/,/^## Milestones/p' "$P/stakeholder-view.md" | grep -c 'HAL-MIL-002'` → 1 or more.
- Every date in both views is in `forecast.json`. `comm -23 <(d "$P/stakeholder-view.md" "$P/operator-view.md") <(d "$P/forecast.json")` → empty.
- Every date in the proposal is in `forecast.json` or `inputs.json`. `comm -23 <(d "$TURNS/1.md") <(d "$P/forecast.json" "$P/inputs.json")` → empty.
- Every date in the Question is in `forecast.json`. `comm -23 <(d "$Q"/HAL-Q-017-*.md) <(d "$P/forecast.json")` → empty.

## By eye

- The proposal says plainly that the target is likely missed, quoting the chance, and that the choice is Margaret's.
- No new date is offered for the target.
