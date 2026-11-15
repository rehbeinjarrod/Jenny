"""UN-02's key lines (acceptance/checks/UN-02-shape-next.md, version 6), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 2)
PRELUDE = (
    'P="$WS/projects/hall-bookings"',
    'Q="projects/hall-bookings/questions/HAL-Q-007-member-rate-for-guests.md"',
)


def proposal(turn):
    nothing = Line('Nothing written, after each turn.', [
        ('git -C "$WS" status --porcelain --untracked-files=all', ""),
        ('git -C "$WS" rev-parse HEAD', '$BASE')])
    if turn == 1:
        return [
            nothing,
            Line('Turn 1, the top 5 in rank order.', [
                ('for q in HAL-Q-007 HAL-Q-009 HAL-Q-008 HAL-Q-003 HAL-Q-010; do grep -n -m1 "$q" "$TURNS/1.md" | cut -d: -f1; done | sort -nc && echo ordered', 'ordered'),
                ('for q in HAL-Q-007 HAL-Q-009 HAL-Q-008 HAL-Q-003 HAL-Q-010; do grep -c "$q" "$TURNS/1.md"; done | grep -cx 0', '0')]),
            Line('Turn 1, each with its score on its own line.', [
                ('grep \'HAL-Q-007\' "$TURNS/1.md" | grep -ciE \'score:? *3\\b\'', ONE),
                ('grep \'HAL-Q-009\' "$TURNS/1.md" | grep -ciE \'score:? *9\\b\'', ONE),
                ('grep \'HAL-Q-008\' "$TURNS/1.md" | grep -ciE \'score:? *6\\b\'', ONE),
                ('grep \'HAL-Q-003\' "$TURNS/1.md" | grep -ciE \'score:? *6\\b\'', ONE),
                ('grep \'HAL-Q-010\' "$TURNS/1.md" | grep -ciE \'score:? *4\\b\'', ONE)]),
            Line('Turn 1, the guess flagged.',
                 'grep \'HAL-Q-007\' "$TURNS/1.md" | grep -ciE \'guess\'', ONE),
            Line('Turn 1, only five: the sixth, the parked, answered and withdrawn ones left out.',
                 'grep -cE \'HAL-Q-(011|005|001|002|006)\\b\' "$TURNS/1.md"', '0'),
            Line('Turn 1, ends by offering to shape the top one.',
                 'tail -n 3 "$TURNS/1.md" | grep -c \'HAL-Q-007\'', ONE),
            Line('Turn 1, no leak-trap items.',
                 'grep -c \'CRT-\' "$TURNS/1.md"', '0'),
        ]
    if turn == 2:
        return [
            nothing,
            Line('Turn 2, the plan for `HAL-Q-007`.', [
                ('grep -c \'HAL-Q-007\' "$TURNS/2.md"', ONE),
                ('grep -c \'Margaret Osei\' "$TURNS/2.md"', ONE),
                ('grep -i \'technique\' "$TURNS/2.md" | grep -ciE \'message|conversation|workshop|document review|demo or prototype|spike\'', ONE),
                ('grep -i \'chase by\' "$TURNS/2.md" | grep -cE \'[0-9]{4}-[0-9]{2}-[0-9]{2}\'', ONE)]),
            Line('Turn 2, a batch.',
                 'grep -ci \'nothing is written yet\' "$TURNS/2.md"', ONE),
        ]
    raise ValueError(f"UN-02 grades no proposal after turn {turn}")


def write():
    return [
        Line('One commit.',
             'git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
        Line('Commit message is the log heading.', [
            ('git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] up-next \\| .*HAL-Q-007\'', '1'),
            ('grep -cE \'^## \\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] up-next \\| .*HAL-Q-007\' "$P"/log/*.md', '1')]),
        Line('Clean tree.',
             'git -C "$WS" status --porcelain --untracked-files=all', ""),
        Line("Exactly these files changed, the log in the run's month.",
             'diff <(git -C "$WS" diff --name-only "$BASE" HEAD) <(printf \'%s\\n\' "projects/hall-bookings/log/$(date +%F | cut -c1-7).md" "$Q" projects/hall-bookings/questions/index.md)', ""),
        Line('Only the plan fields and status changed in the Question.',
             'git -C "$WS" diff -U0 "$BASE" HEAD -- "$Q" | grep -E \'^[-+]\' | grep -vE \'^(\\+\\+\\+|---) \' | grep -vE \'^[-+](Status|Ask|Technique|Chase by): \'', ""),
        Line('The plan.', [
            ('grep -cx \'Status: chasing\' "$WS/$Q"', '1'),
            ('grep -cx \'Ask: Margaret Osei\' "$WS/$Q"', '1'),
            ('grep -cxE \'Technique: (message|conversation|workshop|document review|demo or prototype|delivery-team Spike)\' "$WS/$Q"', '1'),
            ('grep -cxE \'Chase by: [0-9]{4}-[0-9]{2}-[0-9]{2}\' "$WS/$Q"', '1')]),
        Line('The ask has not gone out.',
             'grep -c \'^Asked:\' "$WS/$Q"', '0'),
        Line('The index row moves to chasing, score kept, no other row touched.', [
            ('grep \'HAL-Q-007\' "$P/questions/index.md" | grep -cE \'\\| *chasing *\\| *3 *\\|\'', '1'),
            ('git -C "$WS" diff -U0 "$BASE" HEAD -- projects/hall-bookings/questions/index.md | grep -E \'^[-+]\\|\' | grep -vc \'HAL-Q-007\'', '0')]),
        Line('No score changed anywhere.',
             'git -C "$WS" diff "$BASE" HEAD | grep -cE \'^[-+](Impact|Uncertainty|Score|Score reason):\'', '0'),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiative|open item|spec\'', '0'),
    ]
