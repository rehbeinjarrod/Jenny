---
name: setup
description: Install Jenny into a Workspace, create a Project, change a Project's People, or set the Veneer. Use when the Operator says to follow setup, asks for a new Project, adds or changes People, or wants to set, change or remove the Veneer.
---

# Setup

Four operations: **Install**, **New Project**, **People**, **Veneer**. Each is one confirm-then-write operation, following the rules in the Tool-owned block of `AGENTS.md` (its source is [templates/agents-block.md](templates/agents-block.md)). Every reply to the Operator uses Veneer names, the batch headings included, while every file written uses canonical terms. A proposal shows what each file will hold, never which template it comes from.

Upgrading a Workspace to a new Tool version is not in this version of the Tool. Tell the Operator so if they ask.

## Install

Runs when the Operator, in a folder with no Jenny skills yet, says to follow this file. `<clone>` is the folder two levels above this `SKILL.md` (the Tool clone). Before anything else, read `templates/agents-block.md`: its confirm-then-write rules govern install too.

1. **Gather.**
   - Runtime: Claude Code or Cursor. Ask unless the Operator said. Claude Code is stored as `claude-code` and uses `.claude/skills/` and `.mcp.json`; Cursor is stored as `cursor` and uses `.cursor/skills/` and `.cursor/mcp.json`.
   - Tool version: `cat <clone>/VERSION`.
   - The folder: `ls -A`. Empty is the usual case. A folder with Workspace records (`workspace.md`, `veneer.md`, `projects/`) and no Jenny skills is installed into without changing those records. If a skills folder already holds `setup/VERSION`, Jenny is installed: stop and say so. Any other file: list it and ask before going on.
   - Outbound: `post` (Jenny posts to Jira and Confluence after confirm) unless the Operator wants `outbox` (Jenny writes what would be posted to `outbox/` instead). An existing `Outbound:` line is kept.

   Done when: you hold the runtime, version, clone path, outbound and the folder's state.

2. **Propose** this numbered batch, then "Nothing is written yet.":
   1. Copy every folder in `<clone>/skills/` into the runtime's skills folder.
   2. Copy `<clone>/VERSION` to `<skills folder>/setup/VERSION`.
   3. `AGENTS.md`: the block from `templates/agents-block.md`. If `AGENTS.md` exists without the markers, the block goes at the top and the rest is kept as it is.
   4. Claude Code only, because it reads `CLAUDE.md` rather than `AGENTS.md`: `CLAUDE.md` holding the line `@AGENTS.md`. If `CLAUDE.md` exists without that line, the line goes at the top and the rest is kept.
   5. `workspace.md` from `templates/workspace.md`. If it exists, set the `Tool version:`, `Runtime:` and `Clone path:` lines, add `Outbound:` if missing, and keep every other line.
   6. The MCP config from `templates/mcp-claude-code.json` or `templates/mcp-cursor.json`: the Atlassian MCP server, which signs in through the browser, so the file holds no secrets. If the file exists, add the `atlassian` entry only if it is missing and keep the rest.
   7. Log entry in `log/<YYYY-MM>.md`: `## [<date>] install | Tool <version> for <runtime>`, with the stored runtime value.
   8. `git init`, then one commit. Skip `git init` only when the folder is the top of its own git repository (`git rev-parse --show-toplevel` prints this folder); a folder inside some other git repository gets its own.

   Done when: the batch is shown, ending with "Nothing is written yet."

3. **Amend** by number until the Operator confirms. Done when: the Operator has said yes to the batch as last shown.

4. **Write.** `mkdir -p <skills folder>`, `cp -r <clone>/skills/. <skills folder>/`, `cp <clone>/VERSION <skills folder>/setup/VERSION`, write the files and the log entry, then `git init` (as item 8 says) and commit as `AGENTS.md` says. If git has no user name or email, ask the Operator for them and set them for this git repository only (`git config user.name …`).

   Done when: `git status --porcelain` is empty, `git log -1 --format=%s` is the log heading, and the skills folder matches `<clone>/skills/` apart from `setup/VERSION`.

5. **Hand on.** Tell the Operator Jenny is installed, which runtime folder holds the skills, and that the next step is a new Project (and a Veneer, if they want their organisation's words). In Claude Code, the skills load in a new session started in this folder. Done when: the Operator has been told all three.

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
