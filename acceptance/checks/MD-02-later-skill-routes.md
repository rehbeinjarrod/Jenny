---
id: MD-02
version: 3
skills: [jenny]
cursor-bench: true
routing: true
inputs: []
promise: false
---

# MD-02 · A skill added later routes without changing the mode

A skill the mode has never heard of is dropped into the skills folder. The Operator asks for it in plain Veneer words, with no `/name`. The mode finds it from its description and follows it.

## Start

Sample v7. Fixture: `acceptance/fixtures/skill-headcount/` (a `headcount` skill that counts a Project's People in a fixed shape). After install, before `$BASE`: copy that folder to `$SK/headcount/` and commit it as `Test: add headcount skill`:

```sh
cp -r "$REPO/acceptance/fixtures/skill-headcount" "$SK/headcount" && git -C "$WS" add -A && git -C "$WS" commit -qm "Test: add headcount skill"
```

The key relies on `projects/hall-bookings/project.md` (3 People: Dana Wells, Margaret Osei, Ravi Kumar) and `veneer.md` (Project shown as Initiative).

## Operator script

1. How many people are on the hall initiative?

## Key at proposal

Graded after turn 1, on `$TURNS/1.md`.

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- The added skill's shape. `grep -c '^\*\*Headcount\*\*$' "$TURNS/1.md"` → `1`; `` grep -c '^`HAL`: 3 people$' "$TURNS/1.md" `` → `1`.
- Each person. Each → 1 or more: `grep -c 'Dana Wells' "$TURNS/1.md"`, `grep -c 'Margaret Osei' "$TURNS/1.md"`, `grep -c 'Ravi Kumar' "$TURNS/1.md"`.
- Stays in one Project. `grep -c 'CRT' "$TURNS/1.md"` → `0`.
- Quiet about a matching version: no word of the check. `grep -ci 'version' "$TURNS/1.md"` → `0`.
- The mode itself is unchanged. `diff -r -x VERSION "$REPO/skills/jenny" "$SK/jenny"` → empty.

## Key at write

Graded after turn 1.

- Still nothing written. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `0`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.

## By eye

- The reply is the headcount shape and nothing else of note: the request did not go to `lookup`.
