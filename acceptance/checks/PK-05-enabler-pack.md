---
id: PK-05
version: 2
skills: [pack]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PK-05 · The full pack of a Technical Enabler: Enabled Requirements in section 4, what becomes possible in section 9

The Operator asks Jenny to write the pack for the court Project's card payment account, a Technical Enabler. Jenny runs Decision coverage first and proposes the gap Questions and `pack-v1.md` in one confirm-then-write batch. After confirm, the pack has the ordinary shape and passes the pack shape scan. Section 4 lists each Enabled Requirement word for word with the Epic delivering it (or "not sliced yet") in place of From and rules; section 9 has a criterion for the settled Decision and one for each Enabled Requirement; section 5 holds only the Technical Enabler's own open Question. No Enabler Story reaches the pack, and everything lands in one commit.

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

1. Write the pack for the card payment account spec.
2. Keep every gap as an open item, with no N/A marks. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`. `cats() { for w in rules boundaries unwanted states variants data permissions downstream quality rollout examples; do grep -ci "$w" "$1"; done | grep -cx 0; }` (how many of the 11 categories a reply never names).

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Coverage runs first: all 11 categories shown. `cats "$TURNS/1.md"` → `0`.
- The new pack is an item. `grep -c 'pack-v1.md' "$TURNS/1.md"` → 1 or more.
- Its own open Question is in the proposal; no checklist row cites a Question on the Enabled Requirements alone. `grep -c 'CRT-Q-005' "$TURNS/1.md"` → 1 or more; `grep '^|' "$TURNS/1.md" | grep -cE 'CRT-Q-00[23]'` → `0`.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more.
- No hall items. `grep -c 'HAL-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `P="$WS/projects/court-bookings"`, `PK="$P/epics/CRT-EPC-002-card-payment-account/pack-v1.md"`, `NEWQ=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/court-bookings/questions/CRT-Q-*.md')`, `sec() { awk -v n="$1" '/^## /{s=(index($0, "## " n ".")==1)} s' "$PK"; }` (section `$1` of the pack, heading included), and `` prose() { awk '/^```/{f=!f;next} !f' "$PK" | sed 's/`[^`]*`//g'; } `` (the pack outside code blocks and code spans).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] pack \| '` → `1`; `cat "$P"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only pack files changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/court-bookings/(index\.md|questions/[^/]+\.md|epics/CRT-EPC-002-card-payment-account/pack-v1\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- `index.md` gains one link line naming v1 and loses none. `git -C "$WS" diff --numstat "$BASE" HEAD -- projects/court-bookings/index.md | cut -f1,2` → `1	0`; `git -C "$WS" diff "$BASE" HEAD -- projects/court-bookings/index.md | grep '^+ ' | grep -c 'pack-v1.md'` → `1`.
- One new pack file, and nothing else under `epics/` changed. `git -C "$WS" diff --name-status "$BASE" HEAD -- projects/court-bookings/epics/ | tr '\t\n' '  '` → `A projects/court-bookings/epics/CRT-EPC-002-card-payment-account/pack-v1.md `.
- The pack passes the pack shape scan. `python3 "$REPO/skills/pack/scripts/pack_shape.py" "$PK" | grep -cE '^[0-9]+ lines$'` → `1`.
- No Enabler Story in the pack. `grep -ciE 'CRT-ENS-|enabler stor|nightly' "$PK"` → `0`.
- No Source IDs. `grep -c 'CRT-SRC-' "$PK"` → `0`.
- People by role, never by name. `grep -ciwE 'joe|park|dana|wells' "$PK"` → `0`.
- Shown names in the pack: no renamed canonical term outside code. `prose | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`; `prose | grep -ciw 'spec'` → 1 or more.
- Section 4 lists the Enabled Requirements, in `Enables:` order, and nothing else. `sec 4 | grep '^### ' | grep -oE 'CRT-REQ-[0-9]{3}' | tr '\n' ' '` → `CRT-REQ-001 CRT-REQ-008 `.
- Each word for word. `sec 4 | grep -cxF '> A court booking is paid in full when it is made; there is no deposit.'` → `1`; `sec 4 | grep -cxF '> An hour shows as taken as soon as its booking is paid.'` → `1`.
- Delivered by in place of From and rules: the timetable Epic for `CRT-REQ-008`, not sliced yet for `CRT-REQ-001`. `sec 4 | grep -cE '^- Delivered by: CRT-EPC-001\.?$'` → `1`; `sec 4 | grep -ciE '^- Delivered by: not sliced yet\.?$'` → `1`; `sec 4 | grep -c '^- '` → `2`.
- Section 9: a criterion for the settled Decision and for each Enabled Requirement. `for i in CRT-ANS-001 CRT-REQ-001 CRT-REQ-008; do sec 9 | grep '^- \[ \]' | grep -c "$i"; done | grep -cx 0` → `0`.
- The settled Decision is in section 3. `sec 3 | grep -c 'CRT-ANS-001'` → 1 or more.
- Its own open Question is `DO NOT DECIDE`. `grep 'CRT-Q-005' "$PK" | grep -c 'DO NOT DECIDE'` → 1 or more.
- No Question that bears only on the Epics it enables. `grep -cE 'CRT-Q-00[123]' "$PK"` → `0`.
- Coverage raised gap Questions, each in the pack. `echo "$NEWQ" | grep -c .` → 1 or more; `for q in $NEWQ; do grep -c "$(basename "$q" | cut -c1-9)" "$PK"; done | grep -cx 0` → `0`.
- Every new Question has the coverage shape, scored, for the Technical Enabler. `for q in $NEWQ; do f="$WS/$q"; i=$(sed -n 's/^Impact: //p' "$f"); u=$(sed -n 's/^Uncertainty: //p' "$f"); s=$(sed -n 's/^Score: //p' "$f"); [ "$((i*u))" = "$s" ] || echo "$q score"; grep -qE '^Category: (Rules|Boundaries|Unwanted behaviour|States|Variants|Data|Permissions|Downstream|Quality|Rollout|Examples)$' "$f" || echo "$q category"; grep -qE '^Affects: CRT-EPC-002' "$f" || echo "$q affects"; grep -qx 'Needed by: CRT-EPC-002' "$f" || echo "$q needed"; grep -qx 'Raised from: Decision coverage of CRT-EPC-002' "$f" || echo "$q raised"; done` → empty.
- Every new Question is in the index. `for q in $NEWQ; do grep -c "\[$(basename "$q" | cut -c1-9)\]" "$P/questions/index.md"; done | sort -u` → `1`.
- Existing Questions untouched. `git -C "$WS" diff --name-only --diff-filter=MD "$BASE" HEAD -- 'projects/court-bookings/questions/CRT-Q-*.md'` → empty.
- Hall records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings veneer.md workspace.md` → empty.
- Records other than the pack stay canonical. `git -C "$WS" diff "$BASE" HEAD -- . ':(exclude)*/pack-v*.md' | grep '^+' | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- Turn 1 shows the coverage checklist with the Enabled Requirements as context, not as what settles a category, then the batch with the pack as one item, section by section, and its line count.
- Section 9's Enabled Requirement criteria each say what becomes possible once the account exists, for example a booking paid in full by card.
- Section 1 and section 8 say only what the records say, "Not stated yet." where they are silent.
