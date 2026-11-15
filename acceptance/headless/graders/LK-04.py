"""LK-04's key lines (acceptance/checks/LK-04-unknown-open-question.md, version 7), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Points at the open Question.', 'grep -c \'HAL-Q-003\' "$TURNS/1.md"', ONE),
        Line('Says it is not known.',
             '''grep -ciE 'not (yet )?(known|settled|decided|answered)|unknown|open item|no answer' "$TURNS/1.md"''', ONE),
        Line('Cites where the Question is.',
             r'''grep -cE 'questions/(HAL-Q-003-committee-cancels|index)\.md' "$TURNS/1.md"''', ONE),
        Line('Nothing invented from the court Project.', r'''grep -ciE '\$20|credit|CRT-' "$TURNS/1.md"''', '0'),
        Line('No guessed answer in the gap.',
             r"""sed -n '/Not known yet/,$p' "$TURNS/1.md" | grep -ciE 'probabl|likely|might|could|perhaps|possib|option|for example|such as|e\.g\.|credit|rebook|another date'""", '0'),
        Line('Says who the gap is waiting on.',
             """sed -n '/Not known yet/,$p' "$TURNS/1.md" | grep -ciE 'waiting on|not (been )?asked|nobody|no one'""", ONE),
    ]


def write():
    return [
        Line('Still nothing written.', [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
    ]
