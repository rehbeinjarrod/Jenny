---
id: SL-06
version: 1
skills: [slice]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# SL-06 · A Technical Enabler that enables no Requirement is a pain point until the Operator gives a reason

The hall Project has no story map. The Operator asks Jenny to slice it and to add a Technical Enabler for a test copy of the booking system, saying it enables no Requirement in particular. Jenny flags it as a pain point, suggests a re-slice (naming the Requirements it enables, or an Enabler Story inside an Epic), and asks the Operator's reason before writing it. The Operator gives a reason. After confirm, the Technical Enabler is an Epic with `Technical Enabler: yes`, no `Enables:` line, nothing under Covers, and a `Pain point:` line carrying the Operator's reason, and everything lands in one commit.

## Start

Sample v7 as it is. No fixtures. The key relies on, in `projects/hall-bookings/`:

- No `storymap.md`.
- `requirements/unplaced.md`: `HAL-REQ-008` to `HAL-REQ-013`.
- `features/HAL-FEA-001-book-and-pay.md` with its one Epic `epics/HAL-EPC-001-book-and-pay/epic.md` (handed off), and `features/HAL-FEA-002-cancel-a-booking.md` with no Epic yet.
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Slice the hall bookings initiative, and add a Technical Enabler for a test copy of the booking system. It doesn't enable any requirement in particular.
2. Keep it as it is: the council's IT team won't let anything go live until it has run on a test copy.
3. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`, and after turn 2 on `$TURNS/2.md` where a line says so.

- Nothing written, after each turn. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Turn 1, flagged as a pain point. `grep -ci 'pain point' "$TURNS/1.md"` → 1 or more; `grep -ci 'technical enabler' "$TURNS/1.md"` → 1 or more.
- Turn 1, a re-slice suggested. `grep -ciE 're-?slice' "$TURNS/1.md"` → 1 or more.
- Turn 1, asks for the reason. `grep -ci 'waiting for your reason' "$TURNS/1.md"` → 1 or more.
- Turn 2, still a pain point, in a batch. `grep -ci 'pain point' "$TURNS/2.md"` → 1 or more; `grep -ci 'nothing is written yet' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 3. `P="$WS/projects/hall-bookings"`, `TE=$(grep -lx 'Technical Enabler: yes' "$P"/epics/*/epic.md)`, and `cov() { awk 'FNR==1{s=0} /^## /{s=($0=="## Covers")} s' "$@" | grep -oE 'HAL-REQ-[0-9]{3}'; }` (the Requirement IDs under `## Covers` in the files given).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] slice \| '` → `1`; `grep -cxF "## $(git -C "$WS" log -1 --format=%s)" "$P"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only slicing files changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(features/[^/]+\.md|epics/[^/]+/epic\.md|requirements/unplaced\.md|index\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- One Technical Enabler, the test copy. `echo "$TE" | grep -c .` → `1`; `head -1 "$TE" | grep -ciE 'test'` → `1`.
- It enables nothing and covers nothing. `grep -c '^Enables:' "$TE"` → `0`; `cov "$TE" | wc -l` → `0`.
- It records the pain point with the Operator's reason. `grep '^Pain point:' "$TE" | grep -ci 'enabl'` → `1`; `grep '^Pain point:' "$TE" | grep -ci 'council'` → `1`.
- No other pain point recorded. `grep -l '^Pain point:' "$P"/epics/*/epic.md "$P"/features/*.md | wc -l` → `1`.
- Every Feature has exactly one Epic besides its Technical Enablers. `for f in "$P"/features/HAL-FEA-*.md; do grep -lx "Feature: $(basename "$f" | cut -c1-11)" "$P"/epics/*/epic.md | xargs -r grep -Lx 'Technical Enabler: yes' | wc -l; done | sort -u` → `1`.
- The handed-off Epic is not touched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md` → empty.
- Every Requirement line is kept, each in exactly one place, byte for byte. `diff <(git -C "$WS" grep -h '^- \*\*HAL-REQ-' "$BASE" -- projects/hall-bookings/features projects/hall-bookings/requirements | sort) <(grep -rh '^- \*\*HAL-REQ-' "$P"/features "$P"/requirements | sort)` → empty.
- No Requirement covered by two Epics. `cov "$P"/epics/*/epic.md | sort | uniq -d` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|open item|spec'` → `0`.

## By eye

- Turn 1 says in plain words why a Technical Enabler that enables nothing is a pain point: nothing ties it to the business outcome, so nobody can tell when it is needed or done.
- Turn 1 suggests naming the Requirements it enables, or making it an Enabler Story inside the Epic that needs it first.
- Turn 1 proposes a Feature for it and lets the Operator pick another.
