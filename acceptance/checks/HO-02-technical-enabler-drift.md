---
id: HO-02
version: 2
skills: [handoff]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# HO-02 · Handoff: drift on a Technical Enabler names its Enabled Requirements that changed

The hall's online payment account is a Technical Enabler, handed off with `pack-v1.md` on tech face `HALL-20`. At handoff it enabled three Requirements. Since then Margaret widened card payment to phone wallets, so one was withdrawn and replaced; the committee moved refunds to the treasurer, so another was withdrawn with nothing in its place; and the treasurer's monthly download was added to its `Enables:` line. The Operator asks what has changed since handoff: Jenny reports those three under Requirements, names nothing the pack already carries as it stands, leaves out the Questions and Decisions that bear on the Feature but not on the Technical Enabler, and writes nothing.

## Start

Sample v7, then after install the overlay below, committed as `Overlay: HAL-EPC-002 Technical Enabler handed off, its Requirements changed since`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/handoff-enabler"; cp -r "$F/hall-bookings/." "$H/" && cat "$F/unplaced-lines.md" >> "$H/requirements/unplaced.md" && cat "$F/source-rows.md" >> "$H/sources/index.md" && sed -i "/^- \[log\/\]/e cat $F/index-lines.md" "$H/index.md" && cat "$F/log-entries.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-002 Technical Enabler handed off, its Requirements changed since"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `epics/HAL-EPC-002-online-payment-account/epic.md`: `Technical Enabler: yes`, `Enables: HAL-REQ-001, HAL-REQ-016, HAL-REQ-017`, `## Covers` reading `None.`; `- Tech face: [HALL-20](https://example.atlassian.net/browse/HALL-20) · Pack: pack-v1.md · Handed off: 2026-11-12`; two N/A marks (Downstream, Rollout) dated 2026-11-11, both N/A rows in the pack.
- `epics/HAL-EPC-002-online-payment-account/pack-v1.md`: the only pack; section 4 lists `HAL-REQ-001`, `HAL-REQ-014` and `HAL-REQ-015`; section 3 is "None yet."; section 5 holds no Question.
- `requirements/unplaced.md`: `HAL-REQ-014` withdrawn 2026-11-14, replaced by `HAL-REQ-016`; `HAL-REQ-015` withdrawn 2026-11-14, nothing replaces it; `HAL-REQ-016` and `HAL-REQ-017` active, from `HAL-SRC-007`. `HAL-REQ-001` is unchanged in `HAL-FEA-001`.
- `questions/`: the sample's Questions and Answers on `HAL-FEA-001` and `HAL-REQ-001` (`HAL-Q-004`, `HAL-Q-008`, `HAL-Q-010`, `HAL-Q-013`, `HAL-ANS-001` among them); none names `HAL-EPC-002`.
- `epics/HAL-EPC-001-book-and-pay/`: the sample's handed-off Epic, with its own pack v1.

And `projects/court-bookings/` (untouched), and `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. What's changed on the online payment account spec since handoff?

## Key at proposal

Graded on `$TURNS/1.md`. `reqs() { awk '/^#+ .*Requirement/ || /^\*\*[^*]*Requirement[^*]*\*\*/ || /^Requirements?:? *$/ {f=1; next} /^#+ / || /^\*\*[^*]+\*\*/ {f=0} f' "$TURNS/1.md"; }` prints the lines under a Requirements heading (`#`, bold or plain, with or without words after it), up to the next heading.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Counts from the handed-off v1, through its tech face. `grep -cE 'v1|pack-v1' "$TURNS/1.md"` → 1 or more; `grep -c 'HALL-20' "$TURNS/1.md"` → 1 or more.
- The replaced Enabled Requirement names what replaced it, on its line. `grep 'HAL-REQ-014' "$TURNS/1.md" | grep -c 'HAL-REQ-016'` → 1 or more.
- The withdrawn Enabled Requirement says so. `grep 'HAL-REQ-015' "$TURNS/1.md" | grep -ci 'withdrawn'` → 1 or more.
- The newly enabled Requirement is named. `grep -c 'HAL-REQ-017' "$TURNS/1.md"` → 1 or more.
- All three sit under a Requirements heading. `reqs | grep -oE 'HAL-REQ-01[457]' | sort -u | wc -l` → `3`.
- The delta alone: the Enabled Requirement the pack carries unchanged is named nowhere. `grep -c 'HAL-REQ-001' "$TURNS/1.md"` → `0`.
- Only the Technical Enabler's records: no Question or Answer that bears on the Feature but does not name it. `grep -cE 'HAL-Q-0|HAL-ANS-0' "$TURNS/1.md"` → `0`.
- No newer pack offered for handoff: v2 is named only as the pack still to write. `grep -ciE 'hand off.*v2|not handed (over|off)' "$TURNS/1.md"` → `0`.
- The replacement is not listed again as newly enabled. `grep 'HAL-REQ-016' "$TURNS/1.md" | grep -v 'HAL-REQ-014' | grep -ci 'newly'` → `0`.
- No court items, no Source IDs. `grep -c 'CRT-' "$TURNS/1.md"` → `0`; `grep -c 'HAL-SRC-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 1.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.

## By eye

- Turn 1 leads with one line in the "engineers have v1 (HALL-20, handed off 2026-11-12); since then: …" shape, counting the Requirement changes.
- The Requirements heading holds three short lines: `HAL-REQ-014` replaced by `HAL-REQ-016`, `HAL-REQ-015` withdrawn with nothing in its place, `HAL-REQ-017` newly enabled. `HAL-REQ-016` is not listed again as newly enabled.
- No other heading: no Decisions, facts, Questions, N/A marks or Sign-offs.
- The next step says whether these are worth a v2 is the Operator's call, and offers "write the pack for the online payment account spec".
