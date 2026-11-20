---
id: PL-01
version: 3
skills: [plan]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PL-01 · A Plan from typed Throughput, every date quoted from the Forecast

The hall Project is sliced against its story map: `HAL-EPC-001` is handed off, and `HAL-EPC-002` depends on it. The Operator asks for a plan, typing twelve weeks of Throughput, the handed-off Epic's open and done Story counts, and an engineer's range for the other. Jenny runs the Forecast before proposing, shows the batch with the start date and Epics in flight at their defaults, and writes nothing until confirm. After confirm, one commit adds `plans/plan-v1/` with the inputs, the script's own `forecast.json` and `gantt.mmd`, and both views carrying the chart, and every date she gave in chat or in a view is one the Forecast holds.

## Start

Sample v7, then after install the mapped state from `acceptance/fixtures/storymap/mapped/` (CP-10's result) and the sliced state from `acceptance/fixtures/plan/` laid over it, committed as `[2026-11-17] slice | Slice Community hall bookings`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/storymap/mapped/hall-bookings/." "$H/" && cat "$F/storymap/mapped/log-entry.md" >> "$H/log/2026-11.md" && cp -r "$F/plan/hall-bookings/." "$H/" && cat "$F/plan/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-17] slice | Slice Community hall bookings"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `epics/HAL-EPC-001-book-and-pay/epic.md`: handed off (`Tech face:` HALL-12), Feature `HAL-FEA-001`.
- `epics/HAL-EPC-002-cancel-a-booking/epic.md`: Feature `HAL-FEA-002`, `## Depends on` lists `HAL-EPC-001`; not handed off.
- `milestones/HAL-MIL-001-walking-skeleton-hirers.md` (members `HAL-FEA-001`, `Target: none`) and `milestones/HAL-MIL-002-first-online-bookings.md` (members `HAL-FEA-001`, `HAL-FEA-002`, `Target: 2027-03-01 set by Margaret Osei`).
- No `plans/` folder. `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Make a plan for the hall bookings initiative. Stories finished each week, by the Monday of the week: 2026-08-24: 2, 2026-08-31: 3, 2026-09-07: 1, 2026-09-14: 4, 2026-09-21: 2, 2026-09-28: 3, 2026-10-05: 0, 2026-10-12: 2, 2026-10-19: 3, 2026-10-26: 2, 2026-11-02: 4, 2026-11-09: 2. HAL-EPC-001 has 6 open and 5 done Stories. Ravi says HAL-EPC-002 will take 5 to 9 Stories.
2. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- Shows each Milestone. Each → 1 or more: `grep -c 'HAL-MIL-001' "$TURNS/1.md"`, `grep -c 'HAL-MIL-002' "$TURNS/1.md"`.
- Names the Plan version. `grep -c 'plan-v1' "$TURNS/1.md"` → 1 or more.

## Key at write

Graded after turn 2. `P="$WS/projects/hall-bookings/plans/plan-v1"`; `` d() { sed 's/\[[0-9-]*\]//g' "$@" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | sort -u; } ``. `d` lists the dates in files, leaving out a bracketed log date such as `[2026-11-18]`.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] plan \| plan-v1 '` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- The Plan folder holds the six files. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/plans | sort) <(printf 'projects/hall-bookings/plans/plan-v1/%s\n' forecast.json gantt.mmd inputs.json operator-view.md plan.md stakeholder-view.md)` → empty.
- Outside the Plan folder, only the index and the log changed. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD | grep -v '^projects/hall-bookings/plans/' | sort) <(printf 'projects/hall-bookings/%s\n' index.md "log/$(date +%Y-%m).md" | sort)` → empty.
- The inputs are what the Operator typed, with the default Epics in flight. `python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));w=d["throughput"]["weeks"];e=d["epics"]["HAL-EPC-001"];r=d["ranges"]["HAL-EPC-002"];print(len(w),sum(x["done"] for x in w),e["open"],e["done"],r["low"],r["high"],d.get("in_flight",2))' "$P/inputs.json"` → `12 28 6 5 5 9 2`.
- The start is the default, the Monday after today. `python3 -c 'import json,sys,datetime as d;t=d.date.today();print(json.load(open(sys.argv[1]))["start"]==str(t+d.timedelta(days=7-t.weekday())))' "$P/inputs.json"` → `True`.
- `forecast.json` and `gantt.mmd` are the script's own output for those inputs. `T="$(mktemp -d)/plan-v1"`; `mkdir -p "$T" && cp "$P/inputs.json" "$T/" && python3 "$SK/plan/scripts/forecast.py" "$WS/projects/hall-bookings" "$T" && cmp "$T/forecast.json" "$P/forecast.json" && cmp "$T/gantt.mmd" "$P/gantt.mmd" && echo same` → `same`.
- Every bar and diamond in the Gantt has its `forecast.json` dates. `python3 "$SK/plan/scripts/forecast.py" --check "$P"; echo $?` → `0`.
- Both views carry the Gantt whole. Each → empty: `diff <(sed -n '/^\x60\x60\x60mermaid$/,/^\x60\x60\x60$/{/^\x60\x60\x60/d;p}' "$P/stakeholder-view.md") "$P/gantt.mmd"`, `diff <(sed -n '/^\x60\x60\x60mermaid$/,/^\x60\x60\x60$/{/^\x60\x60\x60/d;p}' "$P/operator-view.md") "$P/gantt.mmd"`.
- Both views give the legend outside the chart. Each → 1 or more: `sed '/^\x60\x60\x60mermaid$/,/^\x60\x60\x60$/d' "$P/stakeholder-view.md" | grep -c '◆'`, `sed '/^\x60\x60\x60mermaid$/,/^\x60\x60\x60$/d' "$P/operator-view.md" | grep -c '◆'`.
- The Operator view gives the Lucid steps for the Gantt. Each → 1 or more: `grep -c 'gantt.mmd' "$P/operator-view.md"`, `grep -ci 'Lucid macro' "$P/operator-view.md"`.
- Every date in both views is in `forecast.json`. `comm -23 <(d "$P/stakeholder-view.md" "$P/operator-view.md") <(d "$P/forecast.json")` → empty.
- Every date in the proposal is in `forecast.json` or `inputs.json`. `comm -23 <(d "$TURNS/1.md") <(d "$P/forecast.json" "$P/inputs.json")` → empty.
- Every date in the report is in `forecast.json` or `inputs.json`. `comm -23 <(d "$TURNS/2.md") <(d "$P/forecast.json" "$P/inputs.json")` → empty.
- The Stakeholder view quotes each Milestone's likely date. `grep -cF "$(python3 -c 'import json,sys;print([m["likely_finish"] for m in json.load(open(sys.argv[1]))["milestones"] if m["milestone"]=="HAL-MIL-002"][0])' "$P/forecast.json")" "$P/stakeholder-view.md"` → 1 or more; `grep -cF "$(python3 -c 'import json,sys;print([m["likely_finish"] for m in json.load(open(sys.argv[1]))["milestones"] if m["milestone"]=="HAL-MIL-001"][0])' "$P/forecast.json")" "$P/stakeholder-view.md"` → 1 or more.
- Both views are in shown names. `grep -c 'Spec' "$P/operator-view.md"` → 1 or more; `python3 "$SK/jenny/scripts/veneer_scan.py" < "$P/stakeholder-view.md" > /dev/null; echo $?` → `0`; `python3 "$SK/jenny/scripts/veneer_scan.py" < "$P/operator-view.md" > /dev/null; echo $?` → `0`.
- The Operator view adds the Epic table and the seed. `grep -c 'HAL-EPC-002' "$P/operator-view.md"` → 1 or more; `grep -ciE 'seed' "$P/operator-view.md"` → 1 or more.
- The plan record is not marked shown yet. `grep -c "^Shown:" "$P/plan.md"` → `0`.
- Every Epic is dated, so no Question is raised. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/questions` → empty.

## By eye

- The batch shows the start date and Epics in flight as defaults the Operator can change.
- The Stakeholder view leads with what is at risk, then one line per Milestone, then the chart under its one-line legend: `HAL-EPC-001` grouped under `HAL-MIL-001`, `HAL-EPC-002` under `HAL-MIL-002`, each group closed by its ◆ row.
- The report gives one line per Milestone and says the Plan is frozen.
