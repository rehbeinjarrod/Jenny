# Check file format

One check per file at `acceptance/checks/<ID>-<slug>.md`. A check grades only what comes out of the Operator's conversation with Jenny: the replies in chat, the git diff after confirm, and files in `outbox/`. It never reads a skill file or template to learn what Jenny should have done; a key line may compare a Workspace's copy against the Tool's own (`$REPO/skills/…`, `$REPO/VERSION`).

## Front matter

```yaml
---
id: SU-01                # prefix + two digits, never reused
version: 1               # bump on any change to the script or keys
skills: [setup]          # skills the check exercises; drives scoped runs
cursor-bench: true       # true → in the Cursor bench (runner/cursor.md)
repeat-at-gate: false    # true → 3 runs in a gate run, all must pass
---
```

Prefixes: `SU` setup, `CP` capture, `UN` up-next, `SL` slice, `PK` pack, `SO` signoff, `HO` handoff, `LK` lookup, `EN` engineer-side, `MD` the Jenny mode.

## Sections, in this order

1. **Start**: the sample version (`Sample vN`), which fixtures to set beside the Workspace (from `acceptance/fixtures/`), any change to the sample before the run, any change after install (made and committed before `$BASE`, with the commit message), each **MCP stand-in** (`MCP stand-in: <URL> → <fixture>`: the fixture Jenny reads as what the Atlassian MCP returned for that URL; a check never reads a real Atlassian site), and the sample files (with the IDs in them) the key relies on. A check that starts from an older Workspace instead of a fresh install says **No install** and gives the commands that lay its frozen fixture over the sample, and the commit message that becomes `$BASE`. An `EN` check runs in an engineer's repo instead of a Workspace: it says **Engineer repo** and gives the commands that make `$WS` from its fixture, and the commit message that becomes `$BASE`; its turns are the engineer's.
2. **Operator script**: numbered turns, typed word for word. Usually 2 (ask, confirm), sometimes 3 with one amend; 1 for a check that writes nothing, such as a lookup. `<paste: <file>>` in a turn stands for the whole text of `acceptance/fixtures/<file>`, pasted in its place word for word, as an Operator pastes material into chat.
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

### Hard and soft

A key line is **hard** unless its bullet starts with `(soft)`, as in `- (soft) Never says a renamed canonical term …`. A **soft** line grades only Veneer words in Jenny's chat replies: every command in it reads `$TURNS` and nothing else, and every expected value is about canonical terms or Veneer names. Everything else stays hard, Veneer included: Veneer in records, IDs, files and `outbox/` text is hard, and so is a line that mixes a Veneer test with any other test. A failed soft line fails its check run softly: the run passes when every hard line passes, and its results row counts the soft failure (see the runner's results shape).

Keys are written first, before the sample records they cite. Editing a sample file means bumping `Sample version:` in `acceptance/sample/workspace.md` and the version of every check whose Start names that file.
