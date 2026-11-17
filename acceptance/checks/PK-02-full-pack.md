---
id: PK-02
version: 7
skills: [pack]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PK-02 · The full pack: For-the-agent block, DO NOT DECIDE, Agreed by, appendices last, Handoff line moved

The Operator asks Jenny to write the pack for the hall's book-and-pay Epic, which was handed off with `pack-v1.md` and has one Sign-off. Jenny runs Decision coverage first and proposes the gap Questions and a new `pack-v2.md` in one confirm-then-write batch. After confirm, `pack-v1.md` is untouched, `pack-v2.md` is new, and the `Tech face:` line in `epic.md` now names `pack-v2.md` in the same commit, as does one new link line in the Project's `index.md`. The pack has every section in order with the appendices last, the For-the-agent block with both fixed shapes, every open Question marked `DO NOT DECIDE` (the parked one listed apart), an "Agreed by" line on the signed-off Decision, people by role, no Source IDs, shown names, under 300 lines, in one commit.

## Start

Sample v7 as it is. No fixtures. The key relies on, in `projects/hall-bookings/`:

- `index.md`: links `pack-v1.md` on a line under the Epic's line.
- `epics/HAL-EPC-001-book-and-pay/epic.md`: covers `HAL-REQ-001` to `HAL-REQ-004` in `features/HAL-FEA-001-book-and-pay.md`; handed off (a `Tech face:` line naming `pack-v1.md`).
- `epics/HAL-EPC-001-book-and-pay/pack-v1.md`: the frozen v1.
- `epics/HAL-EPC-001-book-and-pay/signoffs.md`: `HAL-SO-001`, Margaret Osei (Stakeholder) agreed `HAL-ANS-001`.
- `questions/`: `HAL-ANS-001` (the deposit, a Decision owned by Margaret Osei, in `HAL-Q-001`); `HAL-Q-007` open and building on a guess, `Needed by: HAL-EPC-001`; `HAL-Q-004`, `HAL-Q-008`, `HAL-Q-009`, `HAL-Q-010`, `HAL-Q-011`, `HAL-Q-013` open or chasing, each affecting a covered Requirement or `HAL-FEA-001`; `HAL-Q-005` parked, affecting `HAL-FEA-001`. Highest Question `HAL-Q-013`.
- `project.md` People: Dana Wells (Operator), Margaret Osei (Stakeholder, hall committee chair), Ravi Kumar (engineer).

And `projects/court-bookings/` (untouched), and `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. Write the pack for the book and pay spec.
2. Keep every gap as an open item, with no N/A marks. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`. `cats() { for w in rules boundaries unwanted states variants data permissions downstream quality rollout examples; do grep -ci "$w" "$1"; done | grep -cx 0; }`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Coverage runs first: all 11 categories shown. `cats "$TURNS/1.md"` → `0`.
- The new version is a new file. `grep -c 'pack-v2.md' "$TURNS/1.md"` → 1 or more.
- The batch moves the Handoff line. `grep -c 'Tech face' "$TURNS/1.md"` → 1 or more.
- The batch links the new version from the Project's `index.md`. `sed -E 's#(questions|sources|features)/index\.md##g' "$TURNS/1.md" | grep -c 'index\.md'` → 1 or more.
- The guessed Question is in the proposal. `grep -c 'HAL-Q-007' "$TURNS/1.md"` → 1 or more.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more.
- No court items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `P="$WS/projects/hall-bookings"`, `PK="$P/epics/HAL-EPC-001-book-and-pay/pack-v2.md"`, `NEWQ=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/hall-bookings/questions/HAL-Q-*.md')`, and `` prose() { awk '/^```/{f=!f;next} !f' "$PK" | sed 's/`[^`]*`//g'; } `` (the pack outside code blocks and code spans).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] pack \| '` → `1`; `cat "$P"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only pack files changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(index\.md|questions/[^/]+\.md|epics/HAL-EPC-001-book-and-pay/(pack-v2|epic)\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- `index.md` gains one link line naming v2 and loses none. `git -C "$WS" diff --numstat "$BASE" HEAD -- projects/hall-bookings/index.md | cut -f1,2` → `1	0`; `git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/index.md | grep '^+ ' | grep -c 'pack-v2.md'` → `1`.
- A new pack file and the Handoff line; v1 and the rest of the Epic's folder untouched. `git -C "$WS" diff --name-status "$BASE" HEAD -- projects/hall-bookings/epics/ | sort | tr '\t\n' '  '` → `A projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/pack-v2.md M projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md `.
- The Handoff line names v2, the same work item and today, and is the one line of `epic.md` changed. `grep -cxF -e "- Tech face: [HALL-12](https://example.atlassian.net/browse/HALL-12) · Pack: pack-v2.md · Handed off: $(date +%F)" "$P/epics/HAL-EPC-001-book-and-pay/epic.md"` → `1`; `git -C "$WS" diff --numstat "$BASE" HEAD -- projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md | cut -f1,2` → `1	1`.
- Sections in order, appendices last. `grep -E '^## ' "$PK" | sed -E 's/^## (For the agent|[0-9]\.|Appendix [AB]).*/\1/' | tr '\n' ' '` → `For the agent 1. 2. 3. 4. 5. 6. 7. 8. 9. Appendix A Appendix B `.
- Under the cap. `[ "$(wc -l < "$PK")" -le 300 ] && echo ok` → `ok`.
- Both fixed shapes, with every field. `for w in 'Business question' 'Business call made in build' 'IDs touched' 'Options seen' 'Default if forced' 'Made by'; do grep -c "$w" "$PK"; done | grep -cx 0` → `0`.
- Engineering sections left to the repo. `grep -c 'AGENTS.md' "$PK"` → 1 or more.
- Every open Question bearing on the Epic is `DO NOT DECIDE`. `for q in HAL-Q-004 HAL-Q-007 HAL-Q-008 HAL-Q-009 HAL-Q-010 HAL-Q-011 HAL-Q-013; do grep "$q" "$PK" | grep -c 'DO NOT DECIDE'; done | grep -cx 0` → `0`.
- Coverage raised gap Questions. `echo "$NEWQ" | grep -c .` → 1 or more.
- Every Question raised in the batch is in the pack. `for q in $NEWQ; do grep -c "$(basename "$q" | cut -c1-9)" "$PK"; done | grep -cx 0` → `0`.
- The parked Question is listed apart, not as `DO NOT DECIDE`. `grep -i 'parked' "$PK" | grep -c 'HAL-Q-005'` → 1 or more; `grep 'HAL-Q-005' "$PK" | grep -c 'DO NOT DECIDE'` → `0`.
- "Agreed by" on the signed-off Decision, and only there. `grep -A2 'HAL-ANS-001' "$PK" | grep -c 'Agreed by'` → 1 or more; `grep -c 'Agreed by' "$PK"` → `1`.
- People by role, never by name. `grep -ciwE 'margaret|osei|dana|wells|ravi|kumar' "$PK"` → `0`.
- No Source IDs. `grep -c 'HAL-SRC-' "$PK"` → `0`.
- Shown names in the pack: no renamed canonical term outside code. `prose | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`; `prose | grep -ciw 'initiative'` → 1 or more.
- Every new Question has the coverage shape, scored, for a handed-off Epic. `for q in $NEWQ; do f="$WS/$q"; i=$(sed -n 's/^Impact: //p' "$f"); u=$(sed -n 's/^Uncertainty: //p' "$f"); s=$(sed -n 's/^Score: //p' "$f"); [ "$((i*u))" = "$s" ] || echo "$q score"; grep -qE '^Category: (Rules|Boundaries|Unwanted behaviour|States|Variants|Data|Permissions|Downstream|Quality|Rollout|Examples)$' "$f" || echo "$q category"; grep -qx 'Needed by: HAL-EPC-001' "$f" || echo "$q needed"; grep -qx 'Building on a guess: yes' "$f" || echo "$q guess"; grep -qx 'Raised from: Decision coverage of HAL-EPC-001' "$f" || echo "$q raised"; done` → empty.
- Every new Question is in the index. `for q in $NEWQ; do grep -c "\[$(basename "$q" | cut -c1-9)\]" "$P/questions/index.md"; done | sort -u` → `1`.
- Court records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md` → empty.
- Records other than the pack stay canonical. `git -C "$WS" diff "$BASE" HEAD -- . ':(exclude)*/pack-v*.md' | grep '^+' | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- Turn 1 shows the coverage checklist, then the batch with the pack as one item, section by section, and its line count.
- Sections 1 to 9 say only what the records say; where they say nothing, "Not stated yet." Worked examples are marked as worked from the rules, not agreed (the $50 minimum on a three-hour non-member booking is the obvious one).
- Owners read as roles ("Stakeholder, hall committee chair"), and the Agreed by line gives the Sign-off's role and date.
- `HAL-Q-007` says it is already being built on a guess, and comes first in section 5.
- Turn 1's batch shows the new `Tech face:` line for `epic.md`. The reply after writing says the delivery team now has v2 through `HALL-12` and should be told so there, and what is still open.
