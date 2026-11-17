# Acceptance runner: Claude Code

To start a run, open Claude Code on your Jenny clone and type: "Follow `acceptance/runner/claude-code.md` and run acceptance for `<scope>`", where `<scope>` is a skill name, a check ID, or `gate` for a gate run. A gate run is headless only (**Gate run, headless** below).

Runs checks from `acceptance/checks/` against scratch copies of the sample Workspace in `acceptance/sample/`, with the Tool installed through `setup`'s normal install path. The check file shape is in [check-format.md](check-format.md).

This file is the Claude Code runner. The Cursor bench, where the Operator types each bench check's script into the Jenny mode and a separate grading chat grades it, follows [cursor.md](cursor.md) instead, using this file's keys and results shape.

## Checks, headless

Every check runs unattended from a shell, graded from its own key lines as written ([check-format.md](check-format.md) **Headless grading**), with no orchestrating session. The scope is one or more check IDs or skill names, as for a scoped run:

```bash
export CLAUDE_CODE_OAUTH_TOKEN=<from `claude setup-token`>   # or ANTHROPIC_API_KEY
python3 acceptance/headless/run_check.py CP-01 --model <exact model ID> --runs 3
python3 acceptance/headless/run_check.py capture --model <exact model ID>
```

It follows this file's steps with the headless driver in place of the two subagents. Install and Jenny are each a top-level `claude -p` session in a scratch Workspace outside the clone, each with a fresh `CLAUDE_CONFIG_DIR` and only the token from your environment, so none of your own settings, memory, skills or login are read. No session reaches an MCP server (`--strict-mcp-config`). After the Install key, the check's change after install (its Start's `sh` block) is made, and HEAD is `$BASE`. A **No install** check has no install session: its Start's `sh` block is made over the committed sample instead, and an **Engineer repo** check's in an empty folder; either way its commit is `$BASE`, and `<REPO>` in a turn is the clone's path. Each turn is sent word for word, through `--resume` after the first, and the reply saved is everything Jenny wrote in that turn. A check whose `skills` list names `jenny` runs in the Jenny mode: the mode's instructions from [mode.md](../../skills/jenny/mode.md), pointed at `.claude/skills/jenny/SKILL.md`, are appended to Jenny's system prompt on every turn, as Cursor's mode carries them, and the turns still go word for word. An **Engineer repo** check's session gets the **Engineer prompt** below appended instead, up to its relay sentence (the turns go word for word), and the header's Prompt names it. Each **MCP stand-in** is set in `$D/fixtures/`, and its **MCP stand-in sentence** below is appended to Jenny's system prompt on every turn. The driver grades every key line, and the Veneer scan line records what the scan finds on every reply without grading it. After turn 1, the session transcript must show the Workspace's `CLAUDE.md` and `AGENTS.md` (in an engineer's repo, which has no `CLAUDE.md`, neither is looked for) and its skills loaded, and nothing from outside the Workspace, or the check run is Void. Voids and hard stops work as below; a fail never stops the run. The results file (`Driver: headless`) lands in `acceptance/runs/<run>/results.md` and is copied to `acceptance/results/`, where `plan.py` counts it. Exit 0: every check run passed. Exit 1: one failed. Exit 2: a hard stop.

### Gate run, headless

```bash
python3 acceptance/headless/run_check.py gate --model <exact model ID>
```

A gate run makes only the check runs the gate plan asks for ([check-format.md](check-format.md) **The gate plan**), weighing every results file in `acceptance/results/` (`--results <folder>` for another; `--published none` turns carry-over off). When the plan needs none, it makes none and reports pass. Checks go in check-ID order, each check's runs back to back; after each check run the planner weighs that check again, so a `fail` gets 3 more runs of its check, and a check stops once the planner needs no more runs of it, or once it blocks, since more runs can't lift a block. A fail never ends the run: every other check still gets its runs. Voids and hard stops work as for any headless run; on a hard stop, every run the plan still needed gets a `not run` row.

After its table, the results file holds the **gate report**: the gate plan as it stands with this run's rows counted, giving each check's verdict at its Fingerprint (`pass`, `flake` or `block`), its pass rate across every Fingerprint on the same runtime, driver and model with a 95% Wilson interval, one `Flake: <ID> at <Fingerprint>, fail in <results file>` line per flake, one `Block: <ID> at <Fingerprint>, <fails> in <runs>, in <results files>` line per block, and the overall verdict as `Gate: pass` or `Gate: block`. A flake passes the gate. A run ended by a hard stop has no report. Exit 0: the gate passed. Exit 1: it blocks. Exit 2: a hard stop.

The rest of this file is the subagent driver, for scoped runs.

`$REPO` below is the root of the Jenny clone you're running from (absolute path). `$RUN` is the run folder, `$REPO/acceptance/runs/<run>`. `$SK` is the scratch Workspace's skills folder: `$WS/.claude/skills` on Claude Code.

## Rules of a run

Where a rule says stop, stop then and there, and finish the run as that rule says.

- **Sonnet under test, one session.** Jenny and the install agent run on Sonnet (`model: sonnet` on each subagent, step 2), since replies from any other model are not acceptance evidence. The session following this file orchestrates and grades on any model, and makes every check run itself.
- **Two subagents only.** The only subagents you start are the install agent and Jenny (step 2), each with `model: sonnet`. Never hand a check run, its grading or its results to any other subagent.
- **You grade.** Every grade is a shell command you type in this session, never a script file and never a subagent's report.
- **One at a time.** Start a check run only once the one before it has its section file on disk (step 2.6). Start each subagent in the foreground and wait for its reply (or, where the Agent tool runs it in the background, its completion notice) before doing anything else, so only one subagent is ever working.
- **On disk as it goes.** Each check run's row and section are written to `$RUN/sections/` the moment it is graded, and the results file is put together from those files (step 3). After a compaction, the session picks the run up from `$RUN` (**Picking a run up** below).
- **Evidence only.** A run grades the Tool version the clone holds when it starts, and never edits the clone: everything it writes goes inside `$RUN`. When a check run fails, record it and carry on, leaving every skill, check, fixture and sample as it was. A fix is a new Tool version, with a run of its own.
- **Fixtures only.** A live run against a real Atlassian site is not acceptance evidence; see **MCP stand-in sentence**.
- **Voids.** A check run is `void` when something outside Jenny and the check spoiled it: a subagent returned an error instead of a reply, or stopped mid-turn on a usage, rate or context limit; or this session made a slip of its own in running it (a turn sent wrong, a fixture laid wrong). A Veneer scan that couldn't run is recorded, never a void. Anything Jenny wrote or said is graded, never voided, however odd. A void is graded neither pass nor fail, and is rerun once, straight after it, from step 2.1 in a fresh folder (`$D` is `$RUN/<ID>-<n>-r<k>` for its `k`th rerun). A rerun that voids is itself a void: it counts toward the **fourth void** hard stop and, below that, is rerun once in turn.
- **Order.** Check runs go in check-ID order, and a check's repeats run back to back. A failed check run never ends a run.
- **Hard stops.** Any run, gate or scoped, stops at once, with no verdict, on the first of these:
  - **fourth void**: a fourth `void` row in the run;
  - **clone changed**: the clone-state comparison below prints anything;
  - **run budget**: the check runs made (rows other than `not run`) already equal the lines of `plan.md` plus 3, and another would be started. With one rerun per void and the fourth void a hard stop, this fires only on a miscount: it is the backstop.

  Check them before each check run and once more at the start of step 3. On one, write the `Verdict: none` line (step 3), with the hard stop's name, as the last line of `$RUN/header.md`, give every check run still to make a `not run` row (a void left without its rerun included), and go to step 3.

### Clone state

This prints one line that changes if the clone's commit, tracked files or untracked files change. The run folder is gitignored, so it isn't counted. Step 1 saves its output:

```bash
(cd "$REPO" && { git rev-parse HEAD; git status --porcelain --untracked-files=all; git diff HEAD --binary; git ls-files -z -o --exclude-standard | xargs -0r sha1sum; } | sha1sum) > "$RUN/clone-state"
```

The comparison prints nothing while the clone is unchanged:

```bash
diff <(cd "$REPO" && { git rev-parse HEAD; git status --porcelain --untracked-files=all; git diff HEAD --binary; git ls-files -z -o --exclude-standard | xargs -0r sha1sum; } | sha1sum) "$RUN/clone-state"
```

### Picking a run up

After a compaction, read `$RUN/plan.md`, `$RUN/header.md` and the first line of every file in `$RUN/sections/`. If `header.md` already ends with a `Verdict: none` line, finish the `not run` rows and go to step 3. Otherwise the next check run is the first line of `plan.md` whose `<ID>` and `<n>` have no section file, or whose newest section file is a `void` row (its rerun is next). A check run cut off before its section file was written starts again: delete its `$D` and begin at step 2.1. Count voids and check runs made from the section files' rows, then carry on from step 2.

## 1. Pick the checks

- "run acceptance for `<skill>`": every check whose `skills` list names it.
- "run acceptance for `<ID>`": that check.
- "… through the mode": the same checks, each run with the Mode prompt below instead of the Workspace prompt. A check whose `skills` list names `jenny` always runs that way.

Name the run `<YYYY-MM-DD-HHMM>-<scope>` and make `$RUN` with a `sections/` folder in it. Everything the run writes goes inside `$RUN`, which is gitignored, so the clone's `git status` stays as it was. Then write, before any check run starts:

- `$RUN/clone-state`: the output of the **Clone state** command.
- `$RUN/plan.md`: the check runs in **Order**, one per line as `<ID> <check version> <n>`.
- `$RUN/header.md`: the results file's title and header lines (step 3), with `Tool version` from `$REPO/VERSION` now.
- `$RUN/fingerprints`: each planned check's Fingerprint, one `<ID> <Fingerprint>` per line, from `python3 "$REPO/acceptance/gate/fingerprint.py" <ID> --driver subagent --model <model>`, where `<model>` is the exact model ID the subagents' `sonnet` runs (never the alias).

Done when: those files exist and `plan.md` lists every check run (check ID × repeat).

## 2. Run each check

For each line of `plan.md` in turn, check run `<ID>-<n>`, one at a time: first check the **Hard stops**, then

1. **Copy the sample.** Set `D="$RUN/<ID>-<n>"` (`$RUN/<ID>-<n>-r<k>` for a rerun), `WS="$D/ws"`, `SK="$WS/.claude/skills"`, `TURNS="$D/turns"`. A check whose Start says **Engineer repo** has no sample: `mkdir -p "$WS" "$TURNS"`, run its Start's `sh` block, which lays its fixture into `$WS` and commits it, and skip to step 4 with that commit as `$BASE`. Otherwise: `mkdir -p "$WS" "$TURNS" && cp -r "$REPO/acceptance/sample/." "$WS/"`. Set the check's Start fixtures beside it in `$D/fixtures/`. Then `git -C "$WS" init -q && git -C "$WS" add -A && git -C "$WS" commit -qm "Sample v<sample version>"` and note that commit as `$SAMPLE`.
2. **Install.** A check whose Start says **No install** skips this step and its Install key: run its Start's `sh` block, which lays its fixture over the sample and commits it, and note that commit as `$BASE`. Otherwise, start a fresh subagent (Agent tool, `model: sonnet`) with the install prompt below, then confirm its proposal through `SendMessage` with `The Operator says: "Yes, go ahead."` Answer any other question it asks as an Operator would, from the facts in the prompt. Grade every line of **Install key** below. On a failure, the check run fails as "install": go to step 6.
3. **After install.** With an install, make any change the check's Start says comes after install, and commit it with the message it gives. Then note `$BASE`: `git -C "$WS" rev-parse HEAD`.
4. **Run the script.** Replace each `<paste: <file>>` in a turn with the full text of that fixture (`cat "$REPO/acceptance/fixtures/<file>"`), line breaks kept. For each **MCP stand-in** in the check's Start (its fixture set in `$D/fixtures/` in step 1), add the stand-in sentence below to the prompt, after `change nothing outside it.` Start a second fresh subagent (`model: sonnet`) with the Workspace prompt below (the Mode prompt, or for an **Engineer repo** check the Engineer prompt) and the check's turn 1. Send each later turn word for word through `SendMessage` to that same subagent, framed as `The Operator says: "<turn>"` (`The engineer says:` under the Engineer prompt) so the subagent reads it as the Operator's words. Under the Mode prompt, put `(Jenny mode: read <WS>/.claude/skills/jenny/SKILL.md whole before anything else.)` before the framing, as the Cursor mode does each turn. Save each of Jenny's replies, exactly as returned, to `$TURNS/<turn>.md`, then record its **Veneer scan line** below before sending the next turn.
5. **Grade.** Grade **Key at proposal** after the turns it names, and **Key at write** after the last turn. Run each key line's command as written, with `$REPO`, `$WS`, `$SK`, `$BASE`, `$TURNS` set, and compare the output with the expected value. Record each line as pass or fail with the actual output. Read **By eye** against the replies and note what you see.

   Done when: every key line has its pass or fail, and every turn its **Veneer scan line**.
6. **Write its section.** Write `$RUN/sections/<NNN>-<ID>-<n>.md`, where `<NNN>` is the three-digit number of this check run in the run so far (`001`, `002`, …; a rerun takes the next number). Line 1 is its results row, with the check's Fingerprint from `$RUN/fingerprints`; then a blank line and its section, as in step 3, headed `## <ID> run <n>` (`## <ID> run <n>, rerun <k>` for a rerun). A `void` section says what spoiled the run. Then apply the **Hard stops** and **Voids**, in that order.

A check run passes when every Install key line (when it installs) and every key line passes. Done when: every line of `plan.md` has a section file whose row is `pass`, `fail` or `not run` (each `void` followed by its rerun's file), or the run has stopped and given the rest `not run` rows.

### Veneer scan line

Every check gets this line without carrying it, so a check never keys Veneer in chat itself. It is not a key line: it records what the scan found and never fails or voids a check run. After each turn's reply is saved, when `$WS/veneer.md` exists, run the Veneer scan from the Tool under test on that reply, from the Workspace so it reads the Veneer Jenny read:

```bash
(cd "$WS" && python3 "$REPO/skills/jenny/scripts/veneer_scan.py" < "$TURNS/<turn>.md")
```

Record one of these for the turn:

- Exit 0: `clean`.
- Exit 1: `hits: <line>: <word>, …`, its output's lines joined by `, `.
- Exit 2: `unreadable`: `veneer.md` can't be read.
- Any other exit, such as no `python3`: `not run`.

The section joins the turns with `; `, as in `Veneer scan: turn 1 hits: 1: Project; turn 2 clean`.

With no `veneer.md` after a turn, that turn has no Veneer scan line.

### MCP stand-in sentence

One per stand-in, with `<D>` filled in. Every check reads Jira and Confluence through its stand-ins, never a real Atlassian site.

> The Atlassian MCP is not connected in this session. When you would read `<URL>` through it, read `<D>/fixtures/<file>` instead: the MCP returned this file.

### Install prompt

> You are an AI assistant working for an Operator in the folder `<WS>`. Run every shell command from that folder (`cd <WS> && …`) and change nothing outside it. The Operator's later words reach you as relayed messages that begin `The Operator says:`; treat those as the Operator's own replies. The Operator says: "Follow `<REPO>/skills/setup/SKILL.md` to install Jenny in this folder. I use Claude Code."

### Workspace prompt

> You are Jenny, working for an Operator in the Workspace folder `<WS>`. Treat it as your project folder: read `<WS>/AGENTS.md` now and follow it as your project instructions. Your skills are the folders in `<WS>/.claude/skills/`: when a request matches a skill's description, read its `SKILL.md` and follow it. Run every shell command from the Workspace (`cd <WS> && …`) and change nothing outside it. The Operator's later words reach you as relayed messages that begin `The Operator says:`; treat those as the Operator's own replies. End every turn with your reply to the Operator, word for word as they will read it, and nothing else. The Operator says: "<turn 1>"

### Mode prompt

Stands in for the Jenny mode's instructions in [mode.md](../../skills/jenny/mode.md), pointed at the Claude Code skills folder.

> You are Jenny, working for an Operator in the Workspace folder `<WS>`. Treat it as your project folder: read `<WS>/AGENTS.md` now and follow it as your project instructions. At the start of every turn, before anything else, read `<WS>/.claude/skills/jenny/SKILL.md` whole and follow it. Run every shell command from the Workspace (`cd <WS> && …`) and change nothing outside it. The Operator's later words reach you as relayed messages that begin with the Jenny mode line, then `The Operator says:`; treat those as the Operator's own replies. End every turn with your reply to the Operator, word for word as they will read it, and nothing else. The Operator says: "<turn 1>"

### Engineer prompt

Stands in for an engineer's own coding agent: no Jenny skills, no Workspace, only the repo's `AGENTS.md`.

> You are a coding agent working for an engineer in the repo folder `<WS>`. Read `<WS>/AGENTS.md` now and follow it as your project instructions. Run every shell command from that folder (`cd <WS> && …`) and change nothing outside it. The engineer's later words reach you as relayed messages that begin `The engineer says:`; treat those as the engineer's own replies. End every turn with your reply to the engineer, word for word as they will read it, and nothing else. The engineer says: "<turn 1>"

### Install key

Every line expects the output shown.

- Skills copied. `diff -r -x VERSION "$REPO/skills" "$SK"` → empty.
- Version copied. `cmp "$REPO/VERSION" "$SK/jenny/VERSION"` → empty.
- One runtime folder. `test -e "$WS/.cursor" && echo yes` → empty.
- `AGENTS.md` markers and whole block. `grep -c '^<!-- jenny:begin -->$' "$WS/AGENTS.md"` → `1`; `grep -c '^<!-- jenny:end -->$' "$WS/AGENTS.md"` → `1`; `diff <(sed -n '/^<!-- jenny:begin -->$/,/^<!-- jenny:end -->$/p' "$WS/AGENTS.md") "$REPO/skills/setup/templates/agents-block.md"` → empty; `grep -cx '@AGENTS.md' "$WS/CLAUDE.md"` → `1`.
- `workspace.md` settings. Each → `1`: `grep -cx "Tool version: $(cat "$REPO/VERSION")" "$WS/workspace.md"`, `grep -cx 'Runtime: claude-code' "$WS/workspace.md"`, `grep -cx "Clone path: $REPO" "$WS/workspace.md"`, `grep -cx 'Outbound: outbox' "$WS/workspace.md"`, `grep -cx 'Sample version: .*' "$WS/workspace.md"`.
- MCP config, no secrets. `jq -e .mcpServers.atlassian "$WS/.mcp.json" >/dev/null && echo ok` → `ok`; `grep -ciE 'token|secret|password|api[_-]?key|bearer|authorization' "$WS/.mcp.json"` → `0`.
- Records untouched. `git -C "$WS" diff --name-only "$SAMPLE" HEAD -- projects veneer.md` → empty.
- The Guard is active. `H="$(git -C "$WS" rev-parse --absolute-git-dir)/hooks/pre-commit"`; `grep -c 'jenny:guard' "$H"` → `1`; `test -x "$H" && echo ok` → `ok`.
- One commit, clean tree. `git -C "$WS" rev-list --count "$SAMPLE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## 3. Write the results file

The results file is put together from the files in `$RUN`, never retyped. Unless the run already ended on a hard stop, check the **Hard stops** once more (a clone change ends the run here: write its `Verdict: none` line and go on). Then:

```bash
cd "$RUN" && { cat header.md; printf '\n| Check | Version | Run | Fingerprint | Result |\n| --- | --- | --- | --- | --- |\n'; for f in sections/*.md; do head -n 1 "$f"; done; for f in sections/*.md; do tail -n +2 "$f"; done; } > results.md
```

The results file's shape:

```markdown
# Acceptance run <run>

Date: <YYYY-MM-DD> · Runtime: claude-code · Driver: subagent · Model: <exact model ID> · Prompt: <Workspace prompt | Mode prompt>
Tool version: <VERSION> · Sample version: <from acceptance/sample/workspace.md> · Scope: <scope>

| Check | Version | Run | Fingerprint | Result |
| --- | --- | --- | --- | --- |
| SU-01 | 1 | 1 | 243431cfb08a | pass |

## SU-01 run 1

Install: pass
Key at proposal: <each line: pass | fail, with the actual output on a fail>
Key at write: <same>
Veneer scan: <each turn: clean | hits: <line>: <word>, … | unreadable | not run>
By eye: <notes>
```

Each row's Result is one of four forms:

- `pass`: every Install key line and key line passed.
- `fail`: a key line failed, or the install failed.
- `void`: the check run was spoiled by something outside Jenny and the check, graded neither pass nor fail. Its rerun gets its own row straight after it, with the same Check and Run.
- `not run`: a hard stop ended the run before this check run.

A run that ended on a hard stop has no verdict. Its header then carries one more line, after the `Tool version` line: `Verdict: none · Hard stop: <the hard stop that ended it>`.

A `not run` row is a section file holding only its row, numbered after the last check run made, in `plan.md` order.

Report the table to the Operator with the results file's path, how the run ended (it ran through, or which hard stop), and each `fail` row with its failed lines, one by one, for the Operator to file.

Done when: the results file exists with every line of `plan.md` in its table, and the Operator has the summary.
