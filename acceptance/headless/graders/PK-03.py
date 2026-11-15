"""PK-03's key lines (acceptance/checks/PK-03-over-long.md, version 3), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here.

The pack shape scan holds none of these lines: the pack is refused at Pack
step 1, before any draft, so the scan never runs."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
AFTER_INSTALL = 'cd "$WS/projects/court-bookings" && F="$REPO/acceptance/fixtures/pack/coaching" && cp -r "$F/features" "$F/epics" . && sed -i "/CRT-FEA-002-see-which-courts-are-free.md) |/r $F/features-index-row.md" features/index.md && sed -i "/^- \\[log\\/\\]/i $(cat "$F/index-line.md")" index.md && git -C "$WS" add -A && git -C "$WS" commit -qm "Add CRT-FEA-003 and CRT-EPC-002"'


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Says why: the 300-line cap.',
             'grep -c \'300\' "$TURNS/1.md"', ONE),
        Line('Proposes a re-slice.',
             'grep -ciE \'re-?slic\' "$TURNS/1.md"', ONE),
        Line('No batch.',
             'grep -ci \'nothing is written yet\' "$TURNS/1.md"', '0'),
        Line('No hall items.',
             'grep -c \'HAL-\' "$TURNS/1.md"', '0'),
    ]


def write():
    return [
        Line('Still nothing written.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]
