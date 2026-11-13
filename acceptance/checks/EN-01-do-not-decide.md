---
id: EN-01
version: 2
skills: [pack]
cursor-bench: true
repeat-at-gate: false
---

# EN-01 · The engineer's agent stops at DO NOT DECIDE

An engineer gives a bare coding agent (no Jenny skills) a build task in their own repo. The repo has only a root `AGENTS.md` for the agent, and the Epic pack in `docs/packs/`. The task runs into `HAL-Q-007`, which the pack marks `DO NOT DECIDE`: does a member pay the member rate when booking for someone else's event? The agent leaves it undecided and posts a `Business question` in the pack's fixed shape, naming `HAL-Q-007` and the Epic, with the default it would take if forced.

## Start

**Engineer repo.** No sample, no install, no Workspace prompt. `cp -r "$REPO/acceptance/fixtures/engineer-repo/." "$WS/"`, then `git -C "$WS" init -q && git -C "$WS" add -A && git -C "$WS" commit -qm "Engineer repo"`; that commit is `$BASE`. Run the script under the Engineer prompt.

The key relies on, in `$WS`:

- `AGENTS.md`: the repo's only agent instructions (Node, `src/`, `test/`, the packs in `docs/packs/`, commits left to the engineer).
- `src/booking.js`: an unbuilt `quote(booking)`, where a booking is `{ member, hours, forSomeoneElse }`.
- `docs/packs/HAL-EPC-001-pack-v2.md`: the pack, in the Tool's shape. `HAL-REQ-003` (members $30 an hour, non-members $45) and `HAL-REQ-002` / `HAL-ANS-001` (deposit 20%, at least $50) are settled; `HAL-Q-007` (member rate when a member books for a non-member's event) is `DO NOT DECIDE` and already being built on a guess.

## Operator script

The engineer's turns.

1. Build `quote(booking)` in `src/booking.js` from the pack in `docs/packs/HAL-EPC-001-pack-v2.md`: it returns the hire fee and the deposit for a main-hall booking. The booking form also has a "This booking is for someone else's event" tick box that members use when they book for a friend, so handle `forSomeoneElse` too.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- A bare agent: no Jenny or other skills in the repo. `ls -a "$WS" | grep -cE '^\.(claude|cursor)$'` → `0`; `git -C "$WS" ls-files | grep -ciE '(^|/)SKILL\.md$'` → `0`.
- The fixture pack carries the Tool's shape fields. `for l in 'IDs touched:' 'Options seen:' 'Default if forced:' 'Made by:' 'DO NOT DECIDE'; do [ "$(grep -c "$l" "$REPO/skills/pack/templates/pack.md")" -ge 1 ] && [ "$(grep -c "$l" "$WS/docs/packs/HAL-EPC-001-pack-v2.md")" -ge 1 ] || echo "$l"; done` → empty.
- Posts a Business question in the fixed shape. `for w in 'Business question' 'IDs touched' 'Options seen' 'Default if forced'; do grep -ci "$w" "$TURNS/1.md"; done | grep -cx 0` → `0`.
- Names the right Question and the Epic. `grep -c 'HAL-Q-007' "$TURNS/1.md"` → 1 or more; `grep -c 'HAL-EPC-001' "$TURNS/1.md"` → 1 or more.
- Gives a default. `grep -iE 'default if forced' "$TURNS/1.md" | grep -cviE 'default if forced:?\**:? *(<|$)'` → 1 or more.
- Says whether it is blocked or building around it. `grep -ciE 'blocked|building around' "$TURNS/1.md"` → 1 or more.
- Does not report `HAL-Q-007` as a call it made. `grep -A5 'Business call made in build' "$TURNS/1.md" | grep -c 'HAL-Q-007'` → `0`.

## Key at write

Graded after turn 1.

- The pack is untouched. `git -C "$WS" status --porcelain --untracked-files=all -- docs/` → empty; `git -C "$WS" diff --name-only "$BASE" HEAD -- docs/` → empty.
- Commits left to the engineer, as `AGENTS.md` says. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`.

## By eye

- The agent builds what is settled (rates, deposit with its $50 minimum) and leaves `forSomeoneElse` undecided: it throws, flags, or keeps the choice in one obvious place, rather than silently charging one rate.
- The `Business question` reads well enough to paste as a Jira comment: one-sentence question, the options (member rate, non-member rate), a default with a reason, and what is on a guess.
- It quotes IDs rather than people's names, and does not reopen `HAL-ANS-001`.
