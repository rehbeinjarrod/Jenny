---
id: SL-02
version: 3
skills: [slice]
cursor-bench: false
repeat-at-gate: false
---

# SL-02 · A second Epic and a horizontal Feature flagged, with a re-slice suggested

The Operator asks Jenny to slice the hall Project with two shapes Jenny pushes back on: a Feature holding only the phone-screen Requirement (horizontal: nothing a Stakeholder can see on its own) and a second Epic in Book and pay for the door code email. Jenny flags each as a pain point, suggests a re-slice for each, and asks the Operator's reason before writing either. The Operator gives a reason for the second Epic and drops the horizontal Feature. After confirm, Book and pay has two Epics, the second records the pain point with the Operator's reason, the handed-off Epic is not touched, the phone-screen Requirement sits in a vertical Feature, and everything lands in one commit.

## Start

Sample v7 as it is. No fixtures. The key relies on, in `projects/hall-bookings/`:

- `requirements/unplaced.md`: `HAL-REQ-008` (door code in the confirmation email), and `HAL-REQ-009` to `HAL-REQ-013` from `HAL-SRC-005`, `HAL-REQ-013` being every hirer page works on a phone screen.
- `features/HAL-FEA-001-book-and-pay.md` with its one Epic `epics/HAL-EPC-001-book-and-pay/epic.md` (handed off; Covers `HAL-REQ-001` to `HAL-REQ-004`), and `features/HAL-FEA-002-cancel-a-booking.md` with no Epic yet.

And `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. Slice the hall bookings initiative. Give the phone-screen requirement a Feature of its own, and put the door code email in a second spec under Book and pay.
2. Keep the second spec: the team building Book and pay already has its pack, and the door code email is going to a different team. For the phone screens, do it your way.
3. Yes, write it.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`, and after turn 2 on `$TURNS/2.md` where a line says so.

- Nothing written, after each turn. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Turn 1, both asks named. `grep -c 'HAL-REQ-013' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-REQ-008' "$TURNS/1.md"` → 1 or more.
- Turn 1, flagged as pain points. `grep -ci 'pain point' "$TURNS/1.md"` → 1 or more; `grep -ci 'horizontal' "$TURNS/1.md"` → 1 or more; `grep -ci 'second spec' "$TURNS/1.md"` → 1 or more.
- Turn 1, a re-slice suggested. `grep -ciE 're-?slice' "$TURNS/1.md"` → 1 or more.
- Turn 1, asks for the reason. `grep -ciE 'reason|why' "$TURNS/1.md"` → 1 or more.
- Turn 2, the second Epic is still a pain point, in a batch. `grep -ci 'pain point' "$TURNS/2.md"` → 1 or more; `grep -c 'HAL-REQ-008' "$TURNS/2.md"` → 1 or more; `grep -ci 'nothing is written yet' "$TURNS/2.md"` → 1 or more.
- (soft) After each turn, never says a renamed canonical term (Project, Epic, Question) outside code spans. `sed 's/`[^`]*`//g' "$TURNS/<n>.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## Key at write

Graded after turn 3. `P="$WS/projects/hall-bookings"`, `E1="$P/epics/HAL-EPC-001-book-and-pay/epic.md"`, `E2=$(grep -lx 'Feature: HAL-FEA-001' "$P"/epics/*/epic.md | grep -v HAL-EPC-001-)`, and `cov() { awk 'FNR==1{s=0} /^## /{s=($0=="## Covers")} s' "$@" | grep -oE 'HAL-REQ-[0-9]{3}'; }` (the Requirement IDs under `## Covers` in the files given).

- One commit. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] slice \| '` → `1`; `grep -cxF "## $(git -C "$WS" log -1 --format=%s)" "$P"/log/*.md` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Only slicing files changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(features/[^/]+\.md|epics/[^/]+/epic\.md|requirements/unplaced\.md|index\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- Every Requirement line is kept, each in exactly one place, byte for byte. `diff <(git -C "$WS" grep -h '^- \*\*HAL-REQ-' "$BASE" -- projects/hall-bookings/features projects/hall-bookings/requirements | sort) <(grep -rh '^- \*\*HAL-REQ-' "$P"/features "$P"/requirements | sort)` → empty.
- Book and pay has two Epics. `grep -lx 'Feature: HAL-FEA-001' "$P"/epics/*/epic.md | wc -l` → `2`.
- Every other Feature has exactly one Epic. `for f in "$P"/features/HAL-FEA-*.md; do id=$(basename "$f" | cut -c1-11); [ "$id" = HAL-FEA-001 ] || grep -lx "Feature: $id" "$P"/epics/*/epic.md | wc -l; done | sort -u` → `1`.
- The door code email is in Book and pay, covered by the second Epic, its line moved byte for byte. `grep -cxF -e "$(git -C "$WS" show "$BASE":projects/hall-bookings/requirements/unplaced.md | grep '^- \*\*HAL-REQ-008\*\*')" "$P/features/HAL-FEA-001-book-and-pay.md"` → `1`; `cov "$E2" | grep -cx 'HAL-REQ-008'` → `1`; `grep -c 'HAL-REQ-008' "$P/requirements/unplaced.md"` → `0`.
- The handed-off Epic is not touched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md` → empty.
- The second Epic records the pain point with the Operator's reason. `grep '^Pain point:' "$E2" | grep -ciE 'second'` → `1`; `grep '^Pain point:' "$E2" | grep -ci 'team'` → `1`.
- No other pain point recorded. `grep -l '^Pain point:' "$P"/epics/*/epic.md "$P"/features/*.md | wc -l` → `1`.
- No horizontal Feature: the phone-screen Requirement shares its Feature, and no Feature is about phones. `grep -cE '^- \*\*HAL-REQ-' $(grep -l '^- \*\*HAL-REQ-013\*\*' "$P"/features/HAL-FEA-*.md) </dev/null` → 2 or more; `grep -liE '^# HAL-FEA-[0-9]{3} · .*(phone|mobile|screen)' "$P"/features/*.md | wc -l` → `0`.
- No Requirement covered by two Epics. `cov "$P"/epics/*/epic.md | sort | uniq -d` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep -ciwE 'initiative|open item|spec'` → `0`.
- (soft) Reply after writing never says a renamed canonical term. `sed 's/`[^`]*`//g' "$TURNS/3.md" | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`.

## By eye

- Turn 1 says why each ask is a pain point in plain words, and the re-slice it suggests: for the door code, the next pack version of `HAL-EPC-001`; for the phone screens, keeping `HAL-REQ-013` in a vertical Feature and listing it under **Applies here too** elsewhere.
- Turn 1 does not write either shape without a reason, and says which item waits for one.
- Turn 2 drops the phone-screen Feature and shows the whole batch again under the same heading.
