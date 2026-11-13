# Acceptance runner: Cursor

To prepare a run, clone the public repository at the Tool version under test (`git clone --branch v<VERSION> …`), open that clone in Cursor, start a plain Agent chat on Sonnet (outside the Jenny mode) and type: "Follow `acceptance/runner/cursor.md` to prepare a Cursor bench run". That chat is the **grading chat** below; keep it open for the whole run.

The **Cursor bench** is the few checks that prove a published Tool version works on Cursor: those flagged `cursor-bench: true`, each run once. It runs after publishing, from a public clone at `v<VERSION>`, so it tests exactly what Operators get. It is not a gate run and never decides publication: the Claude Code gate run did that before publishing.

The Operator types each check's script into a fresh chat in the Jenny mode, so the mode itself is under test, and the grading chat prepares the run and grades it. Every grade is still a shell command it types.

Checks, keys, variables and the results shape are those in [claude-code.md](claude-code.md) and [check-format.md](check-format.md). What differs on Cursor:

- Only checks flagged `cursor-bench: true` run, each once, and every one except an `EN` check runs through the Jenny mode.
- No early stop: every check run in scope is made, whatever fails.
- `$SK` is `$WS/.cursor/skills`.
- An **Engineer repo** check (an `EN` check) has no install and no Jenny mode: the grading chat lays its fixture as claude-code.md step 1 says, and the Operator opens `$WS` and types the turns into a plain Agent chat on Sonnet, as the engineer. Its `steps.md` says so in place of the install message.
- "Nothing written" at proposal is graded from the state file the Operator saves after each reply (step 4), because by grading time the run has gone on past that turn.

## 1. Prepare (grading chat)

1. Pick the checks: scope `bench` is every check whose front matter says `cursor-bench: true`, each run once (`repeat-at-gate` is ignored). The Operator may name a narrower scope instead, a bench check's ID or one of its skills, which picks from those same flagged checks only. Name the run `<YYYY-MM-DD-HHMM>-<scope>` and make `$RUN` as in claude-code.md **Pick the checks**. EN-01 runs once, in a plain Agent chat with no Jenny skills (below).
2. For each check run, do claude-code.md **Copy the sample**, with `SK="$WS/.cursor/skills"`, and save `$SAMPLE` to `$D/sample-sha`.
3. Write `$D/steps.md` for the Operator, with every path filled in:
   - the folder to open: `$WS`;
   - the install message: `Follow <REPO>/skills/setup/SKILL.md to install Jenny in this folder. I use Cursor.`;
   - the check's turns, numbered, word for word, with each `<paste: <file>>` replaced by that fixture's full text so the Operator can copy it, and, for each MCP stand-in, claude-code.md's **MCP stand-in sentence** in brackets before turn 1, with the fixture copied to `$D/fixtures/` and its absolute path written out;
   - the state command to run after each reply, with the absolute paths written out (the Operator's terminal has no `$WS` or `$TURNS`) and `<n>` the turn just answered: `{ git -C "<WS>" status --porcelain --untracked-files=all; git -C "<WS>" rev-parse HEAD; } > "<TURNS>/<n>.state"`.

Done when: every check run has its `ws/` with one commit and a `steps.md`, and the Operator has the list of `steps.md` paths.

## 2. Install (Operator)

For each check run, open its `ws/` in a new Cursor window, start a plain Agent chat on Sonnet, and send the install message. Answer the install's questions as an Operator would and confirm with "Yes, go ahead." The first time, make the Jenny mode from the settings the install hands on (also in `skills/jenny/mode.md`). Then tell the grading chat `installed <ID>-<n>`.

## 3. Grade the install (grading chat)

Grade every line of claude-code.md's **Install key**, with these lines in place of their Claude Code ones:

- One runtime folder. `test -e "$WS/.claude" && echo yes` → empty; `test -e "$WS/CLAUDE.md" && echo yes` → empty.
- `AGENTS.md` markers and whole block: the two `grep -c` lines and the `diff` on `AGENTS.md` only.
- `workspace.md` settings: `grep -cx 'Runtime: cursor' "$WS/workspace.md"` → `1` in place of the `claude-code` line.
- MCP config: the same two lines on `$WS/.cursor/mcp.json`.

A failed line fails the check run as "install"; tell the Operator to skip that check run. Otherwise do claude-code.md **After install** (its changes, then `$BASE`), save `$BASE` to `$D/base-sha`, and tell the Operator to run the script.

Done when: the install is graded, and on a pass `$D/base-sha` exists.

## 4. Run the script (Operator)

In the check run's window, start a new chat in the Jenny mode. Type turn 1 word for word. After each of Jenny's replies, and before the next turn, copy the reply (the message's copy button) into `turns/<n>.md` and run the state command from `steps.md` in the terminal. If a reply could not be copied, export the whole chat as Markdown to `transcript.md` beside `ws/` once the last turn is done. Then tell the grading chat `ran <ID>-<n>`.

## 5. Grade the script (grading chat)

1. For any turn without a `$TURNS/<n>.md`, take that reply from `$D/transcript.md`, word for word, without the Operator's turns, tool calls or thinking, and note in the results that it came from the transcript.
2. Grade **Key at proposal** and **Key at write** as claude-code.md **Grade**. A "Nothing written" line at proposal passes when `$TURNS/<n>.state` is exactly one line, equal to `$BASE`.
3. Write `$REPO/acceptance/runs/<run>/results.md` in the shape claude-code.md **Write the results file** shows, with `Runtime: cursor · Model: sonnet · Prompt: Jenny mode`. Type it from your grades; the section files and the run rules there are for Claude Code runs.
4. After the summary and the results file's path, print the **results block** below in a fenced block, as the last thing in the reply.

A check run passes, with or without soft failures, as claude-code.md step 2 says. The bench passes when no row is `fail`. Each soft failure is ticketed and doesn't count against the bench; each hard failure is ticketed and means a new Tool version: land the fix, run the Claude Code gate again, publish again.

Done when: every check run has a pass, `pass · soft <n>` or fail with its graded lines recorded, and the Operator has the summary, the results file's path and the results block.

### Results block

A few lines short enough for the Operator to retype by hand elsewhere, exactly in this shape:

```
jenny cursor bench 2026-11-20-1430
tool 0.15.0 sample 7
runs 5 pass 3
fail MD-02 P3 P4
fail SU-01 I5
soft SU-02 P5
```

- Line 1: `jenny cursor <scope> <run date-time>`, the run's name split at its scope.
- Line 2: `tool <$REPO/VERSION> sample <sample version>`.
- Line 3: `runs <check runs> pass <passing check runs>`, a `pass · soft <n>` run counted as passing.
- One line per check run with any failed key line, in check ID order: `fail` when a hard line failed, `soft` when only `(soft)` lines failed; then the check ID; then each failed key line, hard and soft, as its section letter and its position in that section, counting key bullets from 1: `I` Install key (claude-code.md's numbering), `P` Key at proposal, `W` Key at write. A failed `I` line is an install failure, so its `fail` line holds only `I` lines.

A run with no failed line is the three header lines alone. Every other fact (check versions, actual outputs, By eye notes, transcript-sourced replies) stays in the results file.
