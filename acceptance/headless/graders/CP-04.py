"""CP-04's key lines (acceptance/checks/CP-04-confluence-page.md, version 6), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
PRELUDE = (
    'H="$WS/projects/hall-bookings"',
    "U='https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4521987/Hall+hire+terms'",
)


def proposal(turn):
    lines = [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Says nothing is written yet.',
             'grep -c \'Nothing is written yet\' "$TURNS/1.md"', ONE),
        Line('Read the page: its points are in the batch.', [
            ('grep -c \'120\' "$TURNS/1.md"', ONE),
            ('grep -cF \'$20\' "$TURNS/1.md"', ONE),
            ('grep -ci \'guests\' "$TURNS/1.md"', ONE)]),
        Line('Labels the duplicate against `HAL-REQ-001`.', [
            ('grep -ciw \'duplicate\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-001\' "$TURNS/1.md"', ONE)]),
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
        Line('One Source, a Confluence page from Margaret with the URL, page version and date read.', [
            ('ls "$H"/sources/HAL-SRC-006-*.md | wc -l', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'^Kind: Confluence page$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'^Owner: Margaret Osei$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cxF "URL: $U"', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'^Page version: 3$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cE \'^Read: [0-9]{4}-[0-9]{2}-[0-9]{2}$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'^Previous reading:\'', '0'),
            ('grep -c \'HAL-SRC-006\' "$H/sources/index.md"', ONE)]),
        Line('The parts used, word for word; the parts not used left out.', [
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cF \'The hall holds no more than 120 guests, so a booking for more than 120 cannot be made.\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cF \'the caretaker sets out the tables and chairs before the booking starts, for a $20 fee.\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'committee@riverbend-hall.example\'', '0')]),
        Line('Four new Requirements, each citing the page.', [
            ('grep -rhE \'^- \\*\\*HAL-REQ-01[4-7]\\*\\* .* · Source: HAL-SRC-006 · Status: active$\' "$H" | wc -l', '4'),
            ('grep -rhE \'^- \\*\\*HAL-REQ-01[4-7]\\*\\* \' "$H" | grep -c \'120\'', '1'),
            ('grep -rhE \'^- \\*\\*HAL-REQ-01[4-7]\\*\\* \' "$H" | grep -cF \'$20\'', '1'),
            ('grep -rhE \'^- \\*\\*HAL-REQ-01[4-7]\\*\\* \' "$H" | grep -F \'$20\' | grep -ci \'tables\'', '1'),
            ('grep -rc \'HAL-REQ-018\' "$H" | grep -vc \':0$\'', '0')]),
        Line('The duplicate is left alone, as a log note.', [
            ('grep -cxF -- \'- **HAL-REQ-001** A booking is confirmed only once its deposit has been paid. · Source: HAL-SRC-001 · Status: active\' "$H/features/HAL-FEA-001-book-and-pay.md"', '1'),
            ('git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/log | grep \'^+\' | grep \'HAL-REQ-001\' | grep -ci \'duplicate\'', ONE)]),
        Line('No Feature created.',
             'git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- \'projects/hall-bookings/features\'', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiatives?|programmes?|open items?|specs?\'', '0'),
        Line('Other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox', ""),
    ]

