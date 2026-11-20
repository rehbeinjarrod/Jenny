---
name: plan
description: Delivery Plans and Forecasts for one Project. Use for `/plan`, when the Operator says "make a plan for <Project>", asks when a Milestone or Epic will land, says a Plan version went to someone, or asks what has moved since the last plan.
---

# Plan

Four operations: **When** and **Drift**, which write nothing, and **Make a plan** and **Shown**, each one confirm-then-write operation following the rules in the Tool-owned block of `AGENTS.md`. Today is `date +%F`.

## Words used here

- **Forecast script**: `<skills>/plan/scripts/forecast.py`, run as `python3 <skills>/plan/scripts/forecast.py projects/<slug> <plan folder>`. It reads the Project's Epics, `Depends on` lines and Milestones from the records, and the rest from `<plan folder>/inputs.json`, then writes `<plan folder>/forecast.json` and the Gantt drawn from it. The plan folder must be named `plan-v<N>`: N is the seed.
- **Gantt**: the Mermaid chart the Forecast script writes beside `forecast.json` once any Epic is dated: `gantt.mmd`, or above 20 dated Epics a chapter per Milestone, `gantt-<MIL ID>.mmd` (and `gantt-other.mmd` for Epics in no Milestone). The script reads each one back against `forecast.json` before writing it, so a Gantt is quoted whole, as the script wrote it, and never drawn or edited by hand. `python3 <skills>/plan/scripts/forecast.py --check <plan folder>` checks a folder's Gantts against its `forecast.json`: exit 0 when they match.
- **Quote**: every date and share you give, in chat or in a view, is copied from `forecast.json` as it stands, or in chat from the Drift script's output. A date not in them (or typed by the Operator) never appears. You never add, subtract, average or round a date, and never work one out from Throughput yourself, even roughly. A share is shown as a whole percent (`0.8512` is `85%`); that is the only change you make to a number.
- **Likely** is a `likely_finish` (half the trials finished by then); **very likely** is a `very_likely_finish` (85 in 100). Dates are Fridays.
- **Undated**: an Epic or Milestone whose `no_date` is not `null`. Its `no_date` says why.
- **No-count Epic**: an undated Epic whose `no_date` starts `no Story count`. Only engineers can fix it, by giving a low to high Story count range.
- **Critical**: an Epic with `critical_share` of `0.5` or more.
- **Plan folder**: `projects/<slug>/plans/plan-v<N>/`, holding `inputs.json`, `forecast.json`, its Gantt files, `stakeholder-view.md`, `operator-view.md` and `plan.md`. It is frozen once committed: the Guard rejects any later change but one, a `Shown:` line appended to `plan.md`. A new Plan is a new N, made only when the Operator asks.
- **Plan record**: `plan.md`, from [templates/plan-record.md](templates/plan-record.md), then one `Shown: <YYYY-MM-DD> to <who>` line for each time the version went out.
- **Drift script**: `<skills>/plan/scripts/drift.py`, run as `python3 <skills>/plan/scripts/drift.py projects/<slug> <plan folder>`. It compares the plan folder with the latest earlier version whose `plan.md` has a `Shown:` line, and prints the date moves per Milestone and Epic and what changed in the inputs, or one line saying no version was shown. It writes nothing. Quote its output whole, changing only Delivery terms to shown names; exit 2: say what could not be read.
- **Target setter**: the name after `set by` in a Milestone's `Target:` line. A `derived from plan-v<N>` target has none: its date is the very likely date that Plan version gave the Milestone, worked out by the Forecast script, never typed.

## Jira

When the Operator asks for Throughput read from Jira, in the request or in reply to the offer in **Make a plan**, read [jira.md](jira.md) whole and follow it alongside **Make a plan**: it gives the Throughput, the handed-off Epics' Story counts and their source.

## When

Runs when the Operator asks when a Milestone or Epic will land.

Find the one Project as the Lookup rules say. The latest Plan is the highest N under `projects/<slug>/plans/`.

- With a Plan: read its `forecast.json` and answer from it alone, quoting the Milestone's or Epic's target, likely and very likely dates and its chance of meeting the target, or its `no_date` reason. Name the Plan version (`plans/plan-v<N>/`) and its `start`, and offer a new Plan if the Operator has newer Throughput.
- With none: the reply is these three things, in this order:
  1. The words "There is no Plan yet", and that without a Plan there are no forecast dates.
  2. The Milestone's own target and who set it, as its record states, if it has one. That target is the reply's one date.
  3. An offer to make a Plan, naming in general terms what **Make a plan** needs: weekly Throughput (Stories finished each week, by the Monday of the week, 5 or more weeks), and the open and done Story counts of each handed-off Epic.

  Every other fact in the records waits for the Plan.

Done when: the reply quotes only `forecast.json`, or is just those three things. Nothing is written.

## Make a plan

Runs on "make a plan for <Project>", or when the Operator gives Throughput after **When** offered a Plan.

1. **Gather.** Find the one Project as the Lookup rules say, and work in its folder only. Read `project.md` (People), every `epics/*/epic.md` (an Epic with a `Tech face:` line under `## External items` is handed off) and every `milestones/*.md`. N is one more than the highest `plans/plan-v<N>` folder, or 1.

   From what the Operator typed, hold:
   - **Throughput**: each week's Monday (`YYYY-MM-DD`) and Stories finished. Missing it: when a handed-off Epic's `Tech face:` is a Jira link, or `project.md` links the team's Jira project, offer to read it and the Story counts from the team's Jira project, or to have them typed; otherwise ask for it. Stop here until it comes.
   - **Story counts** of each handed-off Epic: open and done, read today.
   - **Ranges**: an engineer's low and high Story count for an Epic.
   - **Finished Epics**: Story counts of Epics the team already finished, if given.
   - **Start**: as typed, or by default the Monday after today: `python3 -c "import datetime as d;t=d.date.today();print(t+d.timedelta(days=7-t.weekday()))"`.
   - **In flight**: how many Epics the team works on at once, as typed, or 2.

   Ask for nothing else: an Epic with no count and no range is left for the Forecast to mark undated.

   Done when: you hold N, the Throughput weeks, and a start and in-flight value with whether each is a default.

2. **Forecast** in a scratch folder outside the Workspace, so the Workspace stays untouched until the Operator confirms: `python3 -c "import tempfile;print(tempfile.mkdtemp(prefix='jenny-plan-'))"`, then make `<scratch>/plan-v<N>/` and write `<scratch>/plan-v<N>/inputs.json`:

   ```json
   {
     "throughput": {"from": "typed by <Operator's name>, <today>",
                    "weeks": [{"week": "<Monday>", "done": <Stories>}]},
     "finished_epics": [{"key": "<Jira key or name>", "stories": <n>}],
     "epics": {"<handed-off EPC ID>": {"open": <n>, "done": <n>, "read": "<today>"}},
     "ranges": {"<EPC ID>": {"low": <n>, "high": <n>}},
     "start": "<start>",
     "in_flight": <in flight>
   }
   ```

   Weeks oldest first; an empty list or object where nothing was given. Run the Forecast script on `projects/<slug>` and `<scratch>/plan-v<N>`:
   - **Exit 0**: read `<scratch>/plan-v<N>/forecast.json` whole, and list the Gantt files beside it.
   - **Exit 1**: each stderr line is one problem. One naming `inputs.json` is yours: fix the file and run again. One naming a record is the Operator's: tell them the file, line and what it needs, in plain words, and stop. One starting `gantt` is the Tool's: tell the Operator the chart came out unlike the Forecast, quote the line, and stop. Nothing is written.
   - **Exit 2**: say what could not be read, from stderr, and stop.

   When every Epic's `no_date` is about Throughput history, there are no dates to show. Say why, and stop with no batch. The reply holds no date but those the Operator typed: no start date, no record's date, and no week you name yourself, earlier or later.
   - `history.status` is `too short`: say how many weeks of history the Forecast counted (`history.weeks`), that it needs 5 or more, and ask for the weeks before the ones given, without naming their dates.
   - Otherwise no Stories were finished in the weeks counted: say so, and ask the Operator to check the Throughput they typed.

   Then run the Drift script on `projects/<slug>` and `<scratch>/plan-v<N>`, and hold its output.

   Done when: `forecast.json` exists in the scratch folder with at least one dated Epic and you hold the Drift script's output, or you have stopped and said why.

3. **Write the views** in the scratch folder, `<scratch>/plan-v<N>/stakeholder-view.md` from [templates/stakeholder-view.md](templates/stakeholder-view.md) and `operator-view.md` from [templates/operator-view.md](templates/operator-view.md). They are read outside the Workspace, so they use shown names throughout. Every date, share and reason is quoted from `forecast.json`; `Depends on`, `Enables:` and pain points come from the `epic.md` files. Each Gantt goes into the views as the template's `mermaid` block, its text copied from the file whole (`cat` it), and the Operator view's Lucid steps come from [lucid.md](lucid.md), once per Gantt file. Run each view through the Veneer scan as `AGENTS.md` says for a reply, and reword until it exits 0.

   Write `<scratch>/plan-v<N>/plan.md` from [templates/plan-record.md](templates/plan-record.md), with no `Shown:` line.

   Done when: `plan.md` and both views exist, every date in the views is in `forecast.json` (`grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' <view> | sort -u` against the same over `forecast.json`), each `mermaid` block is byte for byte its Gantt file, the Operator view has the Lucid steps for each Gantt file, and each view passes the Veneer scan.

4. **Questions.** For each no-count Epic, one Question for the engineers asking for a low to high Story count range, from the `capture` skill's Question template: title "How many Stories will <EPC ID> <title> take, as a low to high range?", `Status: open`, `Impact: 3` (every Milestone holding it has no date), `Uncertainty: 3` (nobody has sized it), `Score: 9`, `Score reason: <EPC ID> has no Story count, so the Forecast gives it and every Milestone holding it no date.` (canonical terms), `Needed by: <EPC ID>`, `Building on a guess: no`, `Affects:` the Milestone IDs it is a member of, `Raised from: plans/plan-v<N>`. Skip an Epic that already has an `open` or `chasing` Question with `Needed by:` that Epic raised from a Plan, and name that Question instead. New IDs follow the highest `-Q-` in the Project.

   For each Milestone whose `target_met_share` is under `0.5` and whose target has a Target setter, one Question for that Stakeholder: title "Will <setter> move the <target> target for <MIL ID> <name>, or cut its scope?", `Status: open`, `Impact: 3` (the target is likely missed), `Uncertainty: 3` (only the setter can choose), `Score: 9`, `Score reason: <MIL ID> has a <share as a whole percent> chance of meeting its <target> target in plan-v<N>, so its date or scope must change.`, `Needed by: <MIL ID>`, `Building on a guess: no`, `Affects: <MIL ID>`, `Raised from: plans/plan-v<N>`. Skip a Milestone that already has an `open` or `chasing` Question with `Needed by:` that Milestone raised from a Plan, and name that Question instead. A derived target raises none: say so in the batch.

   Done when: each no-count Epic and each such Milestone has a new Question or names an open one.

5. **Propose** under the heading "Plan v<N> for <Name>":
   1. `plans/plan-v<N>/inputs.json`: the Throughput weeks, counts and ranges, and the start and in flight, each marked "default" where it is one, so the Operator can change it.
   2. `plans/plan-v<N>/forecast.json` and each Gantt file by name: the Forecast script's output, written by the script.
   3. `plans/plan-v<N>/stakeholder-view.md`, shown in full.
   4. `plans/plan-v<N>/operator-view.md`: what it adds to the Stakeholder view.
   5. `plans/plan-v<N>/plan.md`, shown in full.
   6. Each new Question, then `questions/index.md` with its rows.
   7. `index.md`: a line linking the Plan's views.
   8. Log entry `## [<date>] plan | plan-v<N> <Project name>`, one line per file written.
   9. One commit.

   Then **Since the last shown Plan**: the Drift script's output, quoted. Then "Nothing is written yet."

   An amend to the inputs (a count, a range, the start, in flight) changes `inputs.json` in the scratch folder: run the Forecast script again (step 2), redo steps 3 and 4 from the new `forecast.json`, and show the batch again in full. The dates are only ever the script's.

   Done when: the batch is shown, ending with "Nothing is written yet."

6. **Confirm, write, log, commit** as `AGENTS.md` says. Copy every file in the scratch folder's `plan-v<N>/` into `projects/<slug>/plans/plan-v<N>/` as it is (`cp`), so `forecast.json` and the Gantt files are byte for byte the script's. Write the Questions, `questions/index.md` and `index.md`, and the log entry. Then delete the scratch folder.

   Done when: one commit whose message is the log heading, adding the Plan folder's files (`inputs.json`, `forecast.json`, each Gantt file, both views and `plan.md`), any Questions with their index rows, `index.md` and the log.

7. **Report**: as `AGENTS.md` says, with one line per Milestone quoted from `forecast.json` (likely, very likely, and chance of meeting its target), each undated Epic with its reason and Question, each missed-target Question, and that the Plan is frozen: a change in Throughput or counts means a new Plan. End by asking the Operator to say when the Plan goes out, and to whom, so the next Plan's drift is measured against it.

   Done when: the report is sent.

## Shown

Runs when the Operator says a Plan version went out: "plan-v<N> went to <who>", "I showed the plan to <who>".

1. **Gather.** Find the one Project as the Lookup rules say. The version is the one named, or else the latest; when the Operator's words could mean another, ask which. Hold who it went to, in the Operator's words, using a name from People where one matches, and the date: today, or the day the Operator gives. A version with no `plan.md` was made before Shown existed: say it can't be marked, and stop.

   Done when: you hold the version, who and the date.

2. **Propose** under the heading "Shown plan-v<N>":
   1. `plans/plan-v<N>/plan.md`: one line appended at the end, `Shown: <date> to <who>`. Every other line stays as it is.
   2. Log entry `## [<date>] plan | Shown plan-v<N> to <who>`, one line for `plan.md`.
   3. One commit.

   Then "Nothing is written yet."

   Done when: the batch is shown, ending with "Nothing is written yet."

3. **Confirm, write, log, commit** as `AGENTS.md` says, appending with `printf '%s\n' 'Shown: <date> to <who>' >> <plan.md>`. The Guard allows this one change to a committed Plan folder.

   Done when: one commit whose message is the log heading, and `git diff HEAD~1` shows only the `Shown:` line added to `plan.md` and the log entry.

## Drift

Runs when the Operator asks what has moved since the last plan, or since Stakeholders last saw one.

Find the one Project as the Lookup rules say. With no Plan, say there is no Plan yet and offer **Make a plan**. When the latest Plan has a `Shown:` line itself, say it is the Plan last shown, so nothing has moved: dates move only with a new Plan, which you offer. Otherwise run the Drift script on `projects/<slug>` and the latest Plan's folder and quote its output.

Done when: the reply quotes the Drift script's output, or says why there is none. Nothing is written.
