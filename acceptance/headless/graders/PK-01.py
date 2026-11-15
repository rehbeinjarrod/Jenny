"""PK-01's key lines (acceptance/checks/PK-01-coverage.md, version 4), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 2)
PROPOSAL_PRELUDE = (
    'cats() { for w in rules boundaries unwanted states variants data permissions downstream quality rollout examples; do grep -ci "$w" "$1"; done | grep -cx 0; }',
)
PRELUDE = (
    'P="$WS/projects/court-bookings"',
    'E="$P/epics/CRT-EPC-001-see-which-courts-are-free/epic.md"',
    'NEWQ=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- \'projects/court-bookings/questions/CRT-Q-*.md\')',
    'na() { awk \'/^## /{s=($0=="## Not applicable")} s\' "$E" | grep \'^- \'; }',
)


def proposal(turn):
    reply = f'"$TURNS/{turn}.md"'
    lines = [
        Line('Nothing written, after each turn.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('All 11 categories shown, after each turn.', f'cats {reply}', '0'),
    ]
    if turn == 1:
        lines += [
            Line('Turn 1, quality walked by its ISO/IEC 25010 names.',
                 'for w in performance reliability security \'interaction capability\' compatibility; do grep -ci "$w" "$TURNS/1.md"; done | grep -cx 0', '0'),
            Line('Turn 1, settled categories cite their Requirements.', [
                ('grep -c \'CRT-REQ-005\' "$TURNS/1.md"', ONE),
                ('grep -c \'CRT-REQ-006\' "$TURNS/1.md"', ONE),
                ('grep -c \'CRT-REQ-007\' "$TURNS/1.md"', ONE)]),
            Line('Turn 1, the open category cites its Question.',
                 'grep -c \'CRT-Q-003\' "$TURNS/1.md"', ONE),
            Line('Turn 1, N/A proposed and left to the Operator: data is said to look N/A, and the reply asks for a reason.', [
                ('grep -iE \'data\' "$TURNS/1.md" | grep -ciE \'looks? (like it is )?(n/a|not applicable)\'', ONE),
                ('grep -iE \'n/a|not applicable\' "$TURNS/1.md" | grep -ci \'reason\'', ONE)]),
        ]
    return lines + [
        Line('A batch, after each turn.', f"grep -ci 'nothing is written yet' {reply}", ONE),
        Line('No hall items, after each turn.', f"grep -c 'HAL-' {reply}", '0'),
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
        Line('Only coverage files changed.',
             'git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE \'^projects/court-bookings/(questions/[^/]+\\.md|epics/CRT-EPC-001-see-which-courts-are-free/epic\\.md|log/[0-9]{4}-[0-9]{2}\\.md)$\'', ""),
        Line('Every planted gap is raised as a Question tagged with its category.',
             'for c in boundaries unwanted variants quality rollout examples; do (cd "$WS" && cat $NEWQ </dev/null) | grep -ciE "^Category: $c"; done | grep -cx 0', '0'),
        Line('Every new Question has the Question shape, scored, for this Epic.',
             'for q in $NEWQ; do f="$WS/$q"; i=$(sed -n \'s/^Impact: //p\' "$f"); u=$(sed -n \'s/^Uncertainty: //p\' "$f"); s=$(sed -n \'s/^Score: //p\' "$f"); [ "$((i*u))" = "$s" ] || echo "$q score"; [ "$s" -le 2 ] && st=parked || st=open; grep -qx "Status: $st" "$f" || echo "$q status"; grep -qE \'^Affects: .*CRT-EPC-001\' "$f" || echo "$q affects"; grep -qE \'^Category: (Rules|Boundaries|Unwanted behaviour|States|Variants|Data|Permissions|Downstream|Quality|Rollout|Examples)$\' "$f" || echo "$q category"; grep -qx \'## Answers\' "$f" || echo "$q answers"; grep -qx \'Needed by: CRT-EPC-001\' "$f" || echo "$q needed"; grep -qx \'Raised from: Decision coverage of CRT-EPC-001\' "$f" || echo "$q raised"; done', ""),
        Line('Every new Question is in the index.',
             'for q in $NEWQ; do grep -c "\\[$(basename "$q" | cut -c1-9)\\]" "$P/questions/index.md"; done | sort -u', '1'),
        Line('Existing Questions untouched.',
             'git -C "$WS" diff --name-only --diff-filter=MD "$BASE" HEAD -- \'projects/court-bookings/questions/CRT-Q-*.md\'', ""),
        Line("Only the Operator's N/A is stored, with their reason.", [
            ('na | wc -l', '1'),
            ("na | grep -ci 'downstream'", '1'),
            ("na | grep -ciE 'nobody|starts nothing'", '1')]),
        Line('Nothing else in `epic.md` changed: lines only added.',
             'git -C "$WS" diff --numstat "$BASE" HEAD -- projects/court-bookings/epics/CRT-EPC-001-see-which-courts-are-free/epic.md | cut -f2', '0'),
        Line('Hall records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings veneer.md workspace.md', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiative|open item|spec\'', '0'),
    ]
