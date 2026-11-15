"""LK-05's key lines (acceptance/checks/LK-05-replaced-decision.md, version 7), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('The current rule.', 'grep -ciw \'half\' "$TURNS/1.md"', ONE),
        Line('Cites the current Decision and Requirement.', [
            ('grep -c \'HAL-ANS-003\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-007\' "$TURNS/1.md"', ONE)]),
        Line('Names the current Decision\'s owner.', 'grep -c \'Margaret Osei\' "$TURNS/1.md"', ONE),
        Line('Notes the replacement.', [
            ('grep -c \'HAL-ANS-002\' "$TURNS/1.md"', ONE),
            ('grep -ciE \'replac|supersed|withdr\' "$TURNS/1.md"', ONE)]),
        Line('Stays in one Project.', 'grep -ciE \'CRT-|24 hours\' "$TURNS/1.md"', '0'),
    ]


def write():
    return [
        Line('Still nothing written.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]
