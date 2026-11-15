# Check file format

One check per file at `acceptance/checks/<ID>-<slug>.md`. A check grades only what comes out of the Operator's conversation with Jenny: the replies in chat, the git diff after confirm, and files in `outbox/`. It never reads a skill file or template to learn what Jenny should have done; a key line may compare a Workspace's copy against the Tool's own (`$REPO/skills/…`, `$REPO/VERSION`).

## Front matter

```yaml
---
id: SU-01                # prefix + two digits, never reused
version: 1               # bump on any change to the script or keys
skills: [setup]          # skills the check exercises; drives scoped runs
cursor-bench: true       # true → in the Cursor bench (runner/cursor.md)
routing: false           # true → tests which skill picks up a request
inputs: []               # other Tool files the check reads, repo-relative, e.g. [CHANGELOG.md]
promise: false           # true → a Promise Check
---
```

`skills`, `inputs` and `routing` decide the check's Fingerprint (below), so a check names every Tool file it depends on through them.

Prefixes: `SU` setup, `CP` capture, `UN` up-next, `SL` slice, `PK` pack, `SO` signoff, `HO` handoff, `LK` lookup, `EN` engineer-side, `MD` the Jenny mode.

## Grader line

A check with a headless grader names it on one line between its summary and **Start**: ``Grader: `acceptance/headless/graders/<ID>.py`, …``. The grader holds the check's key lines and its Start's `sh` block as code, word for word (`AFTER_INSTALL`, or `LAY` for a **No install** or **Engineer repo** check); a key line that needs more than a shell line runs a script of the grader's own, in `acceptance/headless/graders/<ID>/`, so no key line is left to a model's judgement; `acceptance/headless/test_key_parity.py` fails when the two drift, so a change to a check's keys or Start is made in its grader in the same change.

## Sections, in this order

1. **Start**: the sample version (`Sample vN`), which fixtures to set beside the Workspace (from `acceptance/fixtures/`), any change to the sample before the run, any change after install (an `sh` block that makes it and commits it with its message, before `$BASE`), each **MCP stand-in** (`MCP stand-in: <URL> → <fixture>`: the fixture Jenny reads as what the Atlassian MCP returned for that URL; a check never reads a real Atlassian site), and the sample files (with the IDs in them) the key relies on. A check that starts from an older Workspace instead of a fresh install says **No install** and gives, as an `sh` block, the commands that lay its frozen fixture over the committed sample and commit it; that commit is `$BASE`. An `EN` check runs in an engineer's repo instead of a Workspace: it says **Engineer repo** and gives, as an `sh` block, the commands that make `$WS` from its fixture in an empty folder and commit it; that commit is `$BASE`, and its turns are the engineer's.
2. **Operator script**: numbered turns, typed word for word. Usually 2 (ask, confirm), sometimes 3 with one amend; 1 for a check that writes nothing, such as a lookup. `<REPO>` in a turn stands for the root of the Jenny clone (`$REPO`). `<paste: <file>>` in a turn stands for the whole text of `acceptance/fixtures/<file>`, pasted in its place word for word, as an Operator pastes material into chat.
3. **Key at proposal**: lines graded on the proposal replies, before confirm. Always includes "nothing written".
4. **Key at write**: lines graded after the confirm turn: commits, files changed and not changed, IDs and facts present and absent. A check that writes nothing grades it after its last turn, and it holds only the lines that prove nothing was written.
5. **By eye**: prose and tone notes. Read and noted in the results, never scored.

## Key lines

Each key line is a bullet: what it proves, then the shell command in a code span, then `→` and the expected output. Commands use these variables, which the runner sets:

- `$WS`: the scratch Workspace folder.
- `$BASE`: the commit `HEAD` pointed at after install, before turn 1.
- `$TURNS`: the folder holding each of Jenny's replies as `<turn>.md`.
- `$REPO`: the root of the Jenny clone you're running from.
- `$SK`: the scratch Workspace's skills folder (`$WS/.claude/skills` or `$WS/.cursor/skills`).

### Veneer in chat

Every key line is hard: one failed line fails the check run. A check never keys renamed canonical terms in Jenny's chat replies: the runner records the Veneer scan on every saved reply instead ([claude-code.md](claude-code.md) **Veneer scan line**), so a new check gets it for free. That line is not a key line and never fails a check run. A check may still key that a shown name appears. Veneer in records, IDs, files and `outbox/` text is still the check's to key.

Keys are written first, before the sample records they cite. Editing a sample file means bumping `Sample version:` in `acceptance/sample/workspace.md` and the version of every check whose Start names that file.

## Fingerprint

A check run's Fingerprint is what it tested. `acceptance/gate/fingerprint.py` is the one place that decides it, as 12 hex digits taken over:

- every file of each skill in `skills`, and each file or folder in `inputs`;
- the check file, every fixture it names by path (under `acceptance/fixtures/`), and `acceptance/sample/` unless its Start says **Engineer repo**;
- the runtime, the driver and the exact model ID, and for the headless driver its code (`acceptance/headless/*.py`, tests left out) and the check's own grader (`acceptance/headless/graders/<ID>.py`, with any scripts of its own in `acceptance/headless/graders/<ID>/`);
- for a check that installs Jenny (every check but an **Engineer repo** one), the shared parts: the Jenny core (`skills/jenny/`), the AGENTS block (`skills/setup/templates/agents-block.md`), install (`skills/setup/scripts/install.sh`), and the skill set;
- for a `routing: true` check, the skill set.

The skill set is which skills exist, with each one's `name` and `description`. So a body edit to one skill moves only the checks that name it, and an edit to any skill's description moves every check that installs Jenny or routes. `VERSION` is in no Fingerprint.

`python3 acceptance/gate/fingerprint.py <ID> --model <exact model ID> [--driver headless] [--runtime claude-code]` prints one.

## Results files

A results file's header names the exact model ID and the driver, and each row its Fingerprint:

```markdown
Date: <YYYY-MM-DD> · Runtime: claude-code · Driver: <driver> · Model: <exact model ID> · Prompt: <Workspace prompt | Mode prompt>
Tool version: <VERSION> · Sample version: <from acceptance/sample/workspace.md> · Scope: <scope>

| Check | Version | Run | Fingerprint | Result |
| --- | --- | --- | --- | --- |
| SU-01 | 1 | 1 | 243431cfb08a | pass |
```

The Model is the exact ID the runtime reports, never an alias such as `sonnet`. A headless run's Prompt is `none`: its turn 1 goes to Jenny as the Operator typed it, and a check's MCP stand-in sentences are appended to her system prompt instead. When the run holds checks in the Jenny mode, it reads `none, the Jenny mode for <IDs>`: the mode's instructions are appended to those checks' system prompt too. A results file without a `Driver:`, a `Model:` or a Fingerprint column is history and never counts.

## The gate plan

`python3 acceptance/gate/plan.py --model <exact model ID> [--driver headless]` reads every results file in `acceptance/results/` and the current tree, and prints each check's Fingerprint, counted runs, fails, runs still needed, verdict, and pass rate across every Fingerprint on the same runtime, driver and model with its 95% Wilson interval; then a `Flake:` line per flake naming the results file holding its fail, a `Block:` line per block with its fails and the files holding them, a `Needs runs:` line per check still needing runs, the runs needed in all and the gate's verdict. `--published-tree <folder>` with `--published <tag>` takes that tag's tree already extracted, for a root that is not a git checkout. A gate run makes the runs it needs ([claude-code.md](claude-code.md) **Gate run, headless**). The rules:

- every `pass` or `fail` row at the check's current Fingerprint counts, from any run; `void` and `not run` rows never do;
- a check needs 3 counted runs, or none when its Fingerprint is unchanged since the last published Tool version (the newest `v*` tag; `--published none` turns carry-over off);
- each fail asks for 3 more runs after it;
- 2 or more fails `block`; a Promise Check (`promise: true`) blocks on a fail confirmed by another in its 3 more runs;
- with runs still needed the verdict is `needs runs`; otherwise 1 fail is a `flake` and none a `pass`.

The gate is `block` if any check blocks, else `needs runs` if any needs runs, else `pass`. A flake passes the gate.
