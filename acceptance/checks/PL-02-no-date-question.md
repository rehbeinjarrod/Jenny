---
id: PL-02
version: 3
skills: [plan]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PL-02 · An Epic with no Story count gets no date and a Question for the engineers

The hall Project is sliced as in PL-01. The Operator asks for a plan with twelve weeks of Throughput and the handed-off Epic's counts, but the engineers have not sized `HAL-EPC-002`, and no finished Epics are known. The Forecast leaves `HAL-EPC-002`, and the Milestone holding it, undated. Jenny says so, lists it as undated in the views, and raises one Question asking the engineers for a low to high Story count range, all in the one batch written after confirm.

## Start

As PL-01: Sample v7, then after install the mapped state from `acceptance/fixtures/storymap/mapped/` and the sliced state from `acceptance/fixtures/plan/` laid over it, committed as `[2026-11-17] slice | Slice Community hall bookings`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/storymap/mapped/hall-bookings/." "$H/" && cat "$F/storymap/mapped/log-entry.md" >> "$H/log/2026-11.md" && cp -r "$F/plan/hall-bookings/." "$H/" && cat "$F/plan/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-17] slice | Slice Community hall bookings"
```

The key relies on, in `projects/hall-bookings/` after the overlay: `HAL-EPC-002` (Feature `HAL-FEA-002`, not handed off) is in `HAL-MIL-002` only, through `HAL-FEA-002`; `HAL-MIL-001` lists `HAL-FEA-001` alone, so holds only `HAL-EPC-001`. The highest Question is `HAL-Q-016`, so the next is `HAL-Q-017`. `project.md` People: Ravi Kumar, engineer. `veneer.md`: Epic shown as Spec, Question as Open item.

## Operator script

1. Make a plan for the hall bookings initiative. Stories finished each week, by the Monday of the week: 2026-08-24: 2, 2026-08-31: 3, 2026-09-07: 1, 2026-09-14: 4, 2026-09-21: 2, 2026-09-28: 3, 2026-10-05: 0, 2026-10-12: 2, 2026-10-19: 3, 2026-10-26: 2, 2026-11-02: 4, 2026-11-09: 2. HAL-EPC-001 has 6 open and 5 done Stories. The engineers haven't sized HAL-EPC-002 yet.
2. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- Proposes the Question for the undated Epic. `grep -c 'HAL-Q-017' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-EPC-002' "$TURNS/1.md"` → 1 or more.

## Key at write

Graded after turn 2. `P="$WS/projects/hall-bookings/plans/plan-v1"`; `Q="$WS/projects/hall-bookings/questions"`; `` d() { sed 's/\[[0-9-]*\]//g' "$@" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | sort -u; } ``. `d` lists the dates in files, leaving out a bracketed log date.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] plan \| plan-v1 '` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- The Plan folder holds the six files. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/plans | sort) <(printf 'projects/hall-bookings/plans/plan-v1/%s\n' forecast.json gantt.mmd inputs.json operator-view.md plan.md stakeholder-view.md)` → empty.
- No range or count was made up for the unsized Epic. `python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print("HAL-EPC-002" in d.get("ranges",{}), "HAL-EPC-002" in d.get("epics",{}), len(d.get("finished_epics",[])))' "$P/inputs.json"` → `False False 0`.
- The Forecast leaves the Epic and its Milestone undated, and dates the other Milestone. `python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));e={x["epic"]:x for x in d["epics"]};m={x["milestone"]:x for x in d["milestones"]};print(e["HAL-EPC-002"]["no_date"][:14], m["HAL-MIL-002"]["likely_finish"], m["HAL-MIL-001"]["likely_finish"] is not None)' "$P/forecast.json"` → `no Story count None True`.
- `forecast.json` and `gantt.mmd` are the script's own output for those inputs. `T="$(mktemp -d)/plan-v1"`; `mkdir -p "$T" && cp "$P/inputs.json" "$T/" && python3 "$SK/plan/scripts/forecast.py" "$WS/projects/hall-bookings" "$T" && cmp "$T/forecast.json" "$P/forecast.json" && cmp "$T/gantt.mmd" "$P/gantt.mmd" && echo same` → `same`.
- One new Question, `HAL-Q-017`. `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- projects/hall-bookings/questions | grep -c 'questions/HAL-Q-017-.*\.md$'` → `1`; `git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- projects/hall-bookings/questions | wc -l` → `1`.
- The Question asks for a range for `HAL-EPC-002`, raised from this Plan. Each → `1`: `grep -c '^Needed by: HAL-EPC-002$' "$Q"/HAL-Q-017-*.md`, `grep -c '^Raised from: plans/plan-v1$' "$Q"/HAL-Q-017-*.md`, `grep -c '^Status: open$' "$Q"/HAL-Q-017-*.md`, `grep -c '^Affects: .*HAL-MIL-002' "$Q"/HAL-Q-017-*.md`, `head -n 1 "$Q"/HAL-Q-017-*.md | grep -ci 'range'`.
- The Question is in the index. `grep -c 'HAL-Q-017' "$Q/index.md"` → `1`.
- The Stakeholder view lists the undated Epic with its Question. Each → 1 or more: `grep -c 'HAL-EPC-002' "$P/stakeholder-view.md"`, `grep -c 'HAL-Q-017' "$P/stakeholder-view.md"`.
- Every date in both views is in `forecast.json`. `comm -23 <(d "$P/stakeholder-view.md" "$P/operator-view.md") <(d "$P/forecast.json")` → empty.
- Every date in the proposal is in `forecast.json` or `inputs.json`. `comm -23 <(d "$TURNS/1.md") <(d "$P/forecast.json" "$P/inputs.json")` → empty.
- Every date in the report is in `forecast.json` or `inputs.json`. `comm -23 <(d "$TURNS/2.md") <(d "$P/forecast.json" "$P/inputs.json")` → empty.
- Both views are in shown names. `python3 "$SK/jenny/scripts/veneer_scan.py" < "$P/stakeholder-view.md" > /dev/null; echo $?` → `0`; `python3 "$SK/jenny/scripts/veneer_scan.py" < "$P/operator-view.md" > /dev/null; echo $?` → `0`.

## By eye

- The proposal says why `HAL-EPC-002` has no date and who the Question is for (the engineers, Ravi Kumar).
- No date is offered for `HAL-MIL-002`, not even a rough one.
