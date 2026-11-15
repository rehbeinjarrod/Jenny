---
id: SL-01
version: 5
skills: [slice]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# SL-01 · Vertical Features, one Epic each

The Operator asks Jenny to slice the hall Project. Jenny proposes Features for the unplaced Requirements, each a vertical slice a Stakeholder could see and sign off on its own, and one Epic for every Feature that has none, as one confirm-then-write batch. The phone-screen Requirement runs across every hirer page, so it is not given a Feature of its own: it sits in one Feature, is covered by that Feature's Epic, and the other Epics list it under **Applies here too**. After confirm, Requirement lines move byte for byte, no Requirement is covered by two Epics, and everything lands in one commit.

Grader: `acceptance/headless/graders/SL-01.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

Sample v7 as it is. No fixtures. The key relies on, in `projects/hall-bookings/`:

- `requirements/unplaced.md`: `HAL-REQ-008` (door code in the confirmation email, from v1) and, from `HAL-SRC-005`, `HAL-REQ-009` (see upcoming bookings), `HAL-REQ-010` (move a booking), `HAL-REQ-011` (caretaker's 6 pm list), `HAL-REQ-012` (what the list gives), `HAL-REQ-013` (every hirer page works on a phone screen).
- `features/HAL-FEA-001-book-and-pay.md` with its Epic `epics/HAL-EPC-001-book-and-pay/epic.md` (handed off), and `features/HAL-FEA-002-cancel-a-booking.md` with no Epic yet (`HAL-REQ-005`, `HAL-REQ-007`; `HAL-REQ-006` withdrawn).
- `features/index.md` and `index.md`.

And `projects/court-bookings/` (the leak trap, IDs start `CRT-`), and `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. Slice the hall bookings initiative.
2. Yes, write it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Places every new Requirement. Each → 1 or more: `grep -c 'HAL-REQ-009' "$TURNS/1.md"`, `grep -c 'HAL-REQ-010' "$TURNS/1.md"`, `grep -c 'HAL-REQ-011' "$TURNS/1.md"`, `grep -c 'HAL-REQ-012' "$TURNS/1.md"`, `grep -c 'HAL-REQ-013' "$TURNS/1.md"`.
- Gives the Feature with no Epic its Epic. `grep -c 'HAL-FEA-002' "$TURNS/1.md"` → 1 or more.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more.
- No leak-trap items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `P="$WS/projects/hall-bookings"`, `NEW=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- 'projects/hall-bookings/epics/*/epic.md')`, and `cov() { awk 'FNR==1{s=0} /^## /{s=($0=="## Covers")} s' "$@" | grep -oE 'HAL-REQ-[0-9]{3}'; }` (the Requirement IDs under `## Covers` in the files given).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] slice \| '` → `1`; `grep -cxF "## $(git -C "$WS" log -1 --format=%s)" "$P"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only slicing files changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(features/[^/]+\.md|epics/[^/]+/epic\.md|requirements/unplaced\.md|index\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- Every new Requirement is in exactly one Feature, its line moved byte for byte. `for r in HAL-REQ-009 HAL-REQ-010 HAL-REQ-011 HAL-REQ-012 HAL-REQ-013; do grep -l "^- \*\*$r\*\*" "$P"/features/HAL-FEA-*.md | wc -l; done | sort -u` → `1`; `diff <(git -C "$WS" show "$BASE":projects/hall-bookings/requirements/unplaced.md | grep -E '^- \*\*HAL-REQ-(009|01[0-3])\*\*' | sort) <(grep -hE '^- \*\*HAL-REQ-(009|01[0-3])\*\*' "$P"/features/HAL-FEA-*.md | sort)` → empty.
- Gone from unplaced. `grep -cE 'HAL-REQ-(009|01[0-3])\b' "$P/requirements/unplaced.md"` → `0`.
- Every Feature has exactly one Epic. `for f in "$P"/features/HAL-FEA-*.md; do grep -lx "Feature: $(basename "$f" | cut -c1-11)" "$P"/epics/*/epic.md | wc -l; done | sort -u` → `1`.
- No Requirement covered by two Epics. `cov "$P"/epics/*/epic.md | sort | uniq -d` → empty.
- Every new and active Requirement of the cancel Feature is covered. `for r in HAL-REQ-005 HAL-REQ-007 HAL-REQ-009 HAL-REQ-010 HAL-REQ-011 HAL-REQ-012 HAL-REQ-013; do cov "$P"/epics/*/epic.md | grep -cx "$r"; done | sort -u` → `1`; `cov "$P"/epics/*/epic.md | grep -c 'HAL-REQ-006'` → `0`.
- An Epic covers only Requirements of its own Feature. `for e in "$P"/epics/*/epic.md; do f=$(sed -n 's/^Feature: //p' "$e"); for r in $(cov "$e"); do grep -q "^- \*\*$r\*\*" "$P"/features/"$f"-*.md || echo "$r not in $f"; done; done` → empty.
- The handed-off Epic's Covers is unchanged. `cov "$P"/epics/HAL-EPC-001-book-and-pay/epic.md | tr '\n' ' '` → `HAL-REQ-001 HAL-REQ-002 HAL-REQ-003 HAL-REQ-004 `.
- The phone-screen Requirement is not a Feature on its own, and applies to another Epic. `grep -cE '^- \*\*HAL-REQ-' $(grep -l '^- \*\*HAL-REQ-013\*\*' "$P"/features/HAL-FEA-*.md) </dev/null` → 2 or more; `awk 'FNR==1{s=0} /^## /{s=($0=="## Applies here too")} s' "$P"/epics/*/epic.md | grep -c 'HAL-REQ-013'` → 1 or more.
- Each new Epic has the `epic.md` shape, no status, and its folder starts with its ID. `for e in $NEW; do grep -E '^## ' "$WS/$e" | tr '\n' '|'; echo; done | sort -u` → `## Covers|## Applies here too|## Depends on|## External items|## Left out|`; `for e in $NEW; do grep -c '^Status:' "$WS/$e"; done | sort -u` → `0`; `for e in $NEW; do id=$(sed -n 's/^Epic: //p' "$WS/$e"); case "$e" in */epics/"$id"-*/epic.md) ;; *) echo "$e";; esac; done` → empty.
- No pain point recorded. `grep -l '^Pain point:' "$P"/epics/*/epic.md "$P"/features/*.md | wc -l` → `0`.
- IDs unique. `ls "$P/features" | grep -oE '^HAL-FEA-[0-9]{3}' | sort | uniq -d` → empty; `ls "$P/epics" | grep -oE '^HAL-EPC-[0-9]{3}' | sort | uniq -d` → empty.
- Indexes list every Feature and Epic. `for f in "$P"/features/HAL-FEA-*.md; do grep -c "\[$(basename "$f" | cut -c1-11)\]" "$P/features/index.md"; done | sort -u` → `1`; `for e in "$P"/epics/*/epic.md; do grep -c "epics/$(basename "$(dirname "$e")")/epic.md" "$P/index.md"; done | sort -u` → `1`.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- Each proposed Feature has a non-technical one-line description of what a hirer, the caretaker or the committee gets.
- The batch says where `HAL-REQ-013` sits, why it is not a Feature of its own, and that the Operator can pick another Epic to cover it.
- What happens to `HAL-REQ-008`: placed (and said that `HAL-EPC-001` is handed off), or left unplaced with a reason.
- The reply after writing names Decision coverage on one of the new Epics as the next step.
