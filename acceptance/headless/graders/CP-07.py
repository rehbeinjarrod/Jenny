"""CP-07's key lines (acceptance/checks/CP-07-signoff-readback.md, version 4), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
PRELUDE = (
    'H="$WS/projects/hall-bookings"',
    'E="$H/epics/HAL-EPC-001-book-and-pay"',
    "U='https://riverbend-hall.atlassian.net/wiki/spaces/HALL/pages/4530112/Book+and+pay+Margaret+Osei+s+calls'",
    'so() { awk \'/^## HAL-SO-002 /{f=1; print; next} /^## /{f=0} f\' "$E/signoffs.md"; }',
)
AFTER_INSTALL = (
    'H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/signoff/hall-bookings/." "$H/" && '
    'cp -r "$F/signoff-readback/hall-bookings/." "$H/" && '
    'cat "$F/signoff-readback/log-entries.md" >> "$H/log/2026-11.md" && '
    'git -C "$WS" add -A && '
    'git -C "$WS" commit -qm "Overlay: HAL-EPC-001 pack v2, Margaret\'s view published"'
)


def proposal(turn):
    lines = [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Says nothing is written yet.',
             'grep -c \'Nothing is written yet\' "$TURNS/1.md"', ONE),
        Line('Proposes the Sign-off entry.',
             'grep -c \'HAL-SO-002\' "$TURNS/1.md"', ONE),
        Line('Names the tick and the pushback.', [
            ('grep -c \'HAL-ANS-005\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-ANS-004\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-Q-014\' "$TURNS/1.md"', ONE)]),
        Line('Answers her call.', [
            ('grep -c \'HAL-Q-004\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-ANS-006\' "$TURNS/1.md"', ONE)]),
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
        Line('`signoffs.md` is only added to.', [
            ('git -C "$WS" diff "$BASE" HEAD -- \'projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoffs.md\' | grep -cE \'^-([^-]|$)\'', '0'),
            ('grep -c \'^## HAL-SO-001 · Margaret Osei (Stakeholder) · 2026-11-10$\' "$E/signoffs.md"', '1')]),
        Line('One new entry, in the record shape.', [
            ('grep -cE \'^## HAL-SO-002 · Margaret Osei \\(Stakeholder\\) · [0-9]{4}-[0-9]{2}-[0-9]{2}$\' "$E/signoffs.md"', '1'),
            ('grep -c \'^## HAL-SO-\' "$E/signoffs.md"', '2')]),
        Line('The entry names the pack, the view and the page.',
             'so | grep -cxF "Pack: pack-v2.md · View: signoff-view-v1-margaret.md · Where: $U"', '1'),
        Line('The tick is agreement; the pushback is not, and points at its Question.', [
            ("so | grep -cx 'Agreed: HAL-ANS-005'", '1'),
            ("so | grep -cx 'Not agreed: HAL-ANS-004 → HAL-Q-014'", '1'),
            ("so | grep -cx 'Source: HAL-SRC-007'", '1')]),
        Line('Only the new ticks: the Decision agreed before is not recorded again.',
             "so | grep -c 'HAL-ANS-001'", '0'),
        Line('The reading is a new Source.', [
            ('ls "$H"/sources/HAL-SRC-007-*.md | wc -l', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -c \'^Kind: Confluence page$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -cxF "URL: $U"', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -c \'^Page version: 2$\'', '1'),
            ('cat "$H"/sources/HAL-SRC-007-*.md | grep -ciF \'finish by 11 pm\'', ONE),
            ('grep -c \'HAL-SRC-007\' "$H/sources/index.md"', ONE)]),
        Line('The pushback is a Question on the Decision, building on a guess.', [
            ('ls "$H"/questions/HAL-Q-014-*.md | wc -l', '1'),
            ('cat "$H"/questions/HAL-Q-014-*.md | grep -cE \'^Affects: .*HAL-ANS-004\'', '1'),
            ('cat "$H"/questions/HAL-Q-014-*.md | grep -c \'^Building on a guess: yes$\'', '1'),
            ('cat "$H"/questions/HAL-Q-014-*.md | grep -c \'^Raised from: HAL-SRC-007$\'', '1'),
            ('cat "$H"/questions/HAL-Q-014-*.md | grep -cE \'^Status: open$\'', '1'),
            ('grep \'HAL-Q-014\' "$H/questions/index.md" | grep -c \'^| ! |\'', '1')]),
        Line('The Decision stays in force.', [
            ('git -C "$WS" diff --name-only "$BASE" HEAD -- \'projects/hall-bookings/questions/HAL-Q-009-*\'', ""),
            ('grep -rhE \'^- \\*\\*HAL-ANS-004\\*\\* .* · Status: active$\' "$H/questions" | wc -l', '1')]),
        Line('Her reply to a call is a Decision she owns.', [
            ('grep -hE \'^- \\*\\*HAL-ANS-006\\*\\* .* · Kind: decision · Owner: Margaret Osei · Date: [0-9]{4}-[0-9]{2}-[0-9]{2} · Source: HAL-SRC-007 · Status: active$\' "$H"/questions/HAL-Q-004-*.md | wc -l', '1'),
            ('grep -c \'^Status: answered$\' "$H"/questions/HAL-Q-004-*.md', '1')]),
        Line('The view and the packs stay frozen; the Epic file is untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- \'projects/hall-bookings/epics\' | grep -v \'/signoffs\\.md$\'', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiatives?|programmes?|open items?|specs?\'', '0'),
        Line('Other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox projects/hall-bookings/questions/HAL-Q-013-meeting-room.md', ""),
    ]

