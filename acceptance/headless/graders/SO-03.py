"""SO-03's key lines (acceptance/checks/SO-03-standing.md, version 4), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import Line

PROPOSAL_TURNS = (1,)
PROPOSAL_PRELUDE = (
    'who() { awk -v n="**$1**" \'index($0, n) == 1 {f=1; next} /^\\*\\*/{f=0} f\' "$TURNS/1.md"; }',
    'line() { who "$1" | grep "^- $2:"; }',
)
AFTER_INSTALL = 'H="$WS/projects/hall-bookings"; F="$REPO/acceptance/fixtures"; cp -r "$F/signoff/hall-bookings/." "$H/" && cp -r "$F/signoff-readback/hall-bookings/." "$H/" && cat "$F/signoff-readback/log-entries.md" >> "$H/log/2026-11.md" && cp -r "$F/signoff-standing/hall-bookings/." "$H/" && cat "$F/signoff-standing/log-entries.md" >> "$H/log/2026-11.md" && cat "$F/signoff-standing/unplaced-lines.md" >> "$H/requirements/unplaced.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 Sign-offs and a replaced Decision"'


def proposal(turn):
    return [
        Line("One block per Stakeholder, and no one else's.", [
            ('grep -cE \'^\\*\\*(Margaret Osei|Tom Achebe)\\*\\*\' "$TURNS/1.md"', '2'),
            ('grep -cE \'^\\*\\*(Dana Wells|Ravi Kumar)\\*\\*\' "$TURNS/1.md"', '0')]),
        Line('Each block has the three lines.',
             'for p in \'Margaret Osei\' \'Tom Achebe\'; do for l in Agreed Disputed \'Not yet looked at\'; do line "$p" "$l" | wc -l; done; done | sort -u', '1'),
        Line('Margaret agreed the deposit only.',
             "line 'Margaret Osei' Agreed | grep -oE 'HAL-ANS-[0-9]{3}' | sort -u | tr '\\n' ' '", 'HAL-ANS-001 '),
        Line('Margaret disputes the late finish, through its Question.', [
            ("line 'Margaret Osei' Disputed | grep -c 'HAL-ANS-004'", '1'),
            ("line 'Margaret Osei' Disputed | grep -c 'HAL-Q-014'", '1')]),
        Line('The replaced Answer resets her Sign-off: the replacement is not yet looked at.', [
            ("line 'Margaret Osei' 'Not yet looked at' | grep -c 'HAL-ANS-007'", '1'),
            ("line 'Margaret Osei' Agreed | grep -cE 'HAL-ANS-00[57]'", '0')]),
        Line('Tom agreed the deposit only, and has not looked at the other two.', [
            ("line 'Tom Achebe' Agreed | grep -oE 'HAL-ANS-[0-9]{3}' | sort -u | tr '\\n' ' '", 'HAL-ANS-001 '),
            ("line 'Tom Achebe' 'Not yet looked at' | grep -oE 'HAL-ANS-00[47]' | sort -u | tr '\\n' ' '", 'HAL-ANS-004 HAL-ANS-007 '),
            ("line 'Tom Achebe' Disputed | grep -c 'HAL-'", '0')]),
        Line('The withdrawn Decision is not reported as standing.',
             'grep -E \'^- (Agreed|Disputed):\' "$TURNS/1.md" | grep -c \'HAL-ANS-005\'', '0'),
        Line('No yes/no "signed off", and nothing overdue.',
             'grep -ciE \'signed[ -]off|overdue\' "$TURNS/1.md"', '0'),
        Line('No court items.',
             'grep -c \'CRT-\' "$TURNS/1.md"', '0'),
    ]


def write():
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
    ]
