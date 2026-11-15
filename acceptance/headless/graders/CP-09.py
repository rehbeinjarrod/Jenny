"""CP-09's key lines (acceptance/checks/CP-09-jira-recheck.md, version 4), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
PRELUDE = (
    'H="$WS/projects/hall-bookings"',
)
AFTER_INSTALL = (
    'H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures/jira/after-check"; cp -r "$F/hall-bookings/." "$H/" && '
    'cp -r "$F/outbox" "$WS/" && '
    'cat "$F/log-entry.md" >> "$H/log/2026-11.md" && '
    'git -C "$WS" add -A && '
    'git -C "$WS" commit -qm "[2026-11-12] capture | HAL-EPC-001 handed-off Epic check"'
)


def proposal(turn):
    lines = [
        Line('Nothing written, nothing new in the outbox.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE'),
            ('ls "$WS/outbox" | wc -l', '1')]),
        Line('Says nothing is written yet.',
             'grep -c \'Nothing is written yet\' "$TURNS/1.md"', ONE),
        Line('The pushback is a new Question on the Decision.', [
            ('grep -c \'HAL-Q-016\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-ANS-001\' "$TURNS/1.md"', ONE)]),
        Line('Only what changed: the comments seen at the last check are not proposed again.', [
            ('grep -ciE \'same day|twice\' "$TURNS/1.md"', '0'),
            ('grep -ci \'30 minutes\' "$TURNS/1.md"', '0')]),
        Line('No reply: nothing is answered.',
             'grep -ciE \'outbox/|-reply-\' "$TURNS/1.md"', '0'),
        Line('Stays in one Project.',
             'grep -c \'CRT-\' "$TURNS/1.md"', '0'),
    ]
    return lines


def write():
    return [
        Line('One commit, clean tree.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
        Line("Commit message is the check's log heading.", [
            ('git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] capture \\| HAL-EPC-001 handed-off Epic check$\'', '1'),
            ('cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"', ONE)]),
        Line('The new Source holds the new comment alone.', [
            ('ls "$H"/sources/HAL-SRC-008-*.md | wc -l', '1'),
            ('cat "$H"/sources/HAL-SRC-008-*.md | grep -c \'^Kind: Jira item$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-008-*.md | grep -cF \'Should the deposit be capped at the hire fee?\'', '1'),
            ('cat "$H"/sources/HAL-SRC-008-*.md | grep -ciE \'same day|30 minutes\'', '0')]),
        Line("The earlier check's records are untouched.",
             'git -C "$WS" diff --name-only "$BASE" HEAD -- \'projects/hall-bookings/sources/HAL-SRC-006-*\' \'projects/hall-bookings/sources/HAL-SRC-007-*\' \'projects/hall-bookings/questions/HAL-Q-014-*\' \'projects/hall-bookings/questions/HAL-Q-015-*\' projects/hall-bookings/project.md', ""),
        Line('The pushback is one new Question on the Decision, building on a guess.', [
            ('git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- projects/hall-bookings/questions | wc -l', '1'),
            ('cat "$H"/questions/HAL-Q-016-*.md | grep -cE \'^Affects: .*HAL-ANS-001\'', '1'),
            ('cat "$H"/questions/HAL-Q-016-*.md | grep -c \'^Building on a guess: yes$\'', '1'),
            ('cat "$H"/questions/HAL-Q-016-*.md | grep -c \'^Raised from: HAL-SRC-008$\'', '1'),
            ('cat "$H"/questions/HAL-Q-016-*.md | grep -c \'^Status: open$\'', '1'),
            ('grep \'HAL-Q-016\' "$H/questions/index.md" | grep -c \'^| ! |\'', '1')]),
        Line('The Decision stays in force.', [
            ('git -C "$WS" diff --name-only "$BASE" HEAD -- \'projects/hall-bookings/questions/HAL-Q-001-*\'', ""),
            ('grep -rhE \'^- \\*\\*HAL-ANS-001\\*\\* .* · Status: active$\' "$H/questions" | wc -l', '1')]),
        Line('No new Answer, Requirement or reply.', [
            ('git -C "$WS" diff "$BASE" HEAD | grep -cE \'^\\+- \\*\\*HAL-(ANS|REQ)-\'', '0'),
            ('git -C "$WS" diff --name-only "$BASE" HEAD -- outbox', "")]),
        Line("This check's log entry names the new comment.",
             'git -C "$WS" diff "$BASE" HEAD -- projects/hall-bookings/log | grep \'^+\' | grep -c \'10247\'', ONE),
        Line('Other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics projects/hall-bookings/features projects/court-bookings veneer.md workspace.md', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep \'^+\' | grep -ciwE \'initiatives?|programmes?|open items?|specs?\'', '0'),
    ]

