"""MD-01's key lines (acceptance/checks/MD-01-version-mismatch.md, version 8), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
PROPOSAL_PRELUDE = ('V=$(cat "$REPO/VERSION")',)
AFTER_INSTALL = ('f="$WS/workspace.md"; sed \'s/^Tool version: .*/Tool version: 0.0.9/\' "$f" > "$f.new" && mv "$f.new" "$f" '
                 '&& git -C "$WS" commit -qam "Test: version mismatch"')


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Names both versions.', [
            (r'''grep -c '0\.0\.9' "$TURNS/1.md"''', ONE),
            ('grep -cF "$V" "$TURNS/1.md"', ONE)]),
        Line('No work done: no answer, no citations.', [
            (r'''grep -c '\$50\|\$27\|\$135' "$TURNS/1.md"''', '0'),
            (r'''grep -c 'HAL-REQ-\|HAL-FEA-' "$TURNS/1.md"''', '0')]),
    ]


def write():
    return [
        Line('Still nothing written.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]
