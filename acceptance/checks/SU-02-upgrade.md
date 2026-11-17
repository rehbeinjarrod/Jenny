---
id: SU-02
version: 11
skills: [setup]
cursor-bench: true
routing: false
inputs: [CHANGELOG.md]
promise: true
---

# SU-02 · Upgrade a Tool 0.2.0 Workspace to this version

A Workspace installed at Tool 0.2.0 holds the Operator's own text outside the `AGENTS.md` markers, an MCP entry they added, and a non-default `Outbound:`. The Operator has pulled the new version into the clone and asks Jenny to upgrade. Jenny proposes one batch that ends with the restart instruction, writes nothing until confirm, then upgrades in one commit and leaves every record and Operator setting as it was.

Tool 0.2.0 has no upgrade of its own, so the Operator points at the clone's `setup`, as the 0.4.0 CHANGELOG says to.

## Start

**No install.** Sample v7, with the frozen fixture `acceptance/fixtures/workspace-0.2.0/` laid over it as the Tool 0.2.0 install, after the sample is committed. The commit this makes, `[2026-11-11] install | Tool 0.2.0 for claude-code`, is `$BASE`:

```sh
cp -r "$REPO/acceptance/fixtures/workspace-0.2.0/." "$WS/" && mkdir -p "$WS/.claude" && mv "$WS/skills" "$SK" && sed -i "s|^Clone path: .*|Clone path: $REPO|" "$WS/workspace.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-11] install | Tool 0.2.0 for claude-code"
```

The key relies on: `workspace.md` (`Outbound: outbox`, and `Sample version: 3`, the frozen fixture's own line), `AGENTS.md` (the 0.2.0 block, then `## My notes` outside the markers), `.mcp.json` (the `atlassian` entry and the Operator's `calendar` entry), `$SK/setup/VERSION` (0.2.0's place for the copied version), and the records in `projects/` and `veneer.md`.

## Operator script

1. I've pulled the new Jenny into my clone. Follow <REPO>/skills/setup/SKILL.md to upgrade this Workspace.
2. Yes, upgrade it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`. `V="$(cat "$REPO/VERSION")"`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Names both versions. `grep -c '0\.2\.0' "$TURNS/1.md"` → 1 or more; `grep -cF "$V" "$TURNS/1.md"` → 1 or more.
- Shows the CHANGELOG entries in between. `grep -c '0\.3\.0' "$TURNS/1.md"` → 1 or more.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- The restart instruction is in the batch, outside fenced blocks, before "Nothing is written yet": a new or fresh chat, session or conversation in any wording ("a new Claude Code session", "a new chat in the Jenny mode"), or restarting Claude Code or Cursor. `` awk '/^ *```/{f=!f;next} f{next} /(^|[^A-Za-z])([Nn]ew|[Ff]resh) ([^ ]+ )?([^ ]+ )?([^ ]+ )?(chat|session|conversation)([^A-Za-z]|$)|[Rr]estart (Claude Code|Cursor)|[Ss]tart Claude Code again/ && !r {r=NR} /Nothing is written yet/ {n=NR} END {print (r && r < n) ? "ok" : "no"}' "$TURNS/1.md" `` → `ok`.

## Key at write

Graded after turn 2. `V="$(cat "$REPO/VERSION")"`. The upgrade's file work is `install.sh upgrade`'s, which `acceptance/install/test_install.py` holds from this Start (`test_from_0_2_0`): each Tool skill replaced and 0.2.0's `setup/VERSION` gone, this version in `jenny/VERSION`, this version's `AGENTS.md` block with the text outside the markers kept, the Guard, and nothing else from the clone. The lines below grade what is still Jenny's.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -E '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] upgrade \| Tool 0\.2\.0 → ' | grep -cF "→ $V"` → `1`.
- Log entry. `grep -cE '^## \[[0-9]{4}-[0-9]{2}-[0-9]{2}\] upgrade \| Tool 0\.2\.0 → ' "$WS"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- The Tool version setting is this version's. `grep -cx "Tool version: $V" "$WS/workspace.md"` → `1`.
- Only the Tool version setting changed. `git -C "$WS" diff -U0 "$BASE" HEAD -- workspace.md | grep -E '^[-+]' | grep -vE '^(\+\+\+|---) ' | grep -v '^[-+]Tool version: '` → empty.
- Operator's MCP entry kept. `git -C "$WS" diff --name-only "$BASE" HEAD -- .mcp.json CLAUDE.md` → empty.
- No record changed. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects veneer.md` → empty.
- Exactly these files outside the skills folder changed, the log in the run's month. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD | grep -v "^${SK#"$WS"/}/") <(printf '%s\n' AGENTS.md "log/$(date +%F | cut -c1-7).md" workspace.md)` → empty.

## By eye

- The batch is numbered and covers skills, the `AGENTS.md` block (as a diff), settings, MCP config and the CHANGELOG entries, each saying what changes or that nothing does.
- The reply after writing says how to roll back (revert the one commit) and repeats the restart.
- Plain language; no skill or template internals shown to the Operator.
