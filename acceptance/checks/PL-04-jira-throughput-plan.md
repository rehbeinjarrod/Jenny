---
id: PL-04
version: 3
skills: [plan]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PL-04 · A Plan from Throughput and Story counts read from Jira

The hall Project is sliced as in PL-01: `HAL-EPC-001` is handed off on tech face `HALL-12`, and `HAL-EPC-002` depends on it. The Operator asks for a plan without typing any Throughput. Jenny offers to read it from the team's Jira project, `HALL`. On "read it from Jira" she reads the project's done items over the last year and `HALL-12`'s child work items through the MCP stand-ins, counts the weekly Throughput with the Throughput script, leaves out the won't-do items and the one closed without work, names the two items that were never in progress, and proposes the batch with the source recorded. After confirm, one commit adds `plans/plan-v1/` whose `inputs.json` holds the fixture's weeks, finished Epics and `HALL-12`'s counts, with the JQL and run date as the source.

## Start

As PL-01: Sample v7, then after install the mapped state from `acceptance/fixtures/storymap/mapped/` and the sliced state from `acceptance/fixtures/plan/` laid over it, committed as `[2026-11-17] slice | Slice Community hall bookings`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/storymap/mapped/hall-bookings/." "$H/" && cat "$F/storymap/mapped/log-entry.md" >> "$H/log/2026-11.md" && cp -r "$F/plan/hall-bookings/." "$H/" && cat "$F/plan/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-17] slice | Slice Community hall bookings"
```

MCP stand-in: `https://example.atlassian.net/jira/software/projects/HALL` → `jira/hall-done-items.json` (both done-item searches of project `HALL`: 63 done items, 60 of them counted across the 26 weeks from 2026-05-18 to 2026-11-09; `HALL-33` has status Won't Do and `HALL-48` the label `wontdo`; `HALL-41`, `HALL-57` and `HALL-63` were never in progress, and `HALL-63` was done within an hour of being made; finished Epics `HALL-2`, `HALL-5` and `HALL-8` with 9, 11 and 8 counted children).

MCP stand-in: `https://example.atlassian.net/browse/HALL-12` → `jira/hall-12-plan.md` (`HALL-12` In Progress, with 5 done and 6 open child work items).

The fixture's dates are fixed and the Throughput script reads 52 weeks back from today, so from 2027-05-24 its oldest week falls out of the window and the 60-Story key fails: move the fixture's dates forward then.

The key relies on, in `projects/hall-bookings/` after the overlay: `epics/HAL-EPC-001-book-and-pay/epic.md` (`Tech face:` HALL-12), `epics/HAL-EPC-002-cancel-a-booking/epic.md` (not handed off), the Milestones `HAL-MIL-001` and `HAL-MIL-002`, and no `plans/` folder. `veneer.md`: Project shown as Initiative, Epic as Spec.

## Operator script

1. Make a plan for the hall bookings initiative. Ravi says HAL-EPC-002 will take 5 to 9 Stories.
2. Read it from Jira.
3. Keep both of the items that were never in progress: they were real work. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md` and after turn 2 on `$TURNS/2.md`, each before the next turn is sent.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.

After turn 1 only:

- Offers to read the Throughput from the team's Jira project, `HALL`. `grep -ciE 'from (the |your |the team.s )?(jira|hall)|jira project' "$TURNS/1.md"` → 1 or more; `grep -cwE 'HALL' "$TURNS/1.md"` → 1 or more.
- Proposes no batch before the Throughput comes: no Plan file and no date. `grep -cE 'forecast\.json|inputs\.json|stakeholder-view|operator-view|gantt' "$TURNS/1.md"` → `0`; `grep -cE '[0-9]{4}-[0-9]{2}-[0-9]{2}' "$TURNS/1.md"` → `0`.

After turn 2 only:

- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/2.md"` → 1 or more.
- Names the Plan version and each Milestone. Each → 1 or more: `grep -c 'plan-v1' "$TURNS/2.md"`, `grep -c 'HAL-MIL-001' "$TURNS/2.md"`, `grep -c 'HAL-MIL-002' "$TURNS/2.md"`.
- Names each item left out. Each → 1 or more: `grep -c 'HALL-33' "$TURNS/2.md"`, `grep -c 'HALL-48' "$TURNS/2.md"`, `grep -c 'HALL-63' "$TURNS/2.md"`.
- Names each never-in-progress item for the Operator to decide on. Each → 1 or more: `grep -c 'HALL-41' "$TURNS/2.md"`, `grep -c 'HALL-57' "$TURNS/2.md"`.

## Key at write

Graded after turn 3. `P="$WS/projects/hall-bookings/plans/plan-v1"`; `J="$REPO/acceptance/fixtures/jira/hall-done-items.json"`; `` r() { python3 -c 'import json,re,sys;print(re.search(r"run (\d{4}-\d{2}-\d{2})",json.load(open(sys.argv[1]))["throughput"]["from"]).group(1))' "$P/inputs.json"; } ``; `` d() { sed 's/\[[0-9-]*\]//g' "$@" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | sort -u; } ``. `r` is the run date the source records; `d` lists the dates in files, leaving out a bracketed log date.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] plan \| plan-v1 '` → `1`.
- The Plan folder holds the six files, and no copy of the Jira read. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/plans | sort) <(printf 'projects/hall-bookings/plans/plan-v1/%s\n' forecast.json gantt.mmd inputs.json operator-view.md plan.md stakeholder-view.md)` → empty.
- Outside the Plan folder, only the index and the log changed: no Epic record holds the tech face's status. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD | grep -v '^projects/hall-bookings/plans/' | sort) <(printf 'projects/hall-bookings/%s\n' index.md "log/$(date +%Y-%m).md" | sort)` → empty.
- The source names the Jira project, both searches and a run date of today. `python3 -c 'import json,sys;f=json.load(open(sys.argv[1]))["throughput"]["from"];print(all(s in f for s in ("Jira","HALL","statusCategory = Done","WAS NOT")))' "$P/inputs.json"` → `True`; `[ "$(r)" = "$(date +%F)" ] && echo today` → `today`.
- The weeks and finished Epics are the Throughput script's for the fixture on the run date. `python3 -c 'import json,sys;i=json.load(open(sys.argv[1]));o=json.load(sys.stdin);print(i["throughput"]["weeks"]==o["weeks"],i["finished_epics"]==o["finished_epics"])' "$P/inputs.json" < <(python3 "$SK/plan/scripts/throughput.py" "$J" --today "$(r)")` → `True True`.
- The fixture's counted items, both never-in-progress items kept: 60 Stories, and the three finished Epics. `python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(sum(w["done"] for w in d["throughput"]["weeks"]),[(e["key"],e["stories"]) for e in d["finished_epics"]])' "$P/inputs.json"` → `60 [('HALL-2', 9), ('HALL-5', 11), ('HALL-8', 8)]`.
- The handed-off Epic's counts come from its tech face, read today, with no status stored. `python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));e=d["epics"]["HAL-EPC-001"];r=d["ranges"]["HAL-EPC-002"];print(e["open"],e["done"],sorted(e),r["low"],r["high"])' "$P/inputs.json"` → `6 5 ['done', 'open', 'read'] 5 9`; `python3 -c 'import json,sys,datetime as d;print(json.load(open(sys.argv[1]))["epics"]["HAL-EPC-001"]["read"]==str(d.date.today()))' "$P/inputs.json"` → `True`.
- `forecast.json` and `gantt.mmd` are the script's own output for those inputs. `T="$(mktemp -d)/plan-v1"`; `mkdir -p "$T" && cp "$P/inputs.json" "$T/" && python3 "$SK/plan/scripts/forecast.py" "$WS/projects/hall-bookings" "$T" && cmp "$T/forecast.json" "$P/forecast.json" && cmp "$T/gantt.mmd" "$P/gantt.mmd" && echo same` → `same`.
- Every date in both views is in `forecast.json`. `comm -23 <(d "$P/stakeholder-view.md" "$P/operator-view.md") <(d "$P/forecast.json")` → empty.
- Every date in the proposal and the report is in `forecast.json`, `inputs.json` or the Jira read. Each → empty: `comm -23 <(d "$TURNS/2.md") <(d "$P/forecast.json" "$P/inputs.json" "$J" "$REPO/acceptance/fixtures/jira/hall-12-plan.md")`, `comm -23 <(d "$TURNS/3.md") <(d "$P/forecast.json" "$P/inputs.json" "$J" "$REPO/acceptance/fixtures/jira/hall-12-plan.md")`.

## By eye

- Turn 1 offers Jira or typed Throughput, naming the `HALL` project, and stops.
- Turn 2 names the source and the weeks counted, lists the left-out items each with its reason, and asks about `HALL-41` and `HALL-57` one by one.
- Nothing in the batch or the records gives `HALL-12`'s own status.
