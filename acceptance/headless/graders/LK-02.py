"""LK-02's key lines (acceptance/checks/LK-02-lookup-skill.md, version 7), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('The fixed answer shape, three labelled parts.',
             r'''grep -cE '^\*\*(In short|Based on|Not known yet)\*\*' "$TURNS/1.md"''', '3'),
        Line('The right amount.', r'''grep -c '\$50' "$TURNS/1.md"''', ONE),
        Line('Not the 20% figure as the deposit.',
             r'''grep -ciE '(deposit (is|of)|pays?( a)?) \$27|\$27 deposit' "$TURNS/1.md"''', '0'),
        Line('The amount is the short answer.',
             r"""sed -n '/^\*\*In short\*\*/,/^\*\*Based on\*\*/p' "$TURNS/1.md" | grep -c '\$50'""", ONE),
        Line('Cites both Requirements.', [
            ('grep -c \'HAL-REQ-002\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-003\' "$TURNS/1.md"', ONE)]),
        Line('Cites the file.', 'grep -c \'features/HAL-FEA-001-book-and-pay.md\' "$TURNS/1.md"', ONE),
        Line('Stays in one Project.', 'grep -c \'CRT-\' "$TURNS/1.md"', '0'),
    ]


def write():
    return [
        Line('Still nothing written.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]
