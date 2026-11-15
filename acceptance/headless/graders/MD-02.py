"""MD-02's key lines (acceptance/checks/MD-02-later-skill-routes.md, version 2), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
AFTER_INSTALL = ('cp -r "$REPO/acceptance/fixtures/skill-headcount" "$SK/headcount" '
                 '&& git -C "$WS" add -A && git -C "$WS" commit -qm "Test: add headcount skill"')


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('The added skill\'s shape.', [
            (r'''grep -c '^\*\*Headcount\*\*$' "$TURNS/1.md"''', '1'),
            ('''grep -c '^`HAL`: 3 people$' "$TURNS/1.md"''', '1')]),
        Line('Each person.', [
            ('grep -c \'Dana Wells\' "$TURNS/1.md"', ONE),
            ('grep -c \'Margaret Osei\' "$TURNS/1.md"', ONE),
            ('grep -c \'Ravi Kumar\' "$TURNS/1.md"', ONE)]),
        Line('Stays in one Project.', 'grep -c \'CRT\' "$TURNS/1.md"', '0'),
        Line('The mode itself is unchanged.', 'diff -r -x VERSION "$REPO/skills/jenny" "$SK/jenny"', ""),
    ]


def write():
    return [
        Line('Still nothing written.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]
