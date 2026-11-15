"""CP-02's key lines (acceptance/checks/CP-02-pasted-email.md, version 8), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
PRELUDE = (
    'H="$WS/projects/hall-bookings"',
)


def proposal(turn):
    lines = [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Says nothing is written yet.',
             'grep -c \'Nothing is written yet\' "$TURNS/1.md"', ONE),
        Line('Labels the duplicate against `HAL-REQ-001`.', [
            ('grep -ciw \'duplicate\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-001\' "$TURNS/1.md"', ONE)]),
        Line('Labels the refinement against `HAL-REQ-008`.', [
            ('grep -ciw \'refines\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-008\' "$TURNS/1.md"', ONE)]),
        Line('Weighs the chasing Question that affects `HAL-REQ-008`.',
             'grep -c \'HAL-Q-012\' "$TURNS/1.md"', ONE),
        Line('Stays in one Project.',
             'grep -c \'CRT-\' "$TURNS/1.md"', '0'),
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
        Line('The email kept word for word, as a pasted email from Margaret.', [
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cF \'The side door code changes on the first of every month\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'^Kind: pasted email$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'^Owner: Margaret Osei$\'', '1')]),
        Line('The duplicate is left alone.', [
            ('grep -cxF -- \'- **HAL-REQ-001** A booking is confirmed only once its deposit has been paid. · Source: HAL-SRC-001 · Status: active\' "$H/features/HAL-FEA-001-book-and-pay.md"', '1'),
            ('git -C "$WS" diff "$BASE" HEAD | grep -E \'^\\+- \\*\\*HAL-REQ-\' | grep -ci \'deposit\'', '0')]),
        Line('The duplicate is a log note.',
             'git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/log | grep \'^+\' | grep \'HAL-REQ-001\' | grep -ci \'duplicate\'', ONE),
        Line('The refined Requirement withdrawn, struck through, and replaced.', [
            ('grep -rhE \'^- ~~\\*\\*HAL-REQ-008\\*\\* .*~~ · Withdrawn [0-9]{4}-[0-9]{2}-[0-9]{2} · Reason: .+ · Replaced by: HAL-REQ-014\' "$H" | wc -l', '1'),
            ('grep -rhE \'^- \\*\\*HAL-REQ-008\\*\\* \' "$H" | wc -l', '0')]),
        Line('The replacement cites the email.', [
            ('grep -rhE \'^- \\*\\*HAL-REQ-014\\*\\* .* · Source: HAL-SRC-006 · Status: active$\' "$H" | wc -l', '1'),
            ('grep -rhE \'^- \\*\\*HAL-REQ-014\\*\\* \' "$H" | grep -ci \'side door\'', '1')]),
        Line('The side-door code is one Requirement: the replacement holds the month, and nothing else is added.', [
            ('grep -rhE \'^- \\*\\*HAL-REQ-014\\*\\* \' "$H" | grep -ci \'month\'', '1'),
            ('grep -rc \'HAL-REQ-015\' "$H" | grep -vc \':0$\'', '0')]),
        Line('No Feature created.',
             'git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- \'projects/hall-bookings/features\'', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiatives?|programmes?|open items?|specs?\'', '0'),
        Line('Other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox', ""),
    ]

