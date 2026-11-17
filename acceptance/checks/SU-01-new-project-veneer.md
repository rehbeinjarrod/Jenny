---
id: SU-01
version: 11
skills: [setup]
cursor-bench: true
routing: false
inputs: []
promise: false
---

# SU-01 · New Project with People in the Veneer Workspace

The Operator asks for a new Project in Veneer words (a shown name, then an alias). Jenny proposes in Veneer names, takes one amend, writes nothing until confirm, then writes canonical records in one commit.

## Start

Sample v7 as it is. No fixtures. The key relies on `workspace.md` (Projects HAL and CRT, so the code RAL is free), `veneer.md` (Project shown as Initiative, alias programme) and `projects/hall-bookings/` (untouched).

## Operator script

1. Set up a new initiative for the council's allotment waiting list. Call it Riverside Allotments, code RAL. People: Priya Shah is the Stakeholder (allotments officer), Tom Okafor is the engineer, and I'm the Operator, Dana Wells.
2. Add Lee Chen to the programme as a Stakeholder too, plot holders' rep. Otherwise fine.
3. Yes, write it.

## Key at proposal

Graded after turn 1 (on `$TURNS/1.md`) and again after turn 2 (on `$TURNS/2.md`).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Shows the Veneer name. `` sed 's/`[^`]*`//g' "$TURNS/<n>.md" | grep -ciw initiative `` → 1 or more.
- Code and slug. `grep -c 'RAL' "$TURNS/<n>.md"` → 1 or more; `grep -c 'riverside-allotments' "$TURNS/<n>.md"` → 1 or more.
- People and roles. `for p in 'Priya Shah' 'Tom Okafor' 'Dana Wells'; do grep -c "$p" "$TURNS/<n>.md"; done | grep -cx 0` → `0`.
- After turn 2 only: the amend is in. `grep -c 'Lee Chen' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 3. `P="$WS/projects/riverside-allotments"`.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] setup \| .*RAL'` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Exactly these files changed, the log in the run's month. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD) <(printf '%s\n' projects/riverside-allotments/index.md "projects/riverside-allotments/log/$(date +%F | cut -c1-7).md" projects/riverside-allotments/project.md workspace.md)` → empty.
- Fixed code and slug. `grep -c '^Code: RAL$' "$P/project.md"` → `1`; `grep -c '^Slug: riverside-allotments$' "$P/project.md"` → `1`.
- People with canonical roles. Each → `1`: `grep -cE 'Dana Wells *\| *Operator' "$P/project.md"`, `grep -cE 'Priya Shah *\| *Stakeholder' "$P/project.md"`, `grep -cE 'Lee Chen *\| *Stakeholder' "$P/project.md"`, `grep -cE 'Tom Okafor *\| *engineer' "$P/project.md"`.
- Files start with ID and title. `head -1 "$P/index.md" | grep -c 'RAL'` → `1`; `head -1 "$P/project.md" | grep -c 'RAL'` → `1`.
- Log entry. `grep -cE '^## \[[0-9]{4}-[0-9]{2}-[0-9]{2}\] setup \| .*RAL' "$P"/log/*.md` → `1`.
- Listed in the Workspace. `grep -cE 'RAL.*projects/riverside-allotments/' "$WS/workspace.md"` → `1`.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|programme'` → `0`; `git -C "$WS" diff --name-only "$BASE" HEAD | grep -ci initiative` → `0`.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings veneer.md` → empty.

## By eye

- The proposal is a numbered batch the Operator could amend by number.
- The proposal says what will be written and that nothing is written yet.
- Plain language; no skill or template internals shown to the Operator.
