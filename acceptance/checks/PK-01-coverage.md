---
id: PK-01
version: 3
skills: [pack]
cursor-bench: false
repeat-at-gate: true
---

# PK-01 · Decision coverage raises every gap, and N/A is the Operator's call

The Operator asks Jenny to check coverage for the court timetable Epic. Jenny walks all 11 categories and shows each as settled (citing Requirement IDs), open (citing the Question already raised) or a gap, and proposes a scored Question for every gap, as one confirm-then-write batch. Two categories honestly do not apply; Jenny may say they look N/A but marks neither. The Operator marks one of them N/A with a reason and confirms. After confirm, every planted gap is a new Question tagged with its category, only the Operator's N/A is stored, with their reason, and everything lands in one commit.

## Start

Sample v7 as it is. No fixtures. The key relies on, in `projects/court-bookings/`:

- `features/CRT-FEA-002-see-which-courts-are-free.md`: `CRT-REQ-005` (which hours between 7 am and 10 pm each court is free, next 14 days), `CRT-REQ-006` (anyone can see it without signing in), `CRT-REQ-007` (a booked hour shows only as taken, never who booked it), `CRT-REQ-008` (an hour shows as taken once its booking is paid).
- `epics/CRT-EPC-001-see-which-courts-are-free/epic.md`: covers `CRT-REQ-005` to `CRT-REQ-008`; not handed off.
- `questions/CRT-Q-003-closed-court.md`: open, whether a court closed for repairs shows as closed or as taken (a state), `Affects: CRT-REQ-008`, `Needed by: CRT-EPC-001`.
- The planted state, by category: rules and permissions settled by those Requirements; states open on `CRT-Q-003`; boundaries, unwanted behaviour, variants (tennis and netball courts), quality, rollout (bookings already taken at the front desk) and examples (no worked case in any record) are gaps; data (the timetable keeps nothing of its own) and downstream (looking at it starts nothing and tells nobody) honestly do not apply.

And `projects/hall-bookings/` (untouched), and `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. Check coverage for the court timetable spec.
2. Downstream is not applicable: looking at the timetable starts nothing and tells nobody anything. Keep everything else as you have it.
3. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`, and after turn 2 on `$TURNS/2.md` where a line says so. `cats() { for w in rules boundaries unwanted states variants data permissions downstream quality rollout examples; do grep -ci "$w" "$1"; done | grep -cx 0; }` (how many of the 11 categories a reply never names).

- Nothing written, after each turn. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- All 11 categories shown, after each turn. `cats "$TURNS/1.md"` → `0`; `cats "$TURNS/2.md"` → `0`.
- Turn 1, quality walked by its ISO/IEC 25010 names. `for w in performance reliability security 'interaction capability' compatibility; do grep -ci "$w" "$TURNS/1.md"; done | grep -cx 0` → `0`.
- Turn 1, settled categories cite their Requirements. Each → 1 or more: `grep -c 'CRT-REQ-005' "$TURNS/1.md"`, `grep -c 'CRT-REQ-006' "$TURNS/1.md"`, `grep -c 'CRT-REQ-007' "$TURNS/1.md"`.
- Turn 1, the open category cites its Question. `grep -c 'CRT-Q-003' "$TURNS/1.md"` → 1 or more.
- Turn 1, N/A proposed and left to the Operator: data is said to look N/A, and the reply asks for a reason. `grep -iE 'data' "$TURNS/1.md" | grep -ciE 'looks? (like it is )?(n/a|not applicable)'` → 1 or more; `grep -iE 'n/a|not applicable' "$TURNS/1.md" | grep -ci 'reason'` → 1 or more.
- A batch, after each turn. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more; `grep -ci 'nothing is written yet' "$TURNS/2.md"` → 1 or more.
- No hall items, after each turn. `grep -c 'HAL-' "$TURNS/1.md"` → `0`; `grep -c 'HAL-' "$TURNS/2.md"` → `0`.
- (soft) Never says a renamed canonical term (Project, Epic, Question) outside code spans, after each turn. `sed 's/`[^`]*`//g' "$TURNS/<n>.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## Key at write

Graded after turn 3. `P="$WS/projects/court-bookings"`, `E="$P/epics/CRT-EPC-001-see-which-courts-are-free/epic.md"`, `NEWQ=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/court-bookings/questions/CRT-Q-*.md')`, and `na() { awk '/^## /{s=($0=="## Not applicable")} s' "$E" | grep '^- '; }` (the N/A lines in `epic.md`).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] pack \| '` → `1`; `cat "$P"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only coverage files changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/court-bookings/(questions/[^/]+\.md|epics/CRT-EPC-001-see-which-courts-are-free/epic\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- Every planted gap is raised as a Question tagged with its category. `for c in boundaries unwanted variants quality rollout examples; do (cd "$WS" && cat $NEWQ </dev/null) | grep -ciE "^Category: $c"; done | grep -cx 0` → `0`.
- Every new Question has the Question shape, scored, for this Epic. `for q in $NEWQ; do f="$WS/$q"; i=$(sed -n 's/^Impact: //p' "$f"); u=$(sed -n 's/^Uncertainty: //p' "$f"); s=$(sed -n 's/^Score: //p' "$f"); [ "$((i*u))" = "$s" ] || echo "$q score"; [ "$s" -le 2 ] && st=parked || st=open; grep -qx "Status: $st" "$f" || echo "$q status"; grep -qE '^Affects: .*CRT-EPC-001' "$f" || echo "$q affects"; grep -qE '^Category: (Rules|Boundaries|Unwanted behaviour|States|Variants|Data|Permissions|Downstream|Quality|Rollout|Examples)$' "$f" || echo "$q category"; grep -qx '## Answers' "$f" || echo "$q answers"; grep -qx 'Needed by: CRT-EPC-001' "$f" || echo "$q needed"; grep -qx 'Raised from: Decision coverage of CRT-EPC-001' "$f" || echo "$q raised"; done` → empty.
- Every new Question is in the index. `for q in $NEWQ; do grep -c "\[$(basename "$q" | cut -c1-9)\]" "$P/questions/index.md"; done | sort -u` → `1`.
- Existing Questions untouched. `git -C "$WS" diff --name-only --diff-filter=MD "$BASE" HEAD -- 'projects/court-bookings/questions/CRT-Q-*.md'` → empty.
- Only the Operator's N/A is stored, with their reason. `na | wc -l` → `1`; `na | grep -ci 'downstream'` → `1`; `na | grep -ciE 'nobody|starts nothing'` → `1`.
- Nothing else in `epic.md` changed: lines only added. `git -C "$WS" diff --numstat "$BASE" HEAD -- projects/court-bookings/epics/CRT-EPC-001-see-which-courts-are-free/epic.md | cut -f2` → `0`.
- Hall records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings veneer.md workspace.md` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|open item|spec'` → `0`.
- (soft) Reply after writing never says a renamed canonical term. `sed 's/`[^`]*`//g' "$TURNS/3.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## By eye

- Turn 1 shows the 11 categories in the fixed order, each with its state and what it cites, and says data (and perhaps downstream) looks N/A with why, asking for the Operator's reason rather than marking them.
- Gap Questions are plain one-sentence questions a Stakeholder could answer (plain words, not an EARS template), each with a sensible score reason. None repeats `CRT-Q-003`.
- Quality names the characteristics in business words and leaves out safety, or says why no harm is possible.
- Turn 2 shows the whole batch again under the same heading, with downstream as an N/A mark in the Operator's words and data still not N/A.
- The reply after writing says what is left open and points at what to chase next.
