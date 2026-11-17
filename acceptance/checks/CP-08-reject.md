---
id: CP-08
version: 4
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: true
---

# CP-08 · A rejected batch leaves no trace

CP-01's typed note, proposed, then rejected. No file changes and no commit, not even the Source or a log line.

## Start

Sample v7 as it is. Fixture: `acceptance/fixtures/capture/typed-note.md`. The key relies on `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. Capture this: <paste: capture/typed-note.md>
2. No, scrap that. Don't capture any of it.

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- A batch was proposed. `grep -c 'Nothing is written yet' "$TURNS/1.md"` → 1 or more; `grep -ci 'calendar' "$TURNS/1.md"` → 1 or more.

## Key at write

Graded after turn 2.

- No commit, no file changes. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- The reply to the no is short: nothing was written, and nothing will be.
- The reply uses shown names only (Initiative, Spec, Open item).
