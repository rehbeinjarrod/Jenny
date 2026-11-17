---
id: UN-01
version: 6
skills: [up-next]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# UN-01 · Chase now: overdue first, handed-off nudge, no leak-trap items

The Operator asks what to chase next in the hall Project. Jenny lists the `chasing` Questions with the overdue ones first, each with who was asked and how many days overdue, nudges the handed-off Epic with the date of its last check, and pulls in nothing from the court Project. The list writes nothing and changes no status or score.

## Start

Sample v7 as it is. No fixtures. The run's date falls after 2026-11-10 and before 2027-06-30, so two chasing Questions are overdue and one is not yet due. `$D_012` and `$D_004`, set in **Key at proposal**, are the days from each Chase by date to the run's date.

The key relies on:

- `projects/hall-bookings/questions/HAL-Q-012-door-code-by-text.md`: chasing, Ask Ravi Kumar, Chase by 2026-11-08 (the most overdue).
- `projects/hall-bookings/questions/HAL-Q-004-cash-deposits.md`: chasing, Ask Margaret Osei, Chase by 2026-11-10.
- `projects/hall-bookings/questions/HAL-Q-013-meeting-room.md`: chasing, Ask Margaret Osei, Chase by 2027-06-30, ask not sent yet (no `Asked:` line).
- `projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md`: handed off (Tech face line), last checked 2026-11-09 per `projects/hall-bookings/log/2026-11.md`.
- `projects/hall-bookings/questions/`: `HAL-Q-001` and `HAL-Q-002` answered, `HAL-Q-005` parked, `HAL-Q-006` withdrawn.
- `projects/court-bookings/questions/CRT-Q-002-junior-bookings.md`: the leak trap, chasing and overdue, Ask Joe Park.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. What should I chase next in the hall bookings initiative?

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`. `D_012=$(( ($(date -ud "$(date +%F)" +%s) - $(date -ud 2026-11-08 +%s)) / 86400 ))`, `D_004=$(( ($(date -ud "$(date +%F)" +%s) - $(date -ud 2026-11-10 +%s)) / 86400 ))`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Lists every chasing Question. Each → 1 or more: `grep -c 'HAL-Q-012' "$TURNS/1.md"`, `grep -c 'HAL-Q-004' "$TURNS/1.md"`, `grep -c 'HAL-Q-013' "$TURNS/1.md"`.
- Overdue first, most overdue at the top. `for q in HAL-Q-012 HAL-Q-004 HAL-Q-013; do grep -n -m1 "$q" "$TURNS/1.md" | cut -d: -f1; done | sort -nc && echo ordered` → `ordered`.
- Who was asked. `grep -c 'Ravi Kumar' "$TURNS/1.md"` → 1 or more; `grep -c 'Margaret Osei' "$TURNS/1.md"` → 1 or more.
- Days overdue, on each Question's own line. `grep 'HAL-Q-012' "$TURNS/1.md" | grep -cE "\b$D_012 days?\b"` → 1 or more; `grep 'HAL-Q-004' "$TURNS/1.md" | grep -cE "\b$D_004 days?\b"` → 1 or more.
- Not yet due is not called overdue. `grep 'HAL-Q-013' "$TURNS/1.md" | grep -ci 'overdue'` → `0`.
- Handed-off nudge with the last check date, on one line. `grep 'HAL-EPC-001' "$TURNS/1.md" | grep -c '2026-11-09'` → 1 or more.
- Ends by offering to shape the top one. `tail -n 3 "$TURNS/1.md" | grep -c 'HAL-Q-007'` → 1 or more.
- No answered, parked or withdrawn Question. `grep -cE 'HAL-Q-00[1256]\b' "$TURNS/1.md"` → `0`.
- No leak-trap items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`; `grep -c 'Joe Park' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- `HAL-Q-013` reads as not yet due, and says the ask has not gone out.
- The nudge reads as a prompt to check the handed-off Spec for in-build business questions, not as a chasing Open item.
