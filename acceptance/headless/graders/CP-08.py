"""CP-08's key lines (acceptance/checks/CP-08-reject.md, version 4), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)


def proposal(turn):
    lines = [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('A batch was proposed.', [
            ('grep -c \'Nothing is written yet\' "$TURNS/1.md"', ONE),
            ('grep -ci \'calendar\' "$TURNS/1.md"', ONE)]),
    ]
    return lines


def write():
    return [
        Line('No commit, no file changes.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]

