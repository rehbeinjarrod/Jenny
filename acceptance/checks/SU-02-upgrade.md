---
id: SU-02
version: 7
skills: [setup]
cursor-bench: true
repeat-at-gate: false
---

# SU-02 · Upgrade a Tool 0.2.0 Workspace to this version

A Workspace installed at Tool 0.2.0 holds the Operator's own text outside the `AGENTS.md` markers, an MCP entry they added, and a non-default `Outbound:`. The Operator has pulled the new version into the clone and asks Jenny to upgrade. Jenny proposes one batch that ends with the restart instruction, writes nothing until confirm, then upgrades in one commit and leaves every record and Operator setting as it was.

Tool 0.2.0 has no upgrade of its own, so the Operator points at the clone's `setup`, as the 0.4.0 CHANGELOG says to.

## Start

**No install.** Sample v7, with the frozen fixture `acceptance/fixtures/workspace-0.2.0/` laid over it as the Tool 0.2.0 install: after copying the sample, `cp -r "$REPO/acceptance/fixtures/workspace-0.2.0/." "$WS/"`, `mkdir -p "$WS/.claude" && mv "$WS/skills" "$SK"`, `sed -i "s|^Clone path: .*|Clone path: $REPO|" "$WS/workspace.md"`, then commit as `[2026-11-11] install | Tool 0.2.0 for claude-code` and note it as `$BASE`.

The key relies on: `workspace.md` (`Outbound: outbox`, and `Sample version: 3`, the frozen fixture's own line), `AGENTS.md` (the 0.2.0 block, then `## My notes` outside the markers), `.mcp.json` (the `atlassian` entry and the Operator's `calendar` entry), `$SK/setup/VERSION` (0.2.0's place for the copied version), and the records in `projects/` and `veneer.md`.

## Operator script

1. I've pulled the new Jenny into my clone. Follow <REPO>/skills/setup/SKILL.md to upgrade this Workspace.
2. Yes, upgrade it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`. `$V` is `$(cat "$REPO/VERSION")`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Names both versions. `grep -c '0\.2\.0' "$TURNS/1.md"` → 1 or more; `grep -cF "$V" "$TURNS/1.md"` → 1 or more.
- Shows the CHANGELOG entries in between. `grep -c '0\.3\.0' "$TURNS/1.md"` → 1 or more.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more.
- The restart instruction is in the batch, outside fenced blocks, before "Nothing is written yet": a new or fresh chat, session or conversation in any wording ("a new Claude Code session", "a new chat in the Jenny mode"), or restarting Claude Code or Cursor. `awk '/^ *```/{f=!f;next} f{next} /(^|[^A-Za-z])([Nn]ew|[Ff]resh) ([^ ]+ )?([^ ]+ )?([^ ]+ )?(chat|session|conversation)([^A-Za-z]|$)|[Rr]estart (Claude Code|Cursor)|[Ss]tart Claude Code again/ && !r {r=NR} /Nothing is written yet/ {n=NR} END {print (r && r < n) ? "ok" : "no"}' "$TURNS/1.md"` → `ok`.
- (soft) Never says a renamed canonical term (Project, Epic, Question) outside code spans and fenced blocks, since the upgrade diff is shown verbatim. `awk '/^ *```/{f=!f;next} !f' "$TURNS/1.md" | sed 's/`[^`]*`//g' | grep -oiwE 'projects?|epics?|questions?' | wc -l` → 0.

## Key at write

Graded after turn 2.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -E '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] upgrade \| Tool 0\.2\.0 → ' | grep -cF "→ $V"` → `1`.
- Log entry. `grep -cE '^## \[[0-9]{4}-[0-9]{2}-[0-9]{2}\] upgrade \| Tool 0\.2\.0 → ' "$WS"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Versions match. `cmp "$REPO/VERSION" "$SK/jenny/VERSION"` → empty; `grep -cx "Tool version: $V" "$WS/workspace.md"` → `1`.
- Skills replaced. `diff -r -x VERSION "$REPO/skills" "$SK"` → empty; `test -e "$SK/setup/VERSION" && echo yes` → empty.
- Only the Tool version setting changed. `git -C "$WS" diff -U0 "$BASE" HEAD -- workspace.md | grep -E '^[-+]' | grep -vE '^(\+\+\+|---) ' | grep -v '^[-+]Tool version: '` → empty.
- Text outside the markers unchanged. `diff <(git -C "$WS" show "$BASE:AGENTS.md" | sed '/^<!-- jenny:begin -->$/,/^<!-- jenny:end -->$/d') <(sed '/^<!-- jenny:begin -->$/,/^<!-- jenny:end -->$/d' "$WS/AGENTS.md")` → empty.
- Block is this version's. `diff <(sed -n '/^<!-- jenny:begin -->$/,/^<!-- jenny:end -->$/p' "$WS/AGENTS.md") "$REPO/skills/setup/templates/agents-block.md"` → empty.
- Operator's MCP entry kept. `git -C "$WS" diff --name-only "$BASE" HEAD -- .mcp.json CLAUDE.md` → empty.
- No record changed. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects veneer.md` → empty.
- Exactly these files outside the skills folder changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -v '^\.claude/skills/'` → `AGENTS.md`, `log/<YYYY-MM>.md` (the run's month), `workspace.md`, and nothing else.
- Nothing from the clone beyond its skills. `test -e "$WS/acceptance" -o -e "$SK/acceptance" && echo yes` → empty; `git -C "$WS" ls-files | grep -c acceptance` → `0`.

## By eye

- The batch is numbered and covers skills, the `AGENTS.md` block (as a diff), settings, MCP config and the CHANGELOG entries, each saying what changes or that nothing does.
- The reply after writing says how to roll back (revert the one commit) and repeats the restart.
- Plain language; no skill or template internals shown to the Operator.
