"""SL-02's key lines (acceptance/checks/SL-02-pain-points.md, version 4), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line, at_least

PROPOSAL_TURNS = (1, 2)
PRELUDE = (
    'P="$WS/projects/hall-bookings"',
    'E1="$P/epics/HAL-EPC-001-book-and-pay/epic.md"',
    'E2=$(grep -lx \'Feature: HAL-FEA-001\' "$P"/epics/*/epic.md | grep -v HAL-EPC-001-)',
    'cov() { awk \'FNR==1{s=0} /^## /{s=($0=="## Covers")} s\' "$@" | grep -oE \'HAL-REQ-[0-9]{3}\'; }',
)


def proposal(turn):
    lines = [
        Line('Nothing written, after each turn.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
    ]
    if turn == 1:
        lines += [
            Line('Turn 1, both asks named.', [
                ('grep -c \'HAL-REQ-013\' "$TURNS/1.md"', ONE),
                ('grep -c \'HAL-REQ-008\' "$TURNS/1.md"', ONE)]),
            Line('Turn 1, flagged as pain points.', [
                ('grep -ci \'pain point\' "$TURNS/1.md"', ONE),
                ('grep -ci \'horizontal\' "$TURNS/1.md"', ONE),
                ('grep -ci \'second spec\' "$TURNS/1.md"', ONE)]),
            Line('Turn 1, a re-slice suggested.',
                 'grep -ciE \'re-?slice\' "$TURNS/1.md"', ONE),
            Line('Turn 1, asks for the reason.',
                 'grep -ciE \'reason|why\' "$TURNS/1.md"', ONE),
        ]
    if turn == 2:
        lines += [
            Line('Turn 2, the second Epic is still a pain point, in a batch.', [
                ('grep -ci \'pain point\' "$TURNS/2.md"', ONE),
                ('grep -c \'HAL-REQ-008\' "$TURNS/2.md"', ONE),
                ('grep -ci \'nothing is written yet\' "$TURNS/2.md"', ONE)]),
        ]
    return lines


def write():
    return [
        Line('One commit.',
             'git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
        Line('Commit message is the log heading.', [
            ('git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] slice \\| \'', '1'),
            ('grep -cxF "## $(git -C "$WS" log -1 --format=%s)" "$P"/log/*.md', '1')]),
        Line('Clean tree.',
             'git -C "$WS" status --porcelain --untracked-files=all', ""),
        Line('Only slicing files changed.',
             'git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE \'^projects/hall-bookings/(features/[^/]+\\.md|epics/[^/]+/epic\\.md|requirements/unplaced\\.md|index\\.md|log/[0-9]{4}-[0-9]{2}\\.md)$\'', ""),
        Line('Every Requirement line is kept, each in exactly one place, byte for byte.',
             'diff <(git -C "$WS" grep -h \'^- \\*\\*HAL-REQ-\' "$BASE" -- projects/hall-bookings/features projects/hall-bookings/requirements | sort) <(grep -rh \'^- \\*\\*HAL-REQ-\' "$P"/features "$P"/requirements | sort)', ""),
        Line('Book and pay has two Epics.',
             'grep -lx \'Feature: HAL-FEA-001\' "$P"/epics/*/epic.md | wc -l', '2'),
        Line('Every other Feature has exactly one Epic.',
             'for f in "$P"/features/HAL-FEA-*.md; do id=$(basename "$f" | cut -c1-11); [ "$id" = HAL-FEA-001 ] || grep -lx "Feature: $id" "$P"/epics/*/epic.md | wc -l; done | sort -u', '1'),
        Line('The door code email is in Book and pay, covered by the second Epic, its line moved byte for byte.', [
            ('grep -cxF -e "$(git -C "$WS" show "$BASE":projects/hall-bookings/requirements/unplaced.md | grep \'^- \\*\\*HAL-REQ-008\\*\\*\')" "$P/features/HAL-FEA-001-book-and-pay.md"', '1'),
            ('cov "$E2" | grep -cx \'HAL-REQ-008\'', '1'),
            ('grep -c \'HAL-REQ-008\' "$P/requirements/unplaced.md"', '0')]),
        Line('The handed-off Epic is not touched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/epic.md', ""),
        Line("The second Epic records the pain point with the Operator's reason.", [
            ('grep \'^Pain point:\' "$E2" | grep -ciE \'second\'', '1'),
            ('grep \'^Pain point:\' "$E2" | grep -ci \'team\'', '1')]),
        Line('No other pain point recorded.',
             'grep -l \'^Pain point:\' "$P"/epics/*/epic.md "$P"/features/*.md | wc -l', '1'),
        Line('No horizontal Feature: the phone-screen Requirement shares its Feature, and no Feature is about phones.', [
            ('grep -cE \'^- \\*\\*HAL-REQ-\' $(grep -l \'^- \\*\\*HAL-REQ-013\\*\\*\' "$P"/features/HAL-FEA-*.md) </dev/null', at_least(2)),
            ('grep -liE \'^# HAL-FEA-[0-9]{3} · .*(phone|mobile|screen)\' "$P"/features/*.md | wc -l', '0')]),
        Line('No Requirement covered by two Epics.',
             'cov "$P"/epics/*/epic.md | sort | uniq -d', ""),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiative|open item|spec\'', '0'),
    ]
