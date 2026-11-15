---
id: SO-03
version: 4
skills: [signoff]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# SO-03 · Where an Epic stands: per Stakeholder, and a replaced Answer resets its Sign-off

The hall's book-and-pay Epic has pack v2 with three Decisions. Margaret agreed the deposit (`HAL-SO-001`), then on her view agreed the cleaning-fee Decision and pushed back on the late finish (`HAL-SO-002`, Question `HAL-Q-014`). Tom agreed the deposit in person (`HAL-SO-003`). Since then, the cleaning-fee Decision `HAL-ANS-005` was withdrawn and replaced by `HAL-ANS-007`. The Operator asks where the Epic stands. Jenny reads `signoffs.md` against the pack's Decisions as they are now and reports, per Stakeholder, what they agreed, disputed and have not yet looked at. Margaret's agreement to `HAL-ANS-005` does not carry to `HAL-ANS-007`. Nothing is written, and there is no yes/no "signed off".

Grader: `acceptance/headless/graders/SO-03.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

Sample v7, then after install the three overlays below, committed as `Overlay: HAL-EPC-001 Sign-offs and a replaced Decision`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/signoff/hall-bookings/." "$H/" && cp -r "$F/signoff-readback/hall-bookings/." "$H/" && cat "$F/signoff-readback/log-entries.md" >> "$H/log/2026-11.md" && cp -r "$F/signoff-standing/hall-bookings/." "$H/" && cat "$F/signoff-standing/log-entries.md" >> "$H/log/2026-11.md" && cat "$F/signoff-standing/unplaced-lines.md" >> "$H/requirements/unplaced.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 Sign-offs and a replaced Decision"
```

The key relies on, in `projects/hall-bookings/` after the overlays:

- `epics/HAL-EPC-001-book-and-pay/pack-v2.md`: the latest pack, section 3 holding `HAL-ANS-001`, `HAL-ANS-004` and `HAL-ANS-005`.
- `epics/HAL-EPC-001-book-and-pay/signoffs.md`: `HAL-SO-001` (Margaret Osei agreed `HAL-ANS-001`), `HAL-SO-002` (Margaret agreed `HAL-ANS-005`; not agreed `HAL-ANS-004` → `HAL-Q-014`), `HAL-SO-003` (Tom Achebe agreed `HAL-ANS-001`, in person).
- `questions/HAL-Q-011-cleaning-fee.md`: `HAL-ANS-005` withdrawn, `Replaced by: HAL-ANS-007`; `HAL-ANS-007` active (non-members pay a $40 cleaning fee).
- `questions/HAL-Q-014-late-finish-pushback.md`: open, `Affects: HAL-ANS-004`. `questions/HAL-Q-009-late-finish.md`: `HAL-ANS-004` active.
- `project.md` People: Dana Wells (Operator), Margaret Osei (Stakeholder), Ravi Kumar (engineer), Tom Achebe (Stakeholder).
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Where does the book and pay spec stand?

## Key at proposal

Graded on `$TURNS/1.md`. `who() { awk -v n="**$1**" 'index($0, n) == 1 {f=1; next} /^\*\*/{f=0} f' "$TURNS/1.md"; }` (one Stakeholder's block), `line() { who "$1" | grep "^- $2:"; }` (one labelled line in it).

- One block per Stakeholder, and no one else's. `grep -cE '^\*\*(Margaret Osei|Tom Achebe)\*\*' "$TURNS/1.md"` → `2`; `grep -cE '^\*\*(Dana Wells|Ravi Kumar)\*\*' "$TURNS/1.md"` → `0`.
- Each block has the three lines. `for p in 'Margaret Osei' 'Tom Achebe'; do for l in Agreed Disputed 'Not yet looked at'; do line "$p" "$l" | wc -l; done; done | sort -u` → `1`.
- Margaret agreed the deposit only. `line 'Margaret Osei' Agreed | grep -oE 'HAL-ANS-[0-9]{3}' | sort -u | tr '\n' ' '` → `HAL-ANS-001 `.
- Margaret disputes the late finish, through its Question. `line 'Margaret Osei' Disputed | grep -c 'HAL-ANS-004'` → `1`; `line 'Margaret Osei' Disputed | grep -c 'HAL-Q-014'` → `1`.
- The replaced Answer resets her Sign-off: the replacement is not yet looked at. `line 'Margaret Osei' 'Not yet looked at' | grep -c 'HAL-ANS-007'` → `1`; `line 'Margaret Osei' Agreed | grep -cE 'HAL-ANS-00[57]'` → `0`.
- Tom agreed the deposit only, and has not looked at the other two. `line 'Tom Achebe' Agreed | grep -oE 'HAL-ANS-[0-9]{3}' | sort -u | tr '\n' ' '` → `HAL-ANS-001 `; `line 'Tom Achebe' 'Not yet looked at' | grep -oE 'HAL-ANS-00[47]' | sort -u | tr '\n' ' '` → `HAL-ANS-004 HAL-ANS-007 `; `line 'Tom Achebe' Disputed | grep -c 'HAL-'` → `0`.
- The withdrawn Decision is not reported as standing. `grep -E '^- (Agreed|Disputed):' "$TURNS/1.md" | grep -c 'HAL-ANS-005'` → `0`.
- No yes/no "signed off", and nothing overdue. `grep -ciE 'signed[ -]off|overdue' "$TURNS/1.md"` → `0`.
- No court items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 1.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.

## By eye

- The reply leads with one line for the Epic: pack v2, three Decisions, and how many each Stakeholder has agreed.
- `HAL-ANS-007` reads as replacing `HAL-ANS-005`, which Margaret had agreed, so her agreement does not carry.
- The reply says pack v2 still shows `HAL-ANS-005`, and suggests writing a new pack.
- Unticked Decisions read as not yet looked at, never as agreed or late.
