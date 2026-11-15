"""CP-06's key lines (acceptance/checks/CP-06-jira-epic-check.md, version 7), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 2)
PRELUDE = (
    'H="$WS/projects/hall-bookings"',
    "U='https://example.atlassian.net/browse/HALL-12'",
    'A=$(grep -ohE \'^- \\*\\*HAL-ANS-[0-9]{3}\\*\\*\' "$H"/questions/HAL-Q-014-*.md | grep -oE \'HAL-ANS-[0-9]{3}\')',
    'R="$WS/outbox/HALL-13-reply-$A.md"',
)


def proposal(turn):
    lines = [
        Line('Nothing written, nothing in the outbox.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE'),
            ('ls "$WS/outbox" 2>/dev/null | wc -l', '0')]),
        Line('Says nothing is written yet.',
             'grep -c \'Nothing is written yet\' "$TURNS/<n>.md"', ONE),
        Line('The Business question is a Question building on a guess.',
             'grep -c \'HAL-Q-014\' "$TURNS/<n>.md"', ONE),
        Line('The new engineer is proposed for People.',
             'grep -c \'Priya Shah\' "$TURNS/<n>.md"', ONE),
        Line('Her call is a Decision decided during build.', [
            ('grep -c \'HAL-ANS-004\' "$TURNS/<n>.md"', ONE),
            ('grep -ci \'during build\' "$TURNS/<n>.md"', ONE)]),
        Line('No reply to her own call.',
             'grep -c \'HALL-14-reply\' "$TURNS/<n>.md"', '0'),
        Line('The PR note appears only where it is listed as not used.',
             'grep -i \'PR for the booking form\' "$TURNS/<n>.md" | grep -viEc "not used|n\'t used|unused"', '0'),
        Line("The PR note's comment is named (in the not-used line or the log line, which names every comment read).",
             'grep -c \'10235\' "$TURNS/<n>.md"', ONE),
        Line('Stays in one Project.',
             'grep -c \'CRT-\' "$TURNS/<n>.md"', '0'),
    ]
    if turn == 1:
        lines += [
            Line('No reply yet: nothing answers the Business question.', [
                ('grep -c \'HAL-ANS-005\' "$TURNS/1.md"', '0'),
                ('grep -c \'HALL-13-reply\' "$TURNS/1.md"', '0')]),
        ]
    if turn == 2:
        lines += [
            Line("The Operator's answer is an Answer with its reply to `HALL-13` in the same batch.", [
                ('grep -c \'HAL-ANS-005\' "$TURNS/2.md"', ONE),
                ('grep -c \'HALL-13-reply\' "$TURNS/2.md"', ONE),
                ('grep -c \'Margaret\' "$TURNS/2.md"', ONE)]),
        ]
    return lines


def write():
    return [
        Line('One commit, clean tree.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
        Line("Commit message is the check's log heading.", [
            ('git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] capture \\| HAL-EPC-001 handed-off Epic check$\'', '1'),
            ('cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"', '1')]),
        Line('The log names every comment read, used or not, so the next check skips them.',
             'for c in 10231 10235 10238; do cat "$H"/log/*.md | awk -v h="## $(git -C "$WS" log -1 --format=%s)" \'$0==h{f=1;next} /^## /{f=0} f\' | grep -c "$c"; done | grep -cx 0', '0'),
        Line('The Jira read is a Source keeping the comments used, word for word.', [
            ('ls "$H"/sources/HAL-SRC-006-*.md | wc -l', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'^Kind: Jira item$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cxF "URL: $U"', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cE \'^Read: [0-9]{4}-[0-9]{2}-[0-9]{2}$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cF \'do they pay one deposit or a deposit for each booking?\'', ONE),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -cF \'an unpaid booking holds its slot for 30 minutes\'', ONE),
            ('cat "$H"/sources/HAL-SRC-006-*.md | grep -c \'PR for the booking form\'', '0')]),
        Line("The Operator's words are a typed note.", [
            ('grep -l \'^Kind: typed note$\' "$H"/sources/HAL-SRC-007-*.md | wc -l', '1'),
            ('grep -c \'HAL-SRC-007\' "$H/sources/index.md"', ONE)]),
        Line('The new engineer is in People.',
             'grep -cxF \'| Priya Shah | engineer | |\' "$H/project.md"', '1'),
        Line("The Business question became a Question, now answered by Margaret's Decision.", [
            ('ls "$H"/questions/HAL-Q-014-*.md | wc -l', '1'),
            ('cat "$H"/questions/HAL-Q-014-*.md | grep -c \'^Raised from: HAL-SRC-006$\'', '1'),
            ('cat "$H"/questions/HAL-Q-014-*.md | grep -c \'^Status: answered$\'', '1'),
            ('grep -hE \'^- \\*\\*HAL-ANS-00[45]\\*\\* .* · Kind: decision · Owner: Margaret Osei · Date: [0-9]{4}-[0-9]{2}-[0-9]{2} · Source: HAL-SRC-007 · Status: active$\' "$H"/questions/HAL-Q-014-*.md | wc -l', '1')]),
        Line('The build call is a Decision owned by the engineer, answering its own new Question.', [
            ('ls "$H"/questions/HAL-Q-015-*.md | wc -l', '1'),
            ('grep -hE \'^- \\*\\*HAL-ANS-00[45]\\*\\* .* · Kind: decision · Owner: Priya Shah · Date: [0-9]{4}-[0-9]{2}-[0-9]{2} · Source: HAL-SRC-006 · Status: active$\' "$H"/questions/HAL-Q-015-*.md | grep -c \'30 minutes\'', '1'),
            ('cat "$H"/questions/HAL-Q-015-*.md | grep -c \'^Status: answered$\'', '1')]),
        Line('Each Decision sets a Requirement.',
             'grep -rhE \'^- \\*\\*HAL-REQ-01[45]\\*\\* .* · Source: HAL-ANS-00[45] · Status: active$\' "$H" | wc -l', '2'),
        Line('The reply is in the outbox, with the Answer, and is the only file there.', [
            ('ls "$WS/outbox" | wc -l', '1'),
            ('git -C "$WS" diff --name-only "$BASE" HEAD -- outbox', 'outbox/HALL-13-reply-$A.md')]),
        Line('The reply quotes the Answer ID and the Question, and never a Source ID.', [
            ('grep -c "$A" "$R"', ONE),
            ('grep -c \'HAL-Q-014\' "$R"', ONE),
            ('grep -c \'HAL-SRC-\' "$R"', '0'),
            ('grep -ci \'own deposit\' "$R"', ONE)]),
        Line('The reply names people by role.',
             'grep -cE \'Margaret|Osei|Ravi|Priya\' "$R"', '0'),
        Line('The reply uses Veneer names.', [
            ('awk \'/^ *```/{f=!f;next} !f\' "$R" | sed \'s/`[^`]*`//g\' | grep -oiwE \'projects?|epics?|questions?\' | wc -l', '0'),
            ('grep -cE \'Open item|Spec\' "$R"', ONE)]),
        Line('The Epic, its packs and other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics projects/court-bookings veneer.md workspace.md', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD -- projects | grep \'^+\' | grep -ciwE \'initiatives?|programmes?|open items?|specs?\'', '0'),
    ]

