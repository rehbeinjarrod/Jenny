---
id: HO-01
version: 4
skills: [handoff]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# HO-01 · Handoff: the drift report writes nothing; the Tech face line records the pack version given

The hall's book-and-pay Epic was handed off with `pack-v1.md` on tech face `HALL-12`, and `pack-v2.md` has been written since. The Operator asks what has changed since handoff: Jenny reports the drift against v1 (two Decisions since, one decided during build, three N/A marks, one Sign-off, and v2 written but not handed over) and writes nothing. Then the Operator hands off v2: Jenny proposes the new `Tech face:` line and writes it only after the yes, changing that one line of `epic.md`, in one commit. Asked again, the drift now counts from v2 and finds nothing new.

## Start

Sample v7, then after install the overlay below, committed as `Overlay: HAL-EPC-001 pack v2 for Sign-off`:

```sh
cp -r "$REPO/acceptance/fixtures/signoff/hall-bookings/." "$WS/projects/hall-bookings/" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 pack v2 for Sign-off"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `epics/HAL-EPC-001-book-and-pay/epic.md`: `- Tech face: [HALL-12](https://example.atlassian.net/browse/HALL-12) · Pack: pack-v1.md · Handed off: 2026-11-07`; three N/A marks (Downstream, Quality, Rollout) dated 2026-11-11.
- `epics/HAL-EPC-001-book-and-pay/pack-v1.md`: section 3 holds `HAL-ANS-001` only; section 5 holds `HAL-Q-007`, `HAL-Q-009`, `HAL-Q-008`, `HAL-Q-004`, `HAL-Q-010`, `HAL-Q-013`, `HAL-Q-011`; Appendix A has no N/A row.
- `epics/HAL-EPC-001-book-and-pay/pack-v2.md`: written 2026-11-11; section 3 holds `HAL-ANS-001`, `HAL-ANS-004`, `HAL-ANS-005`; Appendix A has the three N/A rows; `HAL-ANS-001` carries its Agreed by line.
- `questions/`: `HAL-ANS-004` (decision, owner Ravi Kumar, engineer) answers `HAL-Q-009`; `HAL-ANS-005` (decision, owner Margaret Osei) answers `HAL-Q-011`; both affect `HAL-REQ-003`, covered by the Epic. `HAL-ANS-003` (decision, 2026-11-08) affects `HAL-REQ-005`, in `HAL-FEA-002`: not this Epic's.
- `epics/HAL-EPC-001-book-and-pay/signoffs.md`: `HAL-SO-001`, 2026-11-10, Margaret Osei agreed `HAL-ANS-001`.

And `projects/court-bookings/` (untouched), and `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. What's changed on the book and pay spec since handoff?
2. Hand off the book and pay spec v2, tech face HALL-12.
3. Yes, go ahead.
4. What's changed on the book and pay spec since handoff now?

## Key at proposal

Graded after turn 1 on `$TURNS/1.md` (the drift report), and after turn 2 on `$TURNS/2.md` (the Handoff proposal), each before the next turn is sent.

After turn 1:

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Counts from the handed-off v1, through its tech face. `grep -cE 'v1|pack-v1' "$TURNS/1.md"` → 1 or more; `grep -c 'HALL-12' "$TURNS/1.md"` → 1 or more.
- Both Decisions since are listed. `for a in HAL-ANS-004 HAL-ANS-005; do grep -c "$a" "$TURNS/1.md"; done | grep -cx 0` → `0`.
- The engineer's Decision is a build Decision. `grep 'HAL-ANS-004' "$TURNS/1.md" | grep -ci 'during build'` → 1 or more.
- The three N/A marks since are listed. `for w in downstream quality rollout; do grep -ci "$w" "$TURNS/1.md"; done | grep -cx 0` → `0`.
- The delta alone: a Question v1 already carries, unchanged, is named nowhere. `grep -c 'HAL-Q-007' "$TURNS/1.md"` → `0`.
- The Sign-off since is listed. `grep -c 'HAL-SO-001' "$TURNS/1.md"` → 1 or more.
- The newer pack, not yet handed over, is named. `grep -cE 'v2|pack-v2' "$TURNS/1.md"` → 1 or more.
- Only this Epic's records: the other Feature's Decision stays out. `grep -c 'HAL-ANS-003' "$TURNS/1.md"` → `0`.
- No court items, no Source IDs. `grep -c 'CRT-' "$TURNS/1.md"` → `0`; `grep -c 'HAL-SRC-' "$TURNS/1.md"` → `0`.

After turn 2:

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- The proposal names the version and the tech face. `grep -c 'pack-v2.md' "$TURNS/2.md"` → 1 or more; `grep -c 'HALL-12' "$TURNS/2.md"` → 1 or more.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 4. `P="$WS/projects/hall-bookings"`, `E="$P/epics/HAL-EPC-001-book-and-pay/epic.md"`.

The Handoff:

- One commit: turn 3's; the second drift report wrote nothing. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] handoff \| '` → `1`; `cat "$P"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- Only `epic.md`, the Project index and the log changed. `git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE '^projects/hall-bookings/(epics/HAL-EPC-001-book-and-pay/epic\.md|index\.md|log/[0-9]{4}-[0-9]{2}\.md)$'` → empty.
- One line of `epic.md` changed. `git -C "$WS" diff --numstat "$BASE" HEAD -- "$E" | cut -f1,2` → `1	1`.
- The Tech face line names v2, the same work item, and today. `grep -cxF -e "- Tech face: [HALL-12](https://example.atlassian.net/browse/HALL-12) · Pack: pack-v2.md · Handed off: $(date +%F)" "$E"` → `1`; `grep -c 'Tech face:' "$E"` → `1`.
- Packs untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- 'projects/hall-bookings/epics/*/pack-v*.md'` → empty.
- Other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md projects/hall-bookings/questions projects/hall-bookings/project.md projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoffs.md` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD | grep '^+' | grep -ciwE 'initiative|open item|spec'` → `0`.

The second drift report:

- Counts from v2, which already carries both Decisions. `grep -cE 'v2|pack-v2' "$TURNS/4.md"` → 1 or more; `grep -cE 'HAL-ANS-00[45]' "$TURNS/4.md"` → `0`.

## By eye

- Turn 1 leads with one line in the "engineers have v1; …" shape: the version, the tech face and the date given, then the counts.
- Each change sits under a short heading of its kind (Decisions, facts, Questions, N/A marks, Sign-offs, in shown names), each with its ID and a few plain words; `HAL-ANS-004` says Ravi made it during the build.
- Turn 1 says v2 is written but not handed over, and offers "hand off … v2" rather than writing a new pack.
- Turn 2 shows the `Tech face:` line as it will read, and says the delivery team should be told v2 is theirs.
- Turn 4 says the delivery team has v2 and nothing has changed since.
