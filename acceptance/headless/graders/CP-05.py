"""CP-05's key lines (acceptance/checks/CP-05-confluence-reread.md, version 4), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 2)
PRELUDE = (
    'H="$WS/projects/hall-bookings"',
    "U='https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4521987/Hall+hire+terms'",
)
AFTER_INSTALL = (
    'H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/confluence/after-v1"; cp "$F/HAL-SRC-006-confluence-hall-hire-terms.md" "$H/sources/" && '
    'cat "$F/sources-index-row.md" >> "$H/sources/index.md" && '
    'cat "$F/unplaced-lines.md" >> "$H/requirements/unplaced.md" && '
    'cat "$F/log-entry.md" >> "$H/log/2026-11.md" && '
    'git -C "$WS" add -A && '
    'git -C "$WS" commit -qm "[2026-11-11] capture | HAL-SRC-006 Confluence page: Hall hire terms"'
)


def proposal(turn):
    lines = [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Says nothing is written yet.',
             'grep -c \'Nothing is written yet\' "$TURNS/<n>.md"', ONE),
        Line('Finds the earlier reading.',
             'grep -c \'HAL-SRC-006\' "$TURNS/<n>.md"', ONE),
        Line('Proposes the changed limit against `HAL-REQ-015`.', [
            ('grep -c \'HAL-REQ-015\' "$TURNS/<n>.md"', ONE),
            ('grep -c \'100\' "$TURNS/<n>.md"', ONE)]),
        Line('Proposes the new kitchen point.',
             'grep -ci \'kitchen\' "$TURNS/<n>.md"', ONE),
        Line('Weighs the Requirement whose text has gone.',
             'grep -c \'HAL-REQ-017\' "$TURNS/<n>.md"', ONE),
        Line('Stays in one Project.',
             'grep -c \'CRT-\' "$TURNS/<n>.md"', '0'),
    ]
    if turn == 1:
        lines += [
            Line('After turn 1 only: asks rather than withdraws.',
                 'grep -ciF \'withdraw?\' "$TURNS/1.md"', ONE),
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
        Line('The first Source is unchanged.', [
            ('git -C "$WS" diff --name-only "$BASE" HEAD -- \'projects/hall-bookings/sources/HAL-SRC-006-*\'', ""),
            ('ls "$H"/sources/HAL-SRC-006-*.md | wc -l', '1')]),
        Line('The new reading is a new Source naming the previous one.', [
            ('ls "$H"/sources/HAL-SRC-007-*.md | wc -l', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -c \'^Previous reading: HAL-SRC-006$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -c \'^Kind: Confluence page$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -cxF "URL: $U"', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -c \'^Page version: 4$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -cE \'^Read: [0-9]{4}-[0-9]{2}-[0-9]{2}$\'', '1'),
            ('grep -c \'HAL-SRC-007\' "$H/sources/index.md"', ONE)]),
        Line('The new reading keeps the parts used, word for word.', [
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -cF \'the hall holds no more than 100 guests, so a booking for more than 100 cannot be made.\'', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -cF \'Hirers say when booking whether they will use the kitchen.\'', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -c \'committee@riverbend-hall.example\'', '0')]),
        Line('The changed limit: withdrawn and replaced, not rewritten.', [
            ('grep -rhE \'^- ~~\\*\\*HAL-REQ-015\\*\\* A booking for more than 120 guests cannot be made\\. · Source: HAL-SRC-006 · Status: withdrawn~~ · Withdrawn [0-9]{4}-[0-9]{2}-[0-9]{2} · Reason: .+ · Replaced by: HAL-REQ-018$\' "$H" | wc -l', '1'),
            ('grep -rhE \'^- \\*\\*HAL-REQ-015\\*\\* \' "$H" | wc -l', '0'),
            ('grep -rhE \'^- \\*\\*HAL-REQ-018\\*\\* .* · Source: HAL-SRC-007 · Status: active$\' "$H" | grep -c \'100\'', '1')]),
        Line('The new point is one new Requirement.',
             'grep -rhE \'^- \\*\\*HAL-REQ-019\\*\\* .* · Source: HAL-SRC-007 · Status: active$\' "$H" | grep -ci \'kitchen\'', '1'),
        Line("The gone text's Requirement withdrawn as the Operator said, with no replacement.", [
            ('grep -rhE \'^- ~~\\*\\*HAL-REQ-017\\*\\* .* · Status: withdrawn~~ · Withdrawn [0-9]{4}-[0-9]{2}-[0-9]{2} · Reason: .+$\' "$H" | grep -vc \'Replaced by\'', '1'),
            ('grep -rhE \'^- \\*\\*HAL-REQ-017\\*\\* \' "$H" | wc -l', '0')]),
        Line("Only the changes: the unchanged parts' Requirements are untouched, and only two Requirements are added.", [
            ('git -C "$WS" diff "$BASE" HEAD | grep -E \'^[-+]- (~~)?\\*\\*HAL-REQ-01[46]\\*\\*\'', ""),
            ('git -C "$WS" diff "$BASE" HEAD | grep -cE \'^\\+- \\*\\*HAL-REQ-\'', '2'),
            ('git -C "$WS" diff "$BASE" HEAD | grep -E \'^[-+]- (~~)?\\*\\*HAL-REQ-001\\*\\*\'', "")]),
        Line('No Feature created.',
             'git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- \'projects/hall-bookings/features\'', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiatives?|programmes?|open items?|specs?\'', '0'),
        Line('Other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox', ""),
    ]

