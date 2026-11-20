---
id: SL-05
version: 3
skills: [slice]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# SL-05 · Slicing a mapped Project turns its enablers into a Technical Enabler and an Enabler Story

The hall Project has a story map with two enablers the engineers named: a card payment account with the bank (a Technical Enabler, enabling the walking-skeleton booking and Book and pay) and an email sending service (an Enabler Story for the caretaker's list). The Operator asks Jenny to slice the Project. The batch says what each enabler becomes before anything is written. After confirm, the card payment account is a Technical Enabler Epic in the Feature that needs it first, naming the Requirements it enables, and every Epic covering a Requirement it enables depends on it, the handed-off one aside; the email sending service is an Enabler Story line in the caretaker's list Epic; the map's `## Enablers` no longer lists either; no pain point is raised; and everything lands in one commit.

## Start

Sample v7, then after install the mapped state laid over it from the frozen fixture `acceptance/fixtures/storymap/mapped/` (CP-10's result), committed as `[2026-11-16] capture | HAL-SRC-006 Story map session of 2026-11-16`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/storymap/mapped"; cp -r "$F/hall-bookings/." "$H/" && cat "$F/log-entry.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-16] capture | HAL-SRC-006 Story map session of 2026-11-16"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `storymap.md`: `HAL-REQ-014` and `HAL-REQ-016` (book and pay in the walking skeleton) in `HAL-MIL-001` (Walking skeleton (hirers), internal); `HAL-REQ-001`, `HAL-REQ-005`, `HAL-REQ-011` (the caretaker's 6 pm list) and `HAL-REQ-015` in `HAL-MIL-002`. `## Enablers` lists `Card payment account with the bank` (Kind: Technical Enabler, Enables: `HAL-REQ-016`, `HAL-REQ-001`) and `Email sending service` (Kind: Enabler Story, Enables: `HAL-REQ-011`), each with `Depends on: none`.
- `features/HAL-FEA-001-book-and-pay.md` (holds `HAL-REQ-001`; its Epic `HAL-EPC-001` is handed off, so it gains no Depends on line) and `features/HAL-FEA-002-cancel-a-booking.md` (holds `HAL-REQ-005`; no Epic yet).
- `requirements/unplaced.md`: `HAL-REQ-008` to `HAL-REQ-016`. No `HAL-ENS-` ID is used anywhere yet.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Slice the hall bookings initiative.
2. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Both enablers named, with what each becomes. `grep -ci 'card payment' "$TURNS/1.md"` → 1 or more; `grep -ci 'email sending' "$TURNS/1.md"` → 1 or more; `grep -ci 'technical enabler' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-ENS-001' "$TURNS/1.md"` → 1 or more.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more.
- The Technical Enabler is not flagged as a second Epic. `grep -i 'second spec' "$TURNS/1.md" | grep -ciE 'card payment|technical enabler'` → `0`. (A second Spec offered for an unplaced Requirement of the handed-off Feature is another matter.)
- No leak-trap items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 2. `P="$WS/projects/hall-bookings"`, `TE=$(grep -lx 'Technical Enabler: yes' "$P"/epics/*/epic.md)`, and `cov() { awk 'FNR==1{s=0} /^## /{s=($0=="## Covers")} s' "$@" | grep -oE 'HAL-REQ-[0-9]{3}'; }` (the Requirement IDs under `## Covers` in the files given).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] slice \| '` → `1`; `grep -cxF "## $(git -C "$WS" log -1 --format=%s)" "$P"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only slicing files changed, the map included. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(features/[^/]+\.md|epics/[^/]+/epic\.md|milestones/HAL-MIL-[0-9]{3}-[^/]+\.md|storymap\.md|requirements/unplaced\.md|index\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- The map is unchanged outside `## Enablers`. `diff <(git -C "$WS" show "$BASE":projects/hall-bookings/storymap.md | awk '/^## /{s=($0=="## Enablers")} !s') <(awk '/^## /{s=($0=="## Enablers")} !s' "$P/storymap.md")` → empty.
- No enabler left on the map; each Technical Enabler names what it enables, covers nothing, and every Epic covering what it enables depends on it, handed-off ones aside. `python3 "$REPO/acceptance/headless/graders/SL-05/enablers.py" "$P"` → empty. The script prints each enabler still under `## Enablers`, each Technical Enabler with no `Enables:` line or with Requirements under `## Covers`, and each Epic not handed off that covers an enabled Requirement without listing the Technical Enabler under `## Depends on`.
- One Technical Enabler, the card payment account. `echo "$TE" | grep -c .` → `1`; `head -1 "$TE" | grep -ciE 'card|payment|bank'` → `1`.
- It enables what the map says. `grep '^Enables:' "$TE" | grep -c 'HAL-REQ-016'` → `1`; `grep '^Enables:' "$TE" | grep -c 'HAL-REQ-001'` → `1`.
- The map's `## Enablers` reads `None.` `awk '/^## /{s=($0=="## Enablers")} s' "$P/storymap.md" | grep -cx 'None.'` → `1`.
- It belongs to the Feature that needs it first: the one holding the walking-skeleton booking, or, while that stays unplaced (its Feature's Spec is handed off), the one holding `HAL-REQ-001`. `F=$(grep -l '^- \*\*HAL-REQ-016\*\*' "$P"/features/HAL-FEA-*.md || grep -l '^- \*\*HAL-REQ-001\*\*' "$P"/features/HAL-FEA-*.md); [ "$(sed -n 's/^Feature: //p' "$TE")" = "$(basename "$F" | cut -c1-11)" ] && echo same` → `same`.
- The email sending service is one Enabler Story, in the Epic covering the caretaker's list. `grep -h '^- \*\*HAL-ENS-[0-9]\{3\}\*\* ' "$P"/epics/*/epic.md | grep -ci 'email'` → `1`; `cov $(grep -l '^- \*\*HAL-ENS-[0-9]\{3\}\*\* .*[Ee]mail' "$P"/epics/*/epic.md) </dev/null | grep -cx 'HAL-REQ-011'` → `1`.
- No pain point recorded. `grep -l '^Pain point:' "$P"/epics/*/epic.md "$P"/features/*.md | wc -l` → `0`.
- Every Feature has exactly one Epic besides its Technical Enablers. `for f in "$P"/features/HAL-FEA-*.md; do grep -lx "Feature: $(basename "$f" | cut -c1-11)" "$P"/epics/*/epic.md | xargs -r grep -Lx 'Technical Enabler: yes' | wc -l; done | sort -u` → `1`.
- The handed-off Epic is not touched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md` → empty.
- Every Requirement line is kept, each in exactly one place, byte for byte. `diff <(git -C "$WS" grep -h '^- \*\*HAL-REQ-' "$BASE" -- projects/hall-bookings/features projects/hall-bookings/requirements | sort) <(grep -rh '^- \*\*HAL-REQ-' "$P"/features "$P"/requirements | sort)` → empty.
- No Requirement covered by two Epics. `cov "$P"/epics/*/epic.md | sort | uniq -d` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- The batch shows the Technical Enabler's `epic.md` with `Technical Enabler: yes`, its `Enables:` line and `## Covers` reading `None.`, and says which Epics depend on it.
- The batch says `HAL-EPC-001` is handed off, so it does not gain the Depends on line now; it waits for the next pack version.
- The card payment account is not flagged as a second Spec, though its Feature also has its own.
