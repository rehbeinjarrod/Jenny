---
name: setup
description: Install Jenny into a Workspace, upgrade it to a newer Tool version, create a Project, change a Project's People, or set the Veneer. Use when the Operator says to follow setup, asks to upgrade Jenny, asks for a new Project, adds or changes People, or wants to set, change or remove the Veneer.
---

# Setup

Five operations: **Install**, **Upgrade**, **New Project**, **People**, **Veneer**. Each is one confirm-then-write operation, following the rules in the Tool-owned block of `AGENTS.md` (its source is [templates/agents-block.md](templates/agents-block.md)). Every reply to the Operator uses Veneer names, the batch headings included, while every file written uses canonical terms. A proposal shows what each file will hold, never which template it comes from.

## The AGENTS.md block

Install and Upgrade write the Tool-owned block of `AGENTS.md` with these commands, in bash, from the Workspace, with `T=<clone>/skills/setup/templates/agents-block.md`. Each builds `AGENTS.md.new`, so `AGENTS.md` stays as it was until the new file passes the check.

1. **Build** the one that fits:
   - No `AGENTS.md`: `cp "$T" AGENTS.md.new`.
   - `AGENTS.md` without the markers: the block at the top, the rest kept, `{ cat "$T"; echo; cat AGENTS.md; } > AGENTS.md.new`.
   - `AGENTS.md` with the markers: the lines from `<!-- jenny:begin -->` to `<!-- jenny:end -->` replaced, every other line kept, `awk -v f="$T" '/^<!-- jenny:begin -->$/ { while ((getline l < f) > 0) print l; s = 1; next } /^<!-- jenny:end -->$/ { s = 0; next } !s' AGENTS.md > AGENTS.md.new`.
2. **Check** that the block is whole:
   - `grep -c '^<!-- jenny:begin -->$' AGENTS.md.new` prints `1`, and so does `grep -c '^<!-- jenny:end -->$' AGENTS.md.new`.
   - `diff <(sed -n '/^<!-- jenny:begin -->$/,/^<!-- jenny:end -->$/p' AGENTS.md.new) "$T"` prints nothing.

   When either fails, `rm AGENTS.md.new` and build it again with the command, unchanged.
3. **Move** it in place: `mv AGENTS.md.new AGENTS.md`.

Done when: the same check, run on `AGENTS.md`, passes, and `AGENTS.md.new` is gone.

## Install

Runs when the Operator, in a folder with no Jenny skills yet, says to follow this file. `<clone>` is the folder two levels above this `SKILL.md` (the Tool clone). Before anything else, read `templates/agents-block.md`: its confirm-then-write rules govern install too.

1. **Gather.**
   - Runtime: Claude Code or Cursor. Ask unless the Operator said. Claude Code is stored as `claude-code` and uses `.claude/skills/` and `.mcp.json`; Cursor is stored as `cursor` and uses `.cursor/skills/` and `.cursor/mcp.json`.
   - Tool version: `cat <clone>/VERSION`.
   - The folder: `ls -A`. Empty is the usual case. A folder with Workspace records (`workspace.md`, `veneer.md`, `projects/`) and no Jenny skills is installed into without changing those records. If a skills folder already holds `jenny/VERSION` (or `setup/VERSION`, from Tool 0.2.0 and earlier), Jenny is installed: stop and say so, and that a newer Tool version goes in through **Upgrade**. Any other file: list it and ask before going on.
   - Outbound: `post` (Jenny posts to Jira and Confluence after confirm) unless the Operator wants `outbox` (Jenny writes what would be posted to `outbox/` instead). An existing `Outbound:` line is kept.

   Done when: you hold the runtime, version, clone path, outbound and the folder's state.

2. **Propose** this numbered batch, then "Nothing is written yet.":
   1. Copy every folder in `<clone>/skills/` into the runtime's skills folder.
   2. Copy `<clone>/VERSION` to `<skills folder>/jenny/VERSION`, where the Jenny mode checks it.
   3. `AGENTS.md`: the block from `templates/agents-block.md`. If `AGENTS.md` exists without the markers, the block goes at the top and the rest is kept as it is; if it holds the markers, only the block between them is replaced.
   4. Claude Code only, because it reads `CLAUDE.md` rather than `AGENTS.md`: `CLAUDE.md` holding the line `@AGENTS.md`. If `CLAUDE.md` exists without that line, the line goes at the top and the rest is kept.
   5. `workspace.md` from `templates/workspace.md`. If it exists, set the `Tool version:`, `Runtime:` and `Clone path:` lines, add `Outbound:` if missing, and keep every other line.
   6. The MCP config from `templates/mcp-claude-code.json` or `templates/mcp-cursor.json`: the Atlassian MCP server, which signs in through the browser, so the file holds no secrets. If the file exists, add the `atlassian` entry only if it is missing and keep the rest.
   7. Log entry in `log/<YYYY-MM>.md`: `## [<date>] install | Tool <version> for <runtime>`, with the stored runtime value.
   8. `git init`, then one commit. Skip `git init` only when the folder is the top of its own git repository (`git rev-parse --show-toplevel` prints this folder); a folder inside some other git repository gets its own.

   Done when: the batch is shown, ending with "Nothing is written yet."

3. **Amend** by number until the Operator confirms. Done when: the Operator has said yes to the batch as last shown.

4. **Write.** `mkdir -p <skills folder>`, `cp -r <clone>/skills/. <skills folder>/`, `cp <clone>/VERSION <skills folder>/jenny/VERSION`. Write `AGENTS.md` as **The AGENTS.md block** says. Write the other files and the log entry, then `git init` (as item 8 says) and commit as `AGENTS.md` says. If git has no user name or email, ask the Operator for them and set them for this git repository only (`git config user.name …`).

   Done when: `git status --porcelain` is empty, `git log -1 --format=%s` is the log heading, the skills folder matches `<clone>/skills/` apart from `jenny/VERSION`, and **The AGENTS.md block** is done.

5. **Hand on.** Tell the Operator Jenny is installed, which runtime folder holds the skills, and that the next step is a new Project (and a Veneer, if they want their organisation's words). In Claude Code, the skills load in a new session started in this folder. In Cursor, every Jenny chat runs in the Jenny mode: give the Operator the mode's settings from `<skills folder>/jenny/mode.md`, in full, and say to start a new chat in it. Done when: the Operator has been told all three, and on Cursor has the mode's settings.

## Upgrade

Runs when the Operator, in an installed Workspace, asks to upgrade Jenny after pulling a newer Tool version into their clone. The new version runs its own upgrade: these steps are always read from the clone.

1. **Find the clone's instructions.** `<clone>` is the `Clone path:` line of `workspace.md`; with no such line, ask the Operator where their clone is. If this file is not `<clone>/skills/setup/SKILL.md`, read that file whole and follow its Upgrade section in place of this one. Done when: you are reading the clone's own `setup`.

2. **Gather.** `<skills>` is the runtime's skills folder (from `Runtime:` in `workspace.md`, as in Install).
   - Versions: `<old>` is the `Tool version:` line of `workspace.md`; `<new>` is `cat <clone>/VERSION`. Equal: say the Workspace is already on `<new>` and stop. `<new>` older than `<old>` (compare each dot-separated number in turn, so `0.10.0` is newer than `0.9.0`): there is no downgrade; say so, and that going back is reverting the upgrade commit (`git revert <commit>`), then stop.
   - A clean tree: `git status --porcelain` is empty, so the one commit holds only the upgrade. Otherwise list what is uncommitted, ask the Operator to commit or drop it, and stop until the tree is clean.
   - Skills: `diff -rq -x VERSION <clone>/skills <skills>`, for each Tool skill folder added, changed or unchanged. A folder in `<skills>` that `<clone>/skills/` lacks is either a Tool skill a CHANGELOG entry in between says was dropped, which is removed so it no longer routes, or the Operator's own, which stays.
   - The `AGENTS.md` block: the lines from `<!-- jenny:begin -->` to `<!-- jenny:end -->` against `<clone>/skills/setup/templates/agents-block.md`, as a unified diff. Missing or doubled markers: stop and ask the Operator where the Tool's block is.
   - Settings: the `Key: value` lines above `## Projects` in `workspace.md`, against the **Settings** table below. A setting in the table and missing from `workspace.md` is new: it is added with its default. A line from the old Tool's `<skills>/setup/templates/workspace.md` that the table no longer holds is no longer used: it stays, and is named. Every other line, Operator values included, stays as it is.
   - MCP config: the old Tool's `<skills>/setup/templates/mcp-<runtime>.json` against the clone's. An entry the template changed is updated in the config only where the config still holds the old template's entry; an entry the Operator changed or added stays, and a template change to an entry they changed is shown for them to make by hand.
   - CHANGELOG: every entry in `<clone>/CHANGELOG.md` above `<old>`, up to and including `<new>`, with its line on how older record shapes are read.

   Done when: you hold both versions, a clean tree, and each of skills, the `AGENTS.md` block, settings, MCP config and CHANGELOG as "changes" with what, or "no change".

3. **Propose** this numbered batch under the heading "Upgrade: Tool `<old>` → `<new>`":
   1. Skills: each Tool skill folder in `<skills>` replaced by the clone's, by name, with which are new and which changed; each dropped Tool skill removed; the Operator's own folders stay.
   2. `<skills>/jenny/VERSION` set to `<new>`.
   3. `AGENTS.md`: the block between the markers, shown as the diff in a fenced `diff` block. Text outside the markers stays as it is.
   4. `workspace.md`: `Tool version: <new>`; each new setting with its default; each setting no longer used, left in place. Every other line stays, `## Projects` and its list included.
   5. MCP config: each template change, or "no change". Entries the Operator added stay.
   6. What changed, from the CHANGELOG: every entry the Gather step collected, each led by its version number (`0.3.0: …`) in a line or two, with how older records are read. Entries that change nothing the Operator would notice may share one line that names each of their versions. Records are never rewritten by an upgrade.
   7. Log entry in `log/<YYYY-MM>.md`: `## [<date>] upgrade | Tool <old> → <new>`.
   8. One commit.

   End the batch with the restart, so the new skills load once it is written: on Cursor, leave the Jenny mode and start it again in a new chat; on Claude Code, start a new session in this folder. Then "Nothing is written yet."

   The block and the CHANGELOG are written in canonical terms, so every line of the batch outside the fenced diff is your own retelling in shown names: "`pack` writes the frozen <shown name for Epic pack>", "asking where a <shown name for Epic> stands goes to `signoff`".

   Done when: the batch is shown, item 6 names every version in range however long the gap, and it ends with the restart and "Nothing is written yet."

4. **Amend** by number until the Operator confirms. Done when: the Operator has said yes to the batch as last shown.

5. **Write**, as one operation. Copy only from `<clone>/skills/` and `<clone>/VERSION`; nothing else in the clone belongs in a Workspace.
   - Edit only the `workspace.md` and MCP config lines the batch names, before the old templates are replaced.
   - For each folder `<name>` in `<clone>/skills/`: `rm -rf <skills>/<name> && cp -r <clone>/skills/<name> <skills>/`. Then `rm -rf` each dropped Tool skill the batch names.
   - `cp <clone>/VERSION <skills>/jenny/VERSION`.
   - Replace the block in `AGENTS.md` as **The AGENTS.md block** says, leaving every line outside the markers.
   - Write the log entry and commit as `AGENTS.md` says.

   Done when: `git status --porcelain` is empty, `git log -1 --format=%s` is the log heading, `cmp <clone>/VERSION <skills>/jenny/VERSION` is silent, `Tool version:` is `<new>`, `diff -r -x VERSION <clone>/skills <skills>` reports only the Operator's own folders, and **The AGENTS.md block** is done.

6. **Hand on.** Tell the Operator the Workspace is on `<new>`, that going back is reverting that one commit (`git revert HEAD` while it is the last), and, again, the restart for their runtime. Done when: the Operator has been told all three.

### Settings

The `workspace.md` settings this version holds, with the default an upgrade adds.

| Setting | Default |
| --- | --- |
| `Tool version:` | set by install and upgrade |
| `Runtime:` | set by install |
| `Clone path:` | set by install |
| `Outbound:` | `post` |

## New Project

1. **Gather** from the Operator's words, asking for what is missing:
   - **Name**.
   - **Code**: 2 to 4 capital letters, unused by any Project in `workspace.md`. Propose one from the name if not given.
   - **Slug**: the name in lower case, words joined with hyphens, other punctuation dropped.
   - **People**: each with a name and one role, `Operator`, `Stakeholder` or `engineer`, plus an optional note of what they look after. Ask for a missing role rather than guess.
   - **Description**: one or two plain sentences from the Operator's words. Propose one if they gave none.

   Done when: you hold a name, a free code, a slug, a description and a role for every person.

2. **Propose**, saying that the code and slug can never change once written:
   1. `projects/<slug>/project.md` from `templates/project.md`, with the People table shown in full.
   2. `projects/<slug>/index.md` from `templates/project-index.md`.
   3. Log entry in `projects/<slug>/log/<YYYY-MM>.md`: `## [<date>] setup | New Project <CODE> <Name>`, naming each file written and each person with their role.
   4. `workspace.md`: add `- **<CODE>** · <Name> · [projects/<slug>/](projects/<slug>/index.md)` under `## Projects` (replacing "None yet.").

   Done when: the batch is shown, ending with "Nothing is written yet."

3. **Amend, confirm, write, log, commit** as `AGENTS.md` says.

   Done when: the four files are in one commit whose message is the log heading.

## People

Adding a person or changing a role or note on a Project. Propose the changed rows of the People table in `project.md` and a log entry `## [<date>] setup | People <CODE>: <who changed>` in that Project's log, then confirm, write, log and commit. A person is never removed, because Decisions name their owners: add `left <YYYY-MM-DD>` to their note instead.

Done when: `project.md` and the log entry are in one commit whose message is the log heading.

## Veneer

Setting, changing or removing the Workspace's `veneer.md` (shape: [templates/veneer.md](templates/veneer.md)).

- Only Delivery terms can be renamed: Project, Requirement, Feature, Epic, Slice, Epic pack, Decision coverage, Sign-off view, Sign-off, Handoff, Story, Question, Answer, Decision, Source, Capture, Milestone, Spike. The terms `AGENTS.md` says are never renamed keep their names; say so if asked.
- Each term has one shown name and any number of input-only aliases. Shown names are unique. Reject an alias that equals another term's shown name, and ask the Operator to rename that term first.
- `Owner:` is the Operator, by the name in a Project's People or the name they give. Ask when neither is known.

Propose the full table as it will be written (or the deletion of `veneer.md`) with a log entry `## [<date>] setup | Veneer <what changed>` in `log/<YYYY-MM>.md`, then confirm, write, log and commit. From the next reply on, speak in the new shown names.

Done when: the commit holds `veneer.md` and the log entry, and nothing else.
