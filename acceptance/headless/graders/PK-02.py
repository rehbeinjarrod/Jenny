"""PK-02's key lines (acceptance/checks/PK-02-full-pack.md, version 7), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here.

The pack shape scan (skills/pack/scripts/pack_shape.py) checks "Sections in order,
appendices last" and "Under the cap" as Jenny drafts, but it is a skill step she
could skip, so both lines stay (ADR-0008)."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
PROPOSAL_PRELUDE = (
    'cats() { for w in rules boundaries unwanted states variants data permissions downstream quality rollout examples; do grep -ci "$w" "$1"; done | grep -cx 0; }',
)
PRELUDE = (
    'P="$WS/projects/hall-bookings"',
    'PK="$P/epics/HAL-EPC-001-book-and-pay/pack-v2.md"',
    'NEWQ=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- \'projects/hall-bookings/questions/HAL-Q-*.md\')',
    'prose() { awk \'/^```/{f=!f;next} !f\' "$PK" | sed \'s/`[^`]*`//g\'; }',
)


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Coverage runs first: all 11 categories shown.',
             'cats "$TURNS/1.md"', '0'),
        Line('The new version is a new file.',
             'grep -c \'pack-v2.md\' "$TURNS/1.md"', ONE),
        Line('The batch moves the Handoff line.',
             'grep -c \'Tech face\' "$TURNS/1.md"', ONE),
        Line("The batch links the new version from the Project's `index.md`.",
             'sed -E \'s#(questions|sources|features)/index\\.md##g\' "$TURNS/1.md" | grep -c \'index\\.md\'', ONE),
        Line('The guessed Question is in the proposal.',
             'grep -c \'HAL-Q-007\' "$TURNS/1.md"', ONE),
        Line('A batch.',
             'grep -ci \'nothing is written yet\' "$TURNS/1.md"', ONE),
        Line('No court items.',
             'grep -c \'CRT-\' "$TURNS/1.md"', '0'),
    ]


def write():
    return [
        Line('One commit.',
             'git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
        Line('Commit message is the log heading.', [
            ('git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] pack \\| \'', '1'),
            ('cat "$P"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"', '1')]),
        Line('Clean tree.',
             'git -C "$WS" status --porcelain --untracked-files=all', ""),
        Line('Only pack files changed.',
             'git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE \'^projects/hall-bookings/(index\\.md|questions/[^/]+\\.md|epics/HAL-EPC-001-book-and-pay/(pack-v2|epic)\\.md|log/[0-9]{4}-[0-9]{2}\\.md)$\'', ""),
        Line('`index.md` gains one link line naming v2 and loses none.', [
            ('git -C "$WS" diff --numstat "$BASE" HEAD -- projects/hall-bookings/index.md | cut -f1,2', '1\t0'),
            ('git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/index.md | grep \'^+ \' | grep -c \'pack-v2.md\'', '1')]),
        Line("A new pack file and the Handoff line; v1 and the rest of the Epic's folder untouched.",
             'git -C "$WS" diff --name-status "$BASE" HEAD -- projects/hall-bookings/epics/ | sort | tr \'\\t\\n\' \'  \'', 'A projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/pack-v2.md M projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md '),
        Line('The Handoff line names v2, the same work item and today, and is the one line of `epic.md` changed.', [
            ('grep -cxF -e "- Tech face: [HALL-12](https://example.atlassian.net/browse/HALL-12) · Pack: pack-v2.md · Handed off: $(date +%F)" "$P/epics/HAL-EPC-001-book-and-pay/epic.md"', '1'),
            ('git -C "$WS" diff --numstat "$BASE" HEAD -- projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md | cut -f1,2', '1\t1')]),
        Line('Sections in order, appendices last.',
             'grep -E \'^## \' "$PK" | sed -E \'s/^## (For the agent|[0-9]\\.|Appendix [AB]).*/\\1/\' | tr \'\\n\' \' \'', 'For the agent 1. 2. 3. 4. 5. 6. 7. 8. 9. Appendix A Appendix B '),
        Line('Under the cap.',
             '[ "$(wc -l < "$PK")" -le 300 ] && echo ok', 'ok'),
        Line('Both fixed shapes, with every field.',
             'for w in \'Business question\' \'Business call made in build\' \'IDs touched\' \'Options seen\' \'Default if forced\' \'Made by\'; do grep -c "$w" "$PK"; done | grep -cx 0', '0'),
        Line('Engineering sections left to the repo.',
             'grep -c \'AGENTS.md\' "$PK"', ONE),
        Line('Every open Question bearing on the Epic is `DO NOT DECIDE`.',
             'for q in HAL-Q-004 HAL-Q-007 HAL-Q-008 HAL-Q-009 HAL-Q-010 HAL-Q-011 HAL-Q-013; do grep "$q" "$PK" | grep -c \'DO NOT DECIDE\'; done | grep -cx 0', '0'),
        Line('Coverage raised gap Questions.',
             'echo "$NEWQ" | grep -c .', ONE),
        Line('Every Question raised in the batch is in the pack.',
             'for q in $NEWQ; do grep -c "$(basename "$q" | cut -c1-9)" "$PK"; done | grep -cx 0', '0'),
        Line('The parked Question is listed apart, not as `DO NOT DECIDE`.', [
            ('grep -i \'parked\' "$PK" | grep -c \'HAL-Q-005\'', ONE),
            ('grep \'HAL-Q-005\' "$PK" | grep -c \'DO NOT DECIDE\'', '0')]),
        Line('"Agreed by" on the signed-off Decision, and only there.', [
            ('grep -A2 \'HAL-ANS-001\' "$PK" | grep -c \'Agreed by\'', ONE),
            ('grep -c \'Agreed by\' "$PK"', '1')]),
        Line('People by role, never by name.',
             'grep -ciwE \'margaret|osei|dana|wells|ravi|kumar\' "$PK"', '0'),
        Line('No Source IDs.',
             'grep -c \'HAL-SRC-\' "$PK"', '0'),
        Line('Shown names in the pack: no renamed canonical term outside code.', [
            ("prose | grep -oiwE 'projects?|epics?|questions?' | wc -l", '0'),
            ("prose | grep -ciw 'initiative'", ONE)]),
        Line('Every new Question has the coverage shape, scored, for a handed-off Epic.',
             'for q in $NEWQ; do f="$WS/$q"; i=$(sed -n \'s/^Impact: //p\' "$f"); u=$(sed -n \'s/^Uncertainty: //p\' "$f"); s=$(sed -n \'s/^Score: //p\' "$f"); [ "$((i*u))" = "$s" ] || echo "$q score"; grep -qE \'^Category: (Rules|Boundaries|Unwanted behaviour|States|Variants|Data|Permissions|Downstream|Quality|Rollout|Examples)$\' "$f" || echo "$q category"; grep -qx \'Needed by: HAL-EPC-001\' "$f" || echo "$q needed"; grep -qx \'Building on a guess: yes\' "$f" || echo "$q guess"; grep -qx \'Raised from: Decision coverage of HAL-EPC-001\' "$f" || echo "$q raised"; done', ""),
        Line('Every new Question is in the index.',
             'for q in $NEWQ; do grep -c "\\[$(basename "$q" | cut -c1-9)\\]" "$P/questions/index.md"; done | sort -u', '1'),
        Line('Court records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md', ""),
        Line('Records other than the pack stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD -- . \':(exclude)*/pack-v*.md\' | grep \'^+\' | grep -ciwE \'initiative|open item|spec\'', '0'),
    ]
