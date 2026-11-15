---
id: MD-01
version: 8
skills: [jenny]
cursor-bench: true
routing: false
inputs: []
promise: true
---

# MD-01 · A Tool version mismatch stops the mode

The copied `VERSION` and the `Tool version:` line in `workspace.md` disagree. The Operator asks a lookup question at the start of a Jenny mode chat. Jenny stops with a warning that names both versions, answers nothing, and writes nothing.

Grader: `acceptance/headless/graders/MD-01.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

Sample v7 as it is. No fixtures. After install, before `$BASE`: set the `Tool version:` line in `workspace.md` to `Tool version: 0.0.9` and commit it as `Test: version mismatch`:

```sh
f="$WS/workspace.md"; sed 's/^Tool version: .*/Tool version: 0.0.9/' "$f" > "$f.new" && mv "$f.new" "$f" && git -C "$WS" commit -qam "Test: version mismatch"
```

The key relies on `projects/hall-bookings/features/HAL-FEA-001-book-and-pay.md` (`HAL-REQ-002`, `HAL-REQ-003`: the answer would be $50) and the Tool's own `VERSION`.

## Operator script

1. How much deposit does a non-member pay to book the main hall for three hours?

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`, with `V=$(cat "$REPO/VERSION")` set.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- Names both versions. `grep -c '0\.0\.9' "$TURNS/1.md"` → 1 or more; `grep -cF "$V" "$TURNS/1.md"` → 1 or more.
- No work done: no answer, no citations. `grep -c '\$50\|\$27\|\$135' "$TURNS/1.md"` → `0`; `grep -c 'HAL-REQ-\|HAL-FEA-' "$TURNS/1.md"` → `0`.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- The warning comes first and is short: what disagrees, that nothing else runs until it is fixed, and what to do next.
- No guess at which version is right.
