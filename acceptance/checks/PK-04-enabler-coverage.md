---
id: PK-04
version: 3
skills: [pack]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# PK-04 · Decision coverage of a Technical Enabler, with one shared N/A reason

The Operator asks Jenny to check coverage for the court Project's card payment account, a Technical Enabler. Jenny walks all 11 categories, reading the Requirements it enables for context only: only the Questions naming the Technical Enabler bear on it, so the Questions on the timetable and on booking rules stay out. The Operator marks three categories N/A in one reply with one shared reason. After confirm, that reason is recorded against each of the three categories in `epic.md`, the other gaps are new Questions for the Technical Enabler, and everything lands in one commit.

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

1. Check coverage for the card payment account spec.
2. Boundaries, states and examples are not applicable, all for one reason: its business rules belong to the booking and the timetable it makes possible. Keep everything else as you have it.
3. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`, and after turn 2 on `$TURNS/2.md` where a line says so. `cats() { for w in rules boundaries unwanted states variants data permissions downstream quality rollout examples; do grep -ci "$w" "$1"; done | grep -cx 0; }` (how many of the 11 categories a reply never names).

- Nothing written, after each turn. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- All 11 categories shown, after each turn. `cats "$TURNS/1.md"` → `0`; `cats "$TURNS/2.md"` → `0`.
- Turn 1, the Technical Enabler's own records cited: its open Question and its Decision. `grep -c 'CRT-Q-005' "$TURNS/1.md"` → 1 or more; `grep -cE 'CRT-ANS-001|CRT-Q-004' "$TURNS/1.md"` → 1 or more.
- Turn 1, Questions on the Enabled Requirements alone do not bear on it: no checklist row cites them. `grep '^|' "$TURNS/1.md" | grep -cE 'CRT-Q-00[23]'` → `0`.
- Turn 2, the shared reason is in the batch. `grep -ci 'makes possible' "$TURNS/2.md"` → 1 or more.
- A batch, after each turn. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more; `grep -ci 'nothing is written yet' "$TURNS/2.md"` → 1 or more.
- No hall items, after each turn. `grep -c 'HAL-' "$TURNS/1.md"` → `0`; `grep -c 'HAL-' "$TURNS/2.md"` → `0`.

## Key at write

Graded after turn 3. `P="$WS/projects/court-bookings"`, `E="$P/epics/CRT-EPC-002-card-payment-account/epic.md"`, `NEWQ=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/court-bookings/questions/CRT-Q-*.md')`, and `na() { awk '/^## /{s=($0=="## Not applicable")} s' "$E" | grep '^- '; }` (the N/A lines in `epic.md`).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] pack \| '` → `1`; `cat "$P"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only coverage files changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/court-bookings/(questions/[^/]+\.md|epics/CRT-EPC-002-card-payment-account/epic\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- The shared reason is recorded against each of the three categories, and only those. `na | wc -l` → `3`; `for c in Boundaries States Examples; do na | grep -c "^- \*\*$c\*\*:"; done | sort -u` → `1`.
- The same reason and date on each. `na | sed 's/^- \*\*[^*]*\*\*: //' | sort -u | wc -l` → `1`; `na | grep -ci 'makes possible'` → `3`.
- Nothing else in `epic.md` changed: lines only added. `git -C "$WS" diff --numstat "$BASE" HEAD -- projects/court-bookings/epics/CRT-EPC-002-card-payment-account/epic.md | cut -f2` → `0`.
- Coverage raised gap Questions, none for an N/A category. `echo "$NEWQ" | grep -c .` → 1 or more; `(cd "$WS" && cat $NEWQ </dev/null) | grep -cE '^Category: (Boundaries|States|Examples)$'` → `0`.
- Every new Question has the coverage shape, scored, for the Technical Enabler. `for q in $NEWQ; do f="$WS/$q"; i=$(sed -n 's/^Impact: //p' "$f"); u=$(sed -n 's/^Uncertainty: //p' "$f"); s=$(sed -n 's/^Score: //p' "$f"); [ "$((i*u))" = "$s" ] || echo "$q score"; grep -qE '^Category: (Rules|Boundaries|Unwanted behaviour|States|Variants|Data|Permissions|Downstream|Quality|Rollout|Examples)$' "$f" || echo "$q category"; grep -qE '^Affects: CRT-EPC-002' "$f" || echo "$q affects"; grep -qx 'Needed by: CRT-EPC-002' "$f" || echo "$q needed"; grep -qx 'Raised from: Decision coverage of CRT-EPC-002' "$f" || echo "$q raised"; done` → empty.
- Every new Question is in the index. `for q in $NEWQ; do grep -c "\[$(basename "$q" | cut -c1-9)\]" "$P/questions/index.md"; done | sort -u` → `1`.
- Existing Questions untouched. `git -C "$WS" diff --name-only --diff-filter=MD "$BASE" HEAD -- 'projects/court-bookings/questions/CRT-Q-*.md'` → empty.
- Hall records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings veneer.md workspace.md` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiatives?|open items?|specs?'` → `0`.

## By eye

- Turn 1's checklist cites `CRT-REQ-001` and `CRT-REQ-008` at most as context, never as what settles a category.
- Turn 1 may propose one shared N/A reason across several categories, naming them, and waits for the Operator's yes before marking any.
- Turn 2 shows the whole batch again with the three N/A lines as one item, each line in the Operator's words, and the Boundaries, States and Examples gap Questions gone.
