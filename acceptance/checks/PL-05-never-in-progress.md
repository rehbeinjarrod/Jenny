---
id: PL-05
version: 1
skills: [plan]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PL-05 · Items never in progress are the Operator's to keep or leave out

The hall Project is sliced as in PL-01, and the Operator asks for a plan with the Throughput read from Jira. Two of the done items, `HALL-41` and `HALL-57`, never went through In Progress. Jenny counts them, names them in the batch and asks whether each was real work. The Operator leaves `HALL-57` out and keeps `HALL-41`. Jenny counts again without it, runs the Forecast again and shows the batch again; after confirm, `inputs.json` holds one Story fewer in `HALL-57`'s week and its source says who left it out.

## Start

As PL-01: Sample v7, then after install the mapped state from `acceptance/fixtures/storymap/mapped/` and the sliced state from `acceptance/fixtures/plan/` laid over it, committed as `[2026-11-17] slice | Slice Community hall bookings`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/storymap/mapped/hall-bookings/." "$H/" && cat "$F/storymap/mapped/log-entry.md" >> "$H/log/2026-11.md" && cp -r "$F/plan/hall-bookings/." "$H/" && cat "$F/plan/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-17] slice | Slice Community hall bookings"
```

MCP stand-in: `https://example.atlassian.net/jira/software/projects/HALL` → `jira/hall-done-items.json` (as in PL-04: 60 counted items; `HALL-41`, done 2026-08-10 under finished Epic `HALL-8`, and `HALL-57`, done 2026-09-24 with no parent, were never in progress). The fixture ages out from 2027-05-24, as PL-04 says.

MCP stand-in: `https://example.atlassian.net/browse/HALL-12` → `jira/hall-12-plan.md` (5 done and 6 open child work items).

The key relies on, in `projects/hall-bookings/` after the overlay: `HAL-EPC-001` handed off on `HALL-12`, `HAL-EPC-002` not handed off, and no `plans/` folder. `project.md`: Operator Dana Wells.

## Operator script

1. Make a plan for the hall bookings initiative, with the Throughput read from Jira. Ravi says HAL-EPC-002 will take 5 to 9 Stories.
2. HALL-57 was only a link change, so leave it out. HALL-41 was real work: keep it.
3. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md` and after turn 2 on `$TURNS/2.md`, each before the next turn is sent.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/<n>.md"` → 1 or more.

After turn 1 only:

- Names each never-in-progress item. Each → 1 or more: `grep -c 'HALL-41' "$TURNS/1.md"`, `grep -c 'HALL-57' "$TURNS/1.md"`.
- Asks whether each was real work to keep or one to leave out. `grep -ciE 'real work|keep (it|them|each|both|either)|leave (it|them|each|either|any of them) out' "$TURNS/1.md"` → 1 or more.

After turn 2 only:

- Shows `HALL-57` as left out by the Operator, and one Story fewer. `grep 'HALL-57' "$TURNS/2.md" | grep -ciE 'left out|leav(e|ing) .{0,20}out|by (the Operator|Dana)'` → 1 or more; `grep -cw '59' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 3. `P="$WS/projects/hall-bookings/plans/plan-v1"`; `J="$REPO/acceptance/fixtures/jira/hall-done-items.json"`; `` r() { python3 -c 'import json,re,sys;print(re.search(r"run (\d{4}-\d{2}-\d{2})",json.load(open(sys.argv[1]))["throughput"]["from"]).group(1))' "$P/inputs.json"; } ``. `r` is the run date the source records.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- One Story fewer, in `HALL-57`'s week, and `HALL-41` still counted. `python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));w={x["week"]:x["done"] for x in d["throughput"]["weeks"]};print(sum(w.values()),w["2026-09-21"],w["2026-08-10"])' "$P/inputs.json"` → `59 3 3`.
- The weeks and finished Epics are the Throughput script's with `HALL-57` left out. `python3 -c 'import json,sys;i=json.load(open(sys.argv[1]));o=json.load(sys.stdin);print(i["throughput"]["weeks"]==o["weeks"],i["finished_epics"]==o["finished_epics"])' "$P/inputs.json" < <(python3 "$SK/plan/scripts/throughput.py" "$J" --today "$(r)" --leave-out HALL-57)` → `True True`.
- The source says who left `HALL-57` out. `python3 -c 'import json,sys;f=json.load(open(sys.argv[1]))["throughput"]["from"];print("HALL-57" in f,"Dana" in f,"HALL-41" in f)' "$P/inputs.json"` → `True True False`.
- `forecast.json` and `gantt.mmd` are the script's own output for those inputs. `T="$(mktemp -d)/plan-v1"`; `mkdir -p "$T" && cp "$P/inputs.json" "$T/" && python3 "$SK/plan/scripts/forecast.py" "$WS/projects/hall-bookings" "$T" && cmp "$T/forecast.json" "$P/forecast.json" && cmp "$T/gantt.mmd" "$P/gantt.mmd" && echo same` → `same`.

## By eye

- Turn 1 asks about `HALL-41` and `HALL-57` one by one, each with its done date, and says they are counted until the Operator says otherwise.
- Turn 2 shows the batch again in full with the new Throughput and Forecast.
