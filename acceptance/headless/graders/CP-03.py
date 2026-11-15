"""CP-03's key lines (acceptance/checks/CP-03-meeting-notes-conflict.md, version 9), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 2)
PRELUDE = (
    'H="$WS/projects/hall-bookings"',
)


def proposal(turn):
    lines = [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Says nothing is written yet.',
             'grep -c \'Nothing is written yet\' "$TURNS/<n>.md"', ONE),
        Line('Labels the conflict against `HAL-REQ-004`.', [
            ('grep -ci \'conflict\' "$TURNS/<n>.md"', ONE),
            ('grep -c \'HAL-REQ-004\' "$TURNS/<n>.md"', ONE)]),
        Line('Matches the open Question.',
             'grep -c \'HAL-Q-003\' "$TURNS/<n>.md"', ONE),
        Line('Stays in one Project.',
             'grep -c \'CRT-\' "$TURNS/<n>.md"', '0'),
    ]
    if turn == 2:
        lines += [
            Line('After turn 2 only: the owner is in the batch.',
                 'grep -c \'Margaret Osei\' "$TURNS/2.md"', ONE),
        ]
    return lines


def write():
    return [
        Line('One commit, clean tree.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
        Line('Commit message is the log heading.', [
            ('git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] capture \\| \'', '1'),
            ('cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"', '1')]),
        Line('Nothing overwritten: the Requirement in conflict stands as it was.', [
            ('grep -cxF -- \'- **HAL-REQ-004** Members can book up to six months ahead; non-members up to three months ahead. · Source: HAL-SRC-001 · Status: active\' "$H/features/HAL-FEA-001-book-and-pay.md"', '1'),
            ('git -C "$WS" diff "$BASE" HEAD | grep -E \'^[-+]- (~~)?\\*\\*HAL-REQ-004\\*\\*\'', "")]),
        Line('The conflict is a Question citing both Sources.', [
            ('grep -lE \'^Affects: .*HAL-REQ-004\' "$H"/questions/HAL-Q-014-*.md | xargs -r grep -l \'HAL-SRC-001\' | xargs -r grep -l \'HAL-SRC-006\' | wc -l', '1'),
            ('cat "$H"/questions/HAL-Q-014-*.md | grep -cE \'^Status: (open|parked)$\'', '1'),
            ('cat "$H"/questions/HAL-Q-014-*.md | grep -cE \'^(Impact|Uncertainty|Score|Score reason): .+\'', '4'),
            ('grep -c \'HAL-Q-014\' "$H/questions/index.md"', ONE)]),
        Line('The Answer, a Decision owned by Margaret.', [
            ('grep -cE \'^- \\*\\*HAL-ANS-004\\*\\* .* · Kind: decision · Owner: Margaret Osei · .*Source: HAL-SRC-006 · Status: active$\' "$H/questions/HAL-Q-003-committee-cancels.md"', '1'),
            ('grep -c \'^Status: answered$\' "$H/questions/HAL-Q-003-committee-cancels.md"', '1')]),
        Line("The Question's wording kept.",
             'head -1 "$H/questions/HAL-Q-003-committee-cancels.md"', "# HAL-Q-003 · What happens to the hirer's deposit when the hall committee cancels a booking?"),
        Line('One Requirement from the Answer.',
             'grep -rhE \'^- \\*\\*HAL-REQ-[0-9]{3}\\*\\* .* · Source: HAL-ANS-004 · Status: active$\' "$H" | wc -l', '1'),
        Line('The Requirements in `Affects:` left unchanged.', [
            ('grep -cxF -- \'- **HAL-REQ-005** A hirer who cancels at least 48 hours before the booking starts gets the whole deposit back. · Source: HAL-SRC-001 · Status: active\' "$H/features/HAL-FEA-002-cancel-a-booking.md"', '1'),
            ('grep -cxF -- \'- **HAL-REQ-007** A hirer who cancels less than 48 hours before the booking starts gets half the deposit back. · Source: HAL-ANS-003 · Status: active\' "$H/features/HAL-FEA-002-cancel-a-booking.md"', '1')]),
        Line('Own words kept word for word; third-party text never copied, its location kept.', [
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cF \'non-members can book up to six months ahead, the same as members\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cF \'The committee agreed to follow the Code: if we cancel a booking, the hirer gets the whole deposit back within seven days.\'', '1'),
            ('git -C "$WS" diff "$BASE" HEAD | grep -ciE \'every sum paid|paid towards that hire|withdraws a confirmed hire|within its control|original method of payment\'', '0'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'3\\.4\'', ONE)]),
        Line('No Feature created.',
             'git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- \'projects/hall-bookings/features\'', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiatives?|programmes?|open items?|specs?\'', '0'),
        Line('Other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox', ""),
    ]

