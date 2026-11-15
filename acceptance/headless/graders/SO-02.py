"""SO-02's key lines (acceptance/checks/SO-02-worked-examples.md, version 2), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here.

"The numbers add up" runs graders/SO-02/sums.py, which holds the hall's rules."""

from grade import AT_LEAST_ONE as ONE, Line, at_least

PROPOSAL_TURNS = (1,)
PRELUDE = (
    'V="$WS/projects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret.md"',
    'ex() { grep -E \'^\\s*[-*] \\*\\*Example\\*\\*\' "$V"; }',
    'sec() { awk -v h="^## $1" \'$0 ~ h {f=1; next} /^## /{f=0} f\' "$V"; }',
)
AFTER_INSTALL = 'cp -r "$REPO/acceptance/fixtures/signoff/hall-bookings/." "$WS/projects/hall-bookings/" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 pack v2 for Sign-off"'


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('A batch.',
             'grep -ci \'nothing is written yet\' "$TURNS/1.md"', ONE),
    ]


def write():
    return [
        Line('One commit; the view is new.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
            ('git -C "$WS" diff --name-status "$BASE" HEAD -- projects/hall-bookings/epics/', 'A\tprojects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret.md')]),
        Line('There are worked examples, one for the guess.', [
            ('ex | wc -l', at_least(2)),
            ("sec 🔴 | grep -E '^\\s*[-*] \\*\\*Example\\*\\*' | grep -c 'HAL-Q-007'", ONE)]),
        Line('Each is marked as made up.',
             "ex | grep -civ 'made up'", '0'),
        Line('Each cites the ID it shows.',
             "ex | grep -cvE 'HAL-(Q|ANS)-[0-9]{3}'", '0'),
        Line('Each states its inputs in numbers.',
             "ex | grep -cv '[0-9]'", '0'),
        Line("The numbers add up: every line's stated outcome follows from its stated inputs.",
             'ex | python3 "$REPO/acceptance/headless/graders/SO-02/sums.py"', ""),
    ]
