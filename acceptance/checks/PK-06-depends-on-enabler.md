---
id: PK-06
version: 2
skills: [pack]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PK-06 · A dependent Epic's pack names its Technical Enabler in section 7, and nothing more of it

The Operator asks Jenny to write the pack for the court timetable Epic, which depends on the card payment account, a Technical Enabler, and holds an Enabler Story. After confirm, section 7 names the Technical Enabler by its shown name, ID and title as "must be built first", with no Handoff state; none of the Technical Enabler's Questions or Decisions is copied in, even the one affecting a Requirement this Epic covers; no Enabler Story reaches the pack; and everything lands in one commit.

## Start

Sample v7. Fixture: `acceptance/fixtures/pack/enabler/` (the court Project after its card payment account became a Technical Enabler). After install, lay it into the court Project and commit:

```sh
cd "$WS/projects/court-bookings" && F="$REPO/acceptance/fixtures/pack/enabler" && cp -r "$F/court-bookings/." . && sed -i "/^- \[log\/\]/i $(cat "$F/index-line.md")" index.md && sed -i "/CRT-SRC-003-email-joe-court-timetable.md) |/r $F/sources-index-row.md" sources/index.md && cat "$F/log-entry.md" >> log/2026-11.md && git -C "$WS" add -A && git -C "$WS" commit -qm "Add CRT-EPC-002 Card payment account, a Technical Enabler"
```

The key relies on, in `projects/court-bookings/` after the overlay:

- `epics/CRT-EPC-002-card-payment-account/epic.md`: `Technical Enabler: yes`, `Feature: CRT-FEA-001`, `Enables: CRT-REQ-001, CRT-REQ-008`, `## Covers` reading `None.`; not handed off, no N/A marks.
- The Enabled Requirements: `CRT-REQ-001` (a court booking is paid in full when it is made), in `CRT-FEA-001`, covered by no Epic, so it is not sliced yet; `CRT-REQ-008` (an hour shows as taken as soon as its booking is paid), covered by `CRT-EPC-001`.
- `epics/CRT-EPC-001-see-which-courts-are-free/epic.md`: covers `CRT-REQ-005` to `CRT-REQ-008`; depends on `CRT-EPC-002`; holds the Enabler Story `CRT-ENS-001` (a nightly copy of the court bookings for the timetable); not handed off.
- Questions naming the Technical Enabler: `CRT-Q-004` (`Affects: CRT-EPC-002, CRT-REQ-008`) answered by `CRT-ANS-001` (a Decision owned by Joe Park, Stakeholder: the account is in the centre's name and pays into its existing bank account), and `CRT-Q-005` open (whether the centre takes American Express), `Affects: CRT-EPC-002, CRT-REQ-008`. Questions on the Enabled Requirements only, which bear on the Epics delivering them: `CRT-Q-002` (`Affects: CRT-REQ-001`) and `CRT-Q-003` (`Affects: CRT-REQ-008`, `Needed by: CRT-EPC-001`). Highest Question `CRT-Q-005`.

And `projects/hall-bookings/` (untouched), and `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item; no shown name for Technical Enabler).

## Operator script

1. Write the pack for the court timetable spec.
2. Keep every gap as an open item, with no N/A marks. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`. `cats() { for w in rules boundaries unwanted states variants data permissions downstream quality rollout examples; do grep -ci "$w" "$1"; done | grep -cx 0; }` (how many of the 11 categories a reply never names).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Coverage runs first: all 11 categories shown. `cats "$TURNS/1.md"` → `0`.
- The new pack is an item. `grep -c 'pack-v1.md' "$TURNS/1.md"` → 1 or more.
- Its own open Question is in the proposal. `grep -c 'CRT-Q-003' "$TURNS/1.md"` → 1 or more.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more.
- No hall items. `grep -c 'HAL-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `P="$WS/projects/court-bookings"`, `PK="$P/epics/CRT-EPC-001-see-which-courts-are-free/pack-v1.md"`, `NEWQ=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/court-bookings/questions/CRT-Q-*.md')`, `sec() { awk -v n="$1" '/^## /{s=(index($0, "## " n ".")==1)} s' "$PK"; }` (section `$1` of the pack, heading included), and `` prose() { awk '/^```/{f=!f;next} !f' "$PK" | sed 's/`[^`]*`//g'; } `` (the pack outside code blocks and code spans).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] pack \| '` → `1`; `cat "$P"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only pack files changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/court-bookings/(index\.md|questions/[^/]+\.md|epics/CRT-EPC-001-see-which-courts-are-free/pack-v1\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- `index.md` gains one link line naming v1 and loses none. `git -C "$WS" diff --numstat "$BASE" HEAD -- projects/court-bookings/index.md | cut -f1,2` → `1	0`; `git -C "$WS" diff "$BASE" HEAD -- projects/court-bookings/index.md | grep '^+ ' | grep -c 'pack-v1.md'` → `1`.
- One new pack file, and nothing else under `epics/` changed. `git -C "$WS" diff --name-status "$BASE" HEAD -- projects/court-bookings/epics/ | tr '\t\n' '  '` → `A projects/court-bookings/epics/CRT-EPC-001-see-which-courts-are-free/pack-v1.md `.
- The pack passes the pack shape scan. `python3 "$REPO/skills/pack/scripts/pack_shape.py" "$PK" | grep -cE '^[0-9]+ lines$'` → `1`.
- No Enabler Story in the pack, by its ID, its term or its title. `grep -ciE 'CRT-ENS-|enabler stor|nightly copy of the court bookings' "$PK"` → `0`.
- No Source IDs. `grep -c 'CRT-SRC-' "$PK"` → `0`.
- People by role, never by name. `grep -ciwE 'joe|park|dana|wells' "$PK"` → `0`.
- New Questions name people by role, never by name. `for q in $NEWQ; do head -1 "$WS/$q"; done | grep -ciwE 'joe|park|dana|wells'` → `0`.
- Shown names in the pack: no renamed canonical term outside code. `prose | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`; `prose | grep -ciw 'spec'` → 1 or more.
- Section 7 names the Technical Enabler by shown name, ID and title, as must be built first. `sec 7 | grep 'CRT-EPC-002' | grep -i 'technical enabler' | grep -i 'card payment account' | grep -ci 'must be built first'` → `1`.
- No Handoff state for it. `sec 7 | grep -ciE 'handed|tech face|work item'` → `0`.
- None of the Technical Enabler's Questions or Decisions. `grep -cE 'CRT-Q-004|CRT-Q-005|CRT-ANS-001' "$PK"` → `0`.
- Its own open Question is `DO NOT DECIDE`. `grep 'CRT-Q-003' "$PK" | grep -c 'DO NOT DECIDE'` → 1 or more.
- Section 4 is its own covered Requirements. `sec 4 | grep '^### ' | grep -oE 'CRT-REQ-[0-9]{3}' | tr '\n' ' '` → `CRT-REQ-005 CRT-REQ-006 CRT-REQ-007 CRT-REQ-008 `.
- Every Question raised in the batch is in the pack. `for q in $NEWQ; do grep -c "$(basename "$q" | cut -c1-9)" "$PK"; done | grep -cx 0` → `0`.
- Every new Question is in the index. `for q in $NEWQ; do grep -c "\[$(basename "$q" | cut -c1-9)\]" "$P/questions/index.md"; done | sort -u` → `1`.
- Existing Questions untouched. `git -C "$WS" diff --name-only --diff-filter=MD "$BASE" HEAD -- 'projects/court-bookings/questions/CRT-Q-*.md'` → empty.
- Hall records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings veneer.md workspace.md` → empty.
- Records other than the pack stay canonical. `git -C "$WS" diff "$BASE" HEAD -- . ':(exclude)*/pack-v*.md' | grep '^+' | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- Turn 1 shows the coverage checklist, then the batch with the pack as one item, section 7 naming the card payment account.
- Section 7's line reads like `- Technical Enabler CRT-EPC-002 Card payment account: must be built first.`
