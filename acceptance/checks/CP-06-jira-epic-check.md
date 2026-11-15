---
id: CP-06
version: 7
skills: [capture]
cursor-bench: false
routing: false
inputs: []
promise: true
---

# CP-06 · A handed-off Epic check: a Business question is answered in the same batch, and its Jira reply goes with it

The hall's book-and-pay Epic was handed off on tech face `HALL-12` and last checked on 2026-11-09. Since then Ravi posted a `Business question` on Story `HALL-13` (one deposit or two when a hirer books twice in one day) and a PR note, and Priya Shah, an engineer not yet in People, posted a `Business call made in build` on `HALL-14` (an unpaid booking holds its slot for 30 minutes). The Operator says "check HALL-12". Jenny proposes one batch: the Jira Source, the Business question as a building-on-a-guess Question, Priya added to People, and her call as a Decision she owns, flagged decided during build, answering a Question raised in the same batch. The Operator gives Margaret's answer to the Business question in an amend: the batch gains a typed-note Source, the Answer and a reply to `HALL-13` quoting the Answer ID. On the yes, the reply is written to `outbox/` in the same commit as the Answer.

Grader: `acceptance/headless/graders/CP-06.py`, which runs it headless (`acceptance/runner/claude-code.md`, **Checks, headless**).

## Start

Sample v7 as it is. MCP stand-in: `https://example.atlassian.net/browse/HALL-12` → `jira/hall-12-v1.md` (the Epic `HALL-12`, Stories `HALL-13` and `HALL-14`, comments 10231, 10235 and 10238, each dated after 2026-11-09).

The key relies on, in `projects/hall-bookings/`:

- `epics/HAL-EPC-001-book-and-pay/epic.md`: `- Tech face: [HALL-12](https://example.atlassian.net/browse/HALL-12) · Pack: pack-v1.md · Handed off: 2026-11-07`.
- `log/2026-11.md`: the last check, `## [2026-11-09] capture | HAL-EPC-001 handed-off Epic check`.
- `project.md`: People Dana Wells (Operator), Margaret Osei (Stakeholder, hall committee chair), Ravi Kumar (engineer); no Priya Shah.
- `features/HAL-FEA-001-book-and-pay.md`: `HAL-REQ-001`, `HAL-REQ-002` (deposit 20%, minimum $50).
- No open Question covers two bookings in one day or how long an unpaid slot is held.
- Highest IDs `HAL-SRC-005`, `HAL-REQ-013`, `HAL-Q-013`, `HAL-ANS-003`, so the new ones are `HAL-SRC-006`, `HAL-SRC-007`, `HAL-Q-014`, `HAL-Q-015`, `HAL-ANS-004` and `HAL-ANS-005` (the amend settles the batch's IDs again, so Margaret's Answer may take either number), and Requirements from `HAL-REQ-014`.
- `workspace.md`: `Outbound: outbox`. `veneer.md`: Project shown as Initiative, Epic as Spec, Question as Open item.

## Operator script

1. Check HALL-12.
2. On the deposit question from HALL-13: Margaret says each booking takes its own deposit, even when the same hirer books twice on one day. Put that in this batch.
3. Yes, go ahead.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md` and after turn 2 on `$TURNS/2.md`, each before the next turn is sent.

Both turns:

- Nothing written, nothing in the outbox. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`; `ls "$WS/outbox" 2>/dev/null | wc -l` → `0`.
- Says nothing is written yet. `grep -c 'Nothing is written yet' "$TURNS/<n>.md"` → 1 or more.
- The Business question is a Question building on a guess. `grep -c 'HAL-Q-014' "$TURNS/<n>.md"` → 1 or more.
- The new engineer is proposed for People. `grep -c 'Priya Shah' "$TURNS/<n>.md"` → 1 or more.
- Her call is a Decision decided during build. `grep -c 'HAL-ANS-004' "$TURNS/<n>.md"` → 1 or more; `grep -ci 'during build' "$TURNS/<n>.md"` → 1 or more.
- No reply to her own call. `grep -c 'HALL-14-reply' "$TURNS/<n>.md"` → `0`.
- The PR note appears only where it is listed as not used. `grep -i 'PR for the booking form' "$TURNS/<n>.md" | grep -viEc "not used|n't used|unused"` → `0`.
- The PR note's comment is named (in the not-used line or the log line, which names every comment read). `grep -c '10235' "$TURNS/<n>.md"` → 1 or more.
- Stays in one Project. `grep -c 'CRT-' "$TURNS/<n>.md"` → `0`.

After turn 1 only:

- No reply yet: nothing answers the Business question. `grep -c 'HAL-ANS-005' "$TURNS/1.md"` → `0`; `grep -c 'HALL-13-reply' "$TURNS/1.md"` → `0`.

After turn 2 only:

- The Operator's answer is an Answer with its reply to `HALL-13` in the same batch. `grep -c 'HAL-ANS-005' "$TURNS/2.md"` → 1 or more; `grep -c 'HALL-13-reply' "$TURNS/2.md"` → 1 or more; `grep -c 'Margaret' "$TURNS/2.md"` → 1 or more.

## Key at write

Graded after turn 3. `H="$WS/projects/hall-bookings"`, `U='https://example.atlassian.net/browse/HALL-12'`, `A=$(grep -ohE '^- \*\*HAL-ANS-[0-9]{3}\*\*' "$H"/questions/HAL-Q-014-*.md | grep -oE 'HAL-ANS-[0-9]{3}')` (Margaret's Answer), `R="$WS/outbox/HALL-13-reply-$A.md"`.

- One commit, clean tree. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- Commit message is the check's log heading. `git -C "$WS" log -1 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] capture \| HAL-EPC-001 handed-off Epic check$'` → `1`; `cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"` → `1`.
- The log names every comment read, used or not, so the next check skips them. `for c in 10231 10235 10238; do cat "$H"/log/*.md | awk -v h="## $(git -C "$WS" log -1 --format=%s)" '$0==h{f=1;next} /^## /{f=0} f' | grep -c "$c"; done | grep -cx 0` → `0`.
- The Jira read is a Source keeping the comments used, word for word. `ls "$H"/sources/HAL-SRC-006-*.md | wc -l` → `1`; each → `1`: `cat "$H"/sources/HAL-SRC-006-*.md | grep -c '^Kind: Jira item$'`, `cat "$H"/sources/HAL-SRC-006-*.md | grep -cxF "URL: $U"`, `cat "$H"/sources/HAL-SRC-006-*.md | grep -cE '^Read: [0-9]{4}-[0-9]{2}-[0-9]{2}$'`; each → 1 or more: `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'do they pay one deposit or a deposit for each booking?'`, `cat "$H"/sources/HAL-SRC-006-*.md | grep -cF 'an unpaid booking holds its slot for 30 minutes'`; `cat "$H"/sources/HAL-SRC-006-*.md | grep -c 'PR for the booking form'` → `0`.
- The Operator's words are a typed note. `grep -l '^Kind: typed note$' "$H"/sources/HAL-SRC-007-*.md | wc -l` → `1`; `grep -c 'HAL-SRC-007' "$H/sources/index.md"` → 1 or more.
- The new engineer is in People. `grep -cxF '| Priya Shah | engineer | |' "$H/project.md"` → `1`.
- The Business question became a Question, now answered by Margaret's Decision. `ls "$H"/questions/HAL-Q-014-*.md | wc -l` → `1`; each → `1`: `cat "$H"/questions/HAL-Q-014-*.md | grep -c '^Raised from: HAL-SRC-006$'`, `cat "$H"/questions/HAL-Q-014-*.md | grep -c '^Status: answered$'`, `grep -hE '^- \*\*HAL-ANS-00[45]\*\* .* · Kind: decision · Owner: Margaret Osei · Date: [0-9]{4}-[0-9]{2}-[0-9]{2} · Source: HAL-SRC-007 · Status: active$' "$H"/questions/HAL-Q-014-*.md | wc -l`.
- The build call is a Decision owned by the engineer, answering its own new Question. `ls "$H"/questions/HAL-Q-015-*.md | wc -l` → `1`; `grep -hE '^- \*\*HAL-ANS-00[45]\*\* .* · Kind: decision · Owner: Priya Shah · Date: [0-9]{4}-[0-9]{2}-[0-9]{2} · Source: HAL-SRC-006 · Status: active$' "$H"/questions/HAL-Q-015-*.md | grep -c '30 minutes'` → `1`; `cat "$H"/questions/HAL-Q-015-*.md | grep -c '^Status: answered$'` → `1`.
- Each Decision sets a Requirement. `grep -rhE '^- \*\*HAL-REQ-01[45]\*\* .* · Source: HAL-ANS-00[45] · Status: active$' "$H" | wc -l` → `2`.
- The reply is in the outbox, with the Answer, and is the only file there. `ls "$WS/outbox" | wc -l` → `1`; `git -C "$WS" diff --name-only "$BASE" HEAD -- outbox` → `outbox/HALL-13-reply-$A.md`.
- The reply quotes the Answer ID and the Question, and never a Source ID. `grep -c "$A" "$R"` → 1 or more; `grep -c 'HAL-Q-014' "$R"` → 1 or more; `grep -c 'HAL-SRC-' "$R"` → `0`; `grep -ci 'own deposit' "$R"` → 1 or more.
- The reply names people by role. `grep -cE 'Margaret|Osei|Ravi|Priya' "$R"` → `0`.
- The reply uses Veneer names. `awk '/^ *```/{f=!f;next} !f' "$R" | sed 's/`[^`]*`//g' | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`; `grep -cE 'Open item|Spec' "$R"` → 1 or more.
- The Epic, its packs and other records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics projects/court-bookings veneer.md workspace.md` → empty.
- Records stay canonical. `git -C "$WS" diff "$BASE" HEAD -- projects | grep '^+' | grep -ciwE 'initiatives?|programmes?|open items?|specs?'` → `0`.

## By eye

- Turn 1 names the last check (2026-11-09) and reads only what came after it; the PR note is listed as not used.
- `HAL-Q-014` is flagged as being built on a guess (a deposit for each booking), needed by the Spec.
- Priya's call is shown as decided during build, with Priya proposed for People as an engineer before her Decision.
- Turn 2 shows the batch again in full, with the reply body in a fenced block straight after Margaret's Answer, and says the reply goes to the outbox, not to Jira.
- The reply names Margaret by role (the hall committee chair) and says the call is settled.
