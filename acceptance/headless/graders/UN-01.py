"""UN-01's key lines (acceptance/checks/UN-01-chase-list.md, version 6), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
PROPOSAL_PRELUDE = (
    'D_012=$(( ($(date -ud "$(date +%F)" +%s) - $(date -ud 2026-11-08 +%s)) / 86400 ))',
    'D_004=$(( ($(date -ud "$(date +%F)" +%s) - $(date -ud 2026-11-10 +%s)) / 86400 ))',
)


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Lists every chasing Question.', [
            ('grep -c \'HAL-Q-012\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-Q-004\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-Q-013\' "$TURNS/1.md"', ONE)]),
        Line('Overdue first, most overdue at the top.',
             'for q in HAL-Q-012 HAL-Q-004 HAL-Q-013; do grep -n -m1 "$q" "$TURNS/1.md" | cut -d: -f1; done | sort -nc && echo ordered', 'ordered'),
        Line('Who was asked.', [
            ('grep -c \'Ravi Kumar\' "$TURNS/1.md"', ONE),
            ('grep -c \'Margaret Osei\' "$TURNS/1.md"', ONE)]),
        Line("Days overdue, on each Question's own line.", [
            ('grep \'HAL-Q-012\' "$TURNS/1.md" | grep -cE "\\b$D_012 days?\\b"', ONE),
            ('grep \'HAL-Q-004\' "$TURNS/1.md" | grep -cE "\\b$D_004 days?\\b"', ONE)]),
        Line('Not yet due is not called overdue.',
             'grep \'HAL-Q-013\' "$TURNS/1.md" | grep -ci \'overdue\'', '0'),
        Line('Handed-off nudge with the last check date, on one line.',
             'grep \'HAL-EPC-001\' "$TURNS/1.md" | grep -c \'2026-11-09\'', ONE),
        Line('Ends by offering to shape the top one.',
             'tail -n 3 "$TURNS/1.md" | grep -c \'HAL-Q-007\'', ONE),
        Line('No answered, parked or withdrawn Question.',
             'grep -cE \'HAL-Q-00[1256]\\b\' "$TURNS/1.md"', '0'),
        Line('No leak-trap items.', [
            ('grep -c \'CRT-\' "$TURNS/1.md"', '0'),
            ('grep -c \'Joe Park\' "$TURNS/1.md"', '0')]),
    ]


def write():
    return [
        Line('Still nothing written.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]
