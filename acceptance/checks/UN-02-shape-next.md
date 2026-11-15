---
id: UN-02
version: 6
skills: [up-next]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# UN-02 · Shape next: top 5 by Score, parked left out, then shape the top one

The Operator asks what is up next in the hall Project. Jenny's Shape next list holds the top 5 `open` Questions, building-on-a-guess first, then by Score, ties by soonest Needed by, each with its score, and leaves out the sixth, the parked one and every answered one. The Operator then shapes the top one: Jenny proposes the plan fields from People and drafts the ask in chat, and after confirm writes only the plan fields and status, in one commit.

Grader: `acceptance/headless/graders/UN-02.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

Sample v7 as it is. No fixtures. The key relies on, in `projects/hall-bookings/questions/`:

- `HAL-Q-007-member-rate-for-guests.md`: open, Score 3, building on a guess (`yes`), Needed by `HAL-EPC-001`. Ranks first.
- `HAL-Q-009-late-finish.md`: open, Score 9. Second.
- `HAL-Q-008-who-sees-bookings.md`: open, Score 6, Needed by 2026-11-20. Third (ties with `HAL-Q-003` on Score, sooner).
- `HAL-Q-003-committee-cancels.md`: open, Score 6, Needed by 2026-12-01. Fourth.
- `HAL-Q-010-responsible-adult.md`: open, Score 4. Fifth.
- `HAL-Q-011-cleaning-fee.md`: open, Score 3, not on a guess. Sixth: left out.
- `HAL-Q-005-photo-gallery.md`: parked. `HAL-Q-001`, `HAL-Q-002`: answered. `HAL-Q-006`: withdrawn.
- `index.md`: one row per Question, with its status and Score.

And `projects/hall-bookings/project.md` (People: Margaret Osei is the only Stakeholder), `projects/court-bookings/` (the leak trap, IDs start `CRT-`), and `veneer.md` (Question shown as Open item).

## Operator script

1. What's up next for the hall bookings initiative?
2. Yes, shape the top one.
3. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`, and after turn 2 on `$TURNS/2.md` where a line says so.

- Nothing written, after each turn. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Turn 1, the top 5 in rank order. `for q in HAL-Q-007 HAL-Q-009 HAL-Q-008 HAL-Q-003 HAL-Q-010; do grep -n -m1 "$q" "$TURNS/1.md" | cut -d: -f1; done | sort -nc && echo ordered` → `ordered`; `for q in HAL-Q-007 HAL-Q-009 HAL-Q-008 HAL-Q-003 HAL-Q-010; do grep -c "$q" "$TURNS/1.md"; done | grep -cx 0` → `0`.
- Turn 1, each with its score on its own line. Each → 1 or more: `grep 'HAL-Q-007' "$TURNS/1.md" | grep -ciE 'score:? *3\b'`, `grep 'HAL-Q-009' "$TURNS/1.md" | grep -ciE 'score:? *9\b'`, `grep 'HAL-Q-008' "$TURNS/1.md" | grep -ciE 'score:? *6\b'`, `grep 'HAL-Q-003' "$TURNS/1.md" | grep -ciE 'score:? *6\b'`, `grep 'HAL-Q-010' "$TURNS/1.md" | grep -ciE 'score:? *4\b'`.
- Turn 1, the guess flagged. `grep 'HAL-Q-007' "$TURNS/1.md" | grep -ciE 'guess'` → 1 or more.
- Turn 1, only five: the sixth, the parked, answered and withdrawn ones left out. `grep -cE 'HAL-Q-(011|005|001|002|006)\b' "$TURNS/1.md"` → `0`.
- Turn 1, ends by offering to shape the top one. `tail -n 3 "$TURNS/1.md" | grep -c 'HAL-Q-007'` → 1 or more.
- Turn 1, no leak-trap items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.
- Turn 2, the plan for `HAL-Q-007`. `grep -c 'HAL-Q-007' "$TURNS/2.md"` → 1 or more; `grep -c 'Margaret Osei' "$TURNS/2.md"` → 1 or more; `grep -i 'technique' "$TURNS/2.md" | grep -ciE 'message|conversation|workshop|document review|demo or prototype|spike'` → 1 or more; `grep -i 'chase by' "$TURNS/2.md" | grep -cE '[0-9]{4}-[0-9]{2}-[0-9]{2}'` → 1 or more.
- Turn 2, a batch. `grep -ci 'nothing is written yet' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 3. `P="$WS/projects/hall-bookings"`, `Q="projects/hall-bookings/questions/HAL-Q-007-member-rate-for-guests.md"`.

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] up-next \| .*HAL-Q-007'` → `1`; `grep -cE '^## \[[0-9]{4}-[0-9]{2}-[0-9]{2}\] up-next \| .*HAL-Q-007' "$P"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Exactly these files changed, the log in the run's month. `diff <(git -C "$WS" diff --name-only "$BASE" HEAD) <(printf '%s\n' "projects/hall-bookings/log/$(date +%F | cut -c1-7).md" "$Q" projects/hall-bookings/questions/index.md)` → empty.
- Only the plan fields and status changed in the Question. `git -C "$WS" diff -U0 "$BASE" HEAD -- "$Q" | grep -E '^[-+]' | grep -vE '^(\+\+\+|---) ' | grep -vE '^[-+](Status|Ask|Technique|Chase by): '` → empty.
- The plan. Each → `1`: `grep -cx 'Status: chasing' "$WS/$Q"`, `grep -cx 'Ask: Margaret Osei' "$WS/$Q"`, `grep -cxE 'Technique: (message|conversation|workshop|document review|demo or prototype|delivery-team Spike)' "$WS/$Q"`, `grep -cxE 'Chase by: [0-9]{4}-[0-9]{2}-[0-9]{2}' "$WS/$Q"`.
- The ask has not gone out. `grep -c '^Asked:' "$WS/$Q"` → `0`. (The draft is not stored: the line above it allows no other change to the file.)
- The index row moves to chasing, score kept, no other row touched. `grep 'HAL-Q-007' "$P/questions/index.md" | grep -cE '\| *chasing *\| *3 *\|'` → `1`; `git -C "$WS" diff -U0 "$BASE" HEAD -- projects/hall-bookings/questions/index.md | grep -E '^[-+]\|' | grep -vc 'HAL-Q-007'` → `0`.
- No score changed anywhere. `git -C "$WS" diff "$BASE" HEAD | grep -cE '^[-+](Impact|Uncertainty|Score|Score reason):'` → `0`.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- Each Shape next line gives the score reason in a few words.
- Turn 2 drafts the wording of the ask for Margaret in chat, ready to paste, and says it is not stored.
- Turn 2 proposes the Technique and Chase by with a reason, open to amend by number.
- Turn 3 says to tell Jenny when the ask has gone out, so `Asked:` can be set.
