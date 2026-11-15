"""HO-01's key lines (acceptance/checks/HO-01-handoff-and-drift.md, version 4),
each command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 2)
PRELUDE = (
    'P="$WS/projects/hall-bookings"',
    'E="$P/epics/HAL-EPC-001-book-and-pay/epic.md"',
)
AFTER_INSTALL = 'cp -r "$REPO/acceptance/fixtures/signoff/hall-bookings/." "$WS/projects/hall-bookings/" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 pack v2 for Sign-off"'


def proposal(turn):
    nothing = Line('Nothing written.', [
        ('git -C "$WS" status --porcelain --untracked-files=all', ""),
        ('git -C "$WS" rev-parse HEAD', '$BASE')])
    if turn == 1:
        return [
            nothing,
            Line('Counts from the handed-off v1, through its tech face.', [
                ('grep -cE \'v1|pack-v1\' "$TURNS/1.md"', ONE),
                ('grep -c \'HALL-12\' "$TURNS/1.md"', ONE)]),
            Line('Both Decisions since are listed.',
                 'for a in HAL-ANS-004 HAL-ANS-005; do grep -c "$a" "$TURNS/1.md"; done | grep -cx 0', '0'),
            Line("The engineer's Decision is a build Decision.",
                 'grep \'HAL-ANS-004\' "$TURNS/1.md" | grep -ci \'during build\'', ONE),
            Line('The three N/A marks since are listed.',
                 'for w in downstream quality rollout; do grep -ci "$w" "$TURNS/1.md"; done | grep -cx 0', '0'),
            Line('The delta alone: a Question v1 already carries, unchanged, is named nowhere.',
                 'grep -c \'HAL-Q-007\' "$TURNS/1.md"', '0'),
            Line('The Sign-off since is listed.',
                 'grep -c \'HAL-SO-001\' "$TURNS/1.md"', ONE),
            Line('The newer pack, not yet handed over, is named.',
                 'grep -cE \'v2|pack-v2\' "$TURNS/1.md"', ONE),
            Line("Only this Epic's records: the other Feature's Decision stays out.",
                 'grep -c \'HAL-ANS-003\' "$TURNS/1.md"', '0'),
            Line('No court items, no Source IDs.', [
                ('grep -c \'CRT-\' "$TURNS/1.md"', '0'),
                ('grep -c \'HAL-SRC-\' "$TURNS/1.md"', '0')]),
        ]
    if turn == 2:
        return [
            nothing,
            Line('The proposal names the version and the tech face.', [
                ('grep -c \'pack-v2.md\' "$TURNS/2.md"', ONE),
                ('grep -c \'HALL-12\' "$TURNS/2.md"', ONE)]),
            Line('A batch.',
                 'grep -ci \'nothing is written yet\' "$TURNS/2.md"', ONE),
        ]
    raise ValueError(f"HO-01 grades no proposal after turn {turn}")


def write():
    return [
        Line("One commit: turn 3's; the second drift report wrote nothing.", [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
        Line('Commit message is the log heading.', [
            ('git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] handoff \\| \'', '1'),
            ('cat "$P"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"', '1')]),
        Line('Only `epic.md`, the Project index and the log changed.',
             'git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE \'^projects/hall-bookings/(epics/HAL-EPC-001-book-and-pay/epic\\.md|index\\.md|log/[0-9]{4}-[0-9]{2}\\.md)$\'', ""),
        Line('One line of `epic.md` changed.',
             'git -C "$WS" diff --numstat "$BASE" HEAD -- "$E" | cut -f1,2', '1\t1'),
        Line('The Tech face line names v2, the same work item, and today.', [
            ('grep -cxF -e "- Tech face: [HALL-12](https://example.atlassian.net/browse/HALL-12) · Pack: pack-v2.md · Handed off: $(date +%F)" "$E"', '1'),
            ('grep -c \'Tech face:\' "$E"', '1')]),
        Line('Packs untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- \'projects/hall-bookings/epics/*/pack-v*.md\'', ""),
        Line('Other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md projects/hall-bookings/questions projects/hall-bookings/project.md projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoffs.md', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep \'^+\' | grep -ciwE \'initiative|open item|spec\'', '0'),
        Line('Counts from v2, which already carries both Decisions.', [
            ('grep -cE \'v2|pack-v2\' "$TURNS/4.md"', ONE),
            ('grep -cE \'HAL-ANS-00[45]\' "$TURNS/4.md"', '0')]),
    ]
