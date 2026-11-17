---
id: SO-01
version: 7
skills: [signoff]
cursor-bench: false
routing: false
inputs: []
promise: true
---

# SO-01 · Sign-off view: the order, addressed by name, checkboxes only on Decisions, published after confirm

The Operator asks for Margaret's Sign-off view of the hall's book-and-pay Epic, whose latest pack is `pack-v2.md`. Jenny proposes a frozen `signoff-view-v1-margaret.md` and writes it only after the yes. Then the Operator says "publish it": under `Outbound: outbox` Jenny proposes the page body in `outbox/` and writes it only after a second yes. The view runs 🔴 being built on a guess → 🟠 your calls → ✅ did we get these right → ⚪ we think these don't matter → flow diagrams → also worth knowing, and only the Decisions Margaret has not yet agreed carry a checkbox.

## Start

Sample v7, then after install the overlay below, committed as `Overlay: HAL-EPC-001 pack v2 for Sign-off`:

```sh
cp -r "$REPO/acceptance/fixtures/signoff/hall-bookings/." "$WS/projects/hall-bookings/" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 pack v2 for Sign-off"
```

The key relies on, in `projects/hall-bookings/` after the overlay:

- `epics/HAL-EPC-001-book-and-pay/pack-v2.md`: the latest pack. Section 3 holds `HAL-ANS-001` (owner Stakeholder, hall committee chair), `HAL-ANS-004` (owner engineer) and `HAL-ANS-005` (owner Stakeholder, hall committee chair). Section 5 holds `HAL-Q-007` (already being built on a guess), `HAL-Q-008`, `HAL-Q-004`, `HAL-Q-010`, `HAL-Q-013`; parked `HAL-Q-005`. Appendix A has three N/A rows: Downstream, Quality, Rollout. Appendix B has one pain point that is no Question or Decision (the deposit and the late-cancellation refund must stay in step).
- `epics/HAL-EPC-001-book-and-pay/signoffs.md`: `HAL-SO-001`, Margaret Osei agreed `HAL-ANS-001`.
- `epics/HAL-EPC-001-book-and-pay/epic.md`: handed off with `pack-v1.md`; `## Left out` names `HAL-REQ-008`.
- `questions/`: `Ask: Margaret Osei` on `HAL-Q-004` and `HAL-Q-013`; `Ask: Tom Achebe` on `HAL-Q-008`; no `Ask:` on `HAL-Q-007` or `HAL-Q-010`. `HAL-ANS-004` is owned by Ravi Kumar, `HAL-ANS-005` by Margaret Osei.
- `project.md` People: Dana Wells (Operator), Margaret Osei (Stakeholder, hall committee chair), Ravi Kumar (engineer), Tom Achebe (Stakeholder, hall treasurer).

And `workspace.md` (`Outbound: outbox`), `projects/court-bookings/` (untouched), and `veneer.md` (Project shown as Initiative, Epic as Spec, Question as Open item).

## Operator script

1. Sign-off view for Margaret, the book and pay spec.
2. Yes, write it.
3. Publish it.
4. Yes, go ahead.

## Key at proposal

Graded after turn 1 on `$TURNS/1.md`, and after turn 3 on `$TURNS/3.md`, each before the next turn is sent.

After turn 1:

- Nothing written. `git -C "$WS" status --porcelain --untracked-files=all` → empty; `git -C "$WS" rev-parse HEAD` → `$BASE`.
- The view is a new file for Margaret. `grep -c 'signoff-view-v1-margaret.md' "$TURNS/1.md"` → 1 or more.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/1.md"` → 1 or more.
- No court items. `grep -c 'CRT-' "$TURNS/1.md"` → `0`.

After turn 3:

- The view is written; nothing posted or put in the outbox yet. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `1`; `git -C "$WS" status --porcelain --untracked-files=all` → empty; `test -e "$WS/outbox" && echo yes` → empty.
- The proposal names the outbox file. `grep -c 'outbox/HAL-EPC-001-signoff-view-v1-margaret.html' "$TURNS/3.md"` → 1 or more.
- A batch. `grep -ci 'nothing is written yet' "$TURNS/3.md"` → 1 or more.

## Key at write

Graded after turn 4. `P="$WS/projects/hall-bookings"`, `V="$P/epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret.md"`, `O="$WS/outbox/HAL-EPC-001-signoff-view-v1-margaret.html"`, `sec() { awk -v h="^## $1" '$0 ~ h {f=1; next} /^## /{f=0} f' "$V"; }` (one section of the view), `` prose() { awk '/^```/{f=!f;next} !f' "$V" | sed 's/`[^`]*`//g'; } ``, and `` nodes() { awk '/^```mermaid/{f=1; split("", s); next} f && /^```/{f=0; c=0; for (k in s) c++; print c; next} f { t=$0; while (match(t, /[A-Za-z0-9_]+(\[|\{|\(\()/)) { id=substr(t, RSTART, RLENGTH); sub(/[\[{(]+$/, "", id); s[id]=1; t=substr(t, RSTART+RLENGTH) } }' "$V"; } `` (the non-start/stop node count of each Mermaid block; start and stop nodes are stadium-shaped `id([…])`, which the pattern skips).

Commits:

- Two commits, one per operation. `git -C "$WS" rev-list --count "$BASE"..HEAD` → `2`.
- Both messages are log headings. `git -C "$WS" log -2 --format=%s | grep -cE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}\] signoff \| '` → `2`; `for m in "$(git -C "$WS" log -1 --format=%s)" "$(git -C "$WS" log -1 --skip=1 --format=%s)"; do cat "$P"/log/*.md | grep -cxF "## $m"; done | sort -u` → `1`.
- Clean tree. `git -C "$WS" status --porcelain --untracked-files=all` → empty.
- The view commit adds the view and the log only. `git -C "$WS" diff --name-status "$BASE" HEAD~1 | grep -vE '^(A	projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret\.md|M	projects/hall-bookings/log/[0-9]{4}-[0-9]{2}\.md)$'` → empty; `git -C "$WS" diff --name-status "$BASE" HEAD~1 | grep -c '^A'` → `1`.
- The publish commit adds the outbox file and the log only, and leaves the view as written. `git -C "$WS" diff --name-status HEAD~1 HEAD | grep -vE '^(A	outbox/HAL-EPC-001-signoff-view-v1-margaret\.html|M	projects/hall-bookings/log/[0-9]{4}-[0-9]{2}\.md)$'` → empty; `test -s "$O" && echo ok` → `ok`.

The view:

- The order. `grep -E '^## ' "$V" | grep -oE '🔴|🟠|✅|⚪|How it works|Also worth knowing' | tr '\n' ' '` → `🔴 🟠 ✅ ⚪ How it works Also worth knowing `.
- Addressed to Margaret by name. `head -8 "$V" | grep -c 'Margaret'` → 1 or more.
- The guess is in 🔴. `sec 🔴 | grep -c 'HAL-Q-007'` → 1 or more.
- Her calls are in 🟠's table; others' are named but not in it. `sec 🟠 | grep '^|' | grep -oE 'HAL-Q-0(04|13)' | sort -u | wc -l` → `2`; `sec 🟠 | grep '^|' | grep -cE 'HAL-Q-0(07|08|10)'` → `0`; `sec 🟠 | grep -v '^|' | grep -c 'HAL-Q-008'` → 1 or more.
- Checkboxes only on the Decisions she has not agreed, one each. `grep -cE '^\s*[-*] \[[ xX]\]' "$V"` → `2`; `grep -E '^\s*[-*] \[[ xX]\]' "$V" | grep -cvE 'HAL-ANS-00[45]'` → `0`; `for a in HAL-ANS-004 HAL-ANS-005; do grep -E '^\s*[-*] \[ \]' "$V" | grep -c "$a"; done | sort -u` → `1`.
- The Decisions are in ✅, the agreed one without a box. `sec ✅ | grep -oE 'HAL-ANS-00[145]' | sort -u | wc -l` → `3`.
- The engineer's Decision is flagged. `grep 'HAL-ANS-004' "$V" | grep -ci 'decided during build'` → 1 or more.
- The three N/A rows. `sec ⚪ | grep -cE '^\s*[-*] '` → `3`.
- Left out is worth knowing. `sec 'Also worth knowing' | grep -c 'HAL-REQ-008'` → 1 or more.
- At least one diagram, none over about 7 nodes (8 at most, besides start and stop). `grep -c '^```mermaid' "$V"` → 1 or more; `nodes | awk '$1 > 8' | wc -l` → `0`.
- Each diagram explains itself: a lead sentence before it, each node labelled in words with its IDs (none a bare ID, none over 12 words besides its IDs), and one walkthrough bullet per node after it, each 🔴 or 🟠 bullet pointing back to its item. `python3 "$REPO/acceptance/headless/graders/SO-01/diagrams.py" view "$V"` → empty. The script prints each diagram that falls short, and why.
- No Source IDs. `grep -c 'HAL-SRC-' "$V"` → `0`.
- Shown names, no renamed canonical term outside code. `prose | grep -oiwE 'projects?|epics?|questions?' | wc -l` → `0`; `prose | grep -ciw 'spec'` → 1 or more.

The outbox page body:

- The same order, addressed to Margaret. `grep -oE '<h2>[^<]*' "$O" | grep -oE '🔴|🟠|✅|⚪|How it works|Also worth knowing' | tr '\n' ' '` → `🔴 🟠 ✅ ⚪ How it works Also worth knowing `; `grep -c 'Margaret' "$O"` → 1 or more.
- Task items only on the two Decisions. `grep -o 'data-type="task-item"' "$O" | wc -l` → `2`; `tr -d '\n' < "$O" | sed 's/<li data-type="task-item"/\n&/g' | grep '^<li data-type="task-item"' | sed 's/<\/li>.*//' | grep -cvE 'HAL-ANS-00[45]'` → `0`.
- No Markdown checkboxes left. `grep -c '\[ \]' "$O"` → `0`.
- Each diagram is a whiteboard embed with its Mermaid source in an expand. `[ "$(grep -o 'data-card-appearance="embed"' "$O" | wc -l)" -ge "$(grep -c '^```mermaid' "$V")" ] && echo ok` → `ok`; `[ "$(grep -o '<details' "$O" | wc -l)" -ge "$(grep -c '^```mermaid' "$V")" ] && echo ok` → `ok`; `grep -c 'flowchart' "$O"` → 1 or more.
- Each whiteboard keeps its explanation: its lead sentence as a `<p>` straight before the embed, and its walkthrough as a `<ul>` after its Mermaid expand. `python3 "$REPO/acceptance/headless/graders/SO-01/diagrams.py" page "$O"` → empty.
- A body fragment. `grep -ciE '<html|<body|<head' "$O"` → `0`.
- No Source IDs. `grep -c 'HAL-SRC-' "$O"` → `0`.

Records:

- Records untouched. `git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md projects/hall-bookings/questions projects/hall-bookings/project.md` → empty.

## By eye

- Turn 1 lists the view section by section: what each holds, with IDs.
- The opening line speaks to Margaret ("Margaret, this takes about …") and counts the guess, her calls and the Decisions to confirm.
- 🔴 says the delivery team is already building on a guess for `HAL-Q-007`, and what the guess is.
- 🟠 names Tom for `HAL-Q-008` in one line, and `HAL-Q-010` as not yet put to anyone.
- `HAL-ANS-001` reads as already agreed by her, with its date, and carries no box.
- Each flow diagram's lead sentence says which part of the flow it is and why Margaret is looking at it; its nodes are short plain-word steps citing the IDs that bear on them; its walkthrough says what happens at each node and why it's there.
- Turn 3 says this Workspace's outbound is the outbox, so nothing goes to Confluence, and names the file.
- Turn 4 says the page body is in `outbox/` and what to do with it.
