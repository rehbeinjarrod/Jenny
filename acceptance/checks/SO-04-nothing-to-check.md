---
id: SO-04
version: 1
skills: [signoff]
cursor-bench: false
routing: false
inputs: []
promise: false
---

# SO-04 · A Sign-off view with nothing to check writes nothing

The hall's online payment account is a Technical Enabler: engineers named it as the set-up the book-and-pay Feature needs before anyone can pay a deposit online. Its pack v1 settles no Decision, leaves no Question open and builds on no guess. The Operator asks for Margaret's Sign-off view of it. Sorted, the view would hold no 🔴 item, no 🟠 call of hers and no ✅ Decision to check, so Jenny says there is nothing for Margaret to check and writes nothing: no view, no log entry, no commit.

## Start

Sample v7, then after install the overlay below, committed as `Overlay: HAL-EPC-002 Technical Enabler pack v1`:

```sh
H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/signoff-enabler"; cp -r "$F/hall-bookings/." "$H/" && sed -i "/^- \[log\/\]/e cat $F/index-lines.md" "$H/index.md" && cat "$F/log-entries.md" >> "$H/log/2026-11.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-002 Technical Enabler pack v1"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `epics/HAL-EPC-002-online-payment-account/pack-v1.md`: the latest pack for the Technical Enabler `HAL-EPC-002`. Section 3 is "None yet."; section 5 holds no Question, and nothing parked. Appendix A has two N/A rows, Downstream and Rollout. Section 6 holds `HAL-REQ-002`.
- `epics/HAL-EPC-002-online-payment-account/epic.md`: not handed off. `index.md` lists it as a Technical Enabler for `HAL-FEA-001`. No `signoffs.md` and no Sign-off view in its folder.
- `epics/HAL-EPC-001-book-and-pay/`: the sample's pack v1, with Questions open and building on a guess, so a view for that Epic would have items.
- `project.md` People: Dana Wells (Operator), Margaret Osei (Stakeholder, hall committee chair), Ravi Kumar (engineer).
- `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Sign-off view for Margaret, the online payment account spec.

## Key at proposal

Graded on `$TURNS/1.md`.

- Says there is nothing for Margaret to check. `grep -ci 'nothing for Margaret to check' "$TURNS/1.md"` → 1 or more.
- Names the Epic. `grep -c 'HAL-EPC-002' "$TURNS/1.md"` → 1 or more.
- No batch to confirm. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → `0`; `grep -cE '^1\. ' "$TURNS/1.md"` → `0`.
- Not the other hall Epic, and no court items. `grep -cE 'HAL-Q-0|CRT-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 1.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.

## By eye

- The reply is a few plain lines: the pack has nothing being built on a guess, no call of Margaret's and no Decision for her to check, so no view is written.
- It offers no view anyway, and does not call the Epic, or Margaret, "signed off".
