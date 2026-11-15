"""LK-03's key lines (acceptance/checks/LK-03-leak-trap.md, version 5), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Says there is no deposit.',
             '''grep -ciE 'no deposit|not take a deposit|paid in full|pays? (the )?(whole|full)' "$TURNS/1.md"''', ONE),
        Line('Says nothing comes back.',
             '''grep -ciE 'no refund|nothing back|gets? nothing|not get anything' "$TURNS/1.md"''', ONE),
        Line('Cites the court rules.', [
            ('grep -c \'CRT-REQ-001\' "$TURNS/1.md"', ONE),
            ('grep -c \'CRT-REQ-003\' "$TURNS/1.md"', ONE)]),
        Line('Cites the court file.', 'grep -c \'CRT-FEA-001-book-and-cancel-a-court.md\' "$TURNS/1.md"', ONE),
        Line('No hall IDs.', 'grep -c \'HAL-\' "$TURNS/1.md"', '0'),
        Line('No hall rules.', r'''grep -ciE '48[ -]hour|20 ?%|\$50|half' "$TURNS/1.md"''', '0'),
    ]


def write():
    return [
        Line('Still nothing written.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]
