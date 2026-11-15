"""CP-01's key lines (acceptance/checks/CP-01-typed-note.md, version 8), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 2)
PRELUDE = ('H="$WS/projects/hall-bookings"',)


def proposal(turn):
    lines = [
        Line("Nothing written.", [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', "$BASE")]),
        Line("Says nothing is written yet.", "grep -c 'Nothing is written yet' \"$TURNS/<n>.md\"", ONE),
        Line("Names the hall Project.", [
            ("grep -ci 'hall' \"$TURNS/<n>.md\"", ONE),
            ("grep -c 'CRT-' \"$TURNS/<n>.md\"", "0")]),
        Line("Proposes both needs and the unknown.", [
            ("grep -ci 'calendar' \"$TURNS/<n>.md\"", ONE),
            ("grep -ciw 'map' \"$TURNS/<n>.md\"", ONE),
            ("grep -ciwE 'drinks?' \"$TURNS/<n>.md\"", ONE)]),
        Line("Proposes scores for the new Question.", [
            ("grep -ci 'impact' \"$TURNS/<n>.md\"", ONE),
            ("grep -ci 'uncertainty' \"$TURNS/<n>.md\"", ONE)]),
    ]
    if turn == 1:
        lines.append(Line("After turn 1 only: not yet reworded.",
                          "grep -c 'button that adds the booking' \"$TURNS/1.md\"", "0"))
    if turn == 2:
        lines.append(Line("After turn 2 only: the amend took.",
                          "grep -c 'button that adds the booking' \"$TURNS/2.md\"", ONE))
    return lines


def write():
    return [
        Line("One commit, clean tree.", [
            ('git -C "$WS" rev-list --count "$BASE"..HEAD', "1"),
            ('git -C "$WS" status --porcelain --untracked-files=all', "")]),
        Line("Commit message is the log heading.", [
            ("git -C \"$WS\" log -1 --format=%s | grep -cE '^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] capture \\| '", "1"),
            ('cat "$H"/log/*.md | grep -cxF "## $(git -C "$WS" log -1 --format=%s)"', "1")]),
        Line("Only capture's files changed, and no Feature created.", [
            ("git -C \"$WS\" diff --name-only \"$BASE\" HEAD | grep -vE '^projects/hall-bookings/(index\\.md|"
             "sources/(index|HAL-SRC-006-[a-z0-9-]+)\\.md|requirements/unplaced\\.md|"
             "features/(index|HAL-FEA-00[12]-[a-z0-9-]+)\\.md|questions/(index|HAL-Q-014-[a-z0-9-]+)\\.md|"
             "log/[0-9]{4}-[0-9]{2}\\.md)$'", ""),
            ("git -C \"$WS\" diff --name-only --diff-filter=A \"$BASE\" HEAD -- 'projects/hall-bookings/features'", "")]),
        Line("The Source, word for word, as a typed note.", [
            ("cat \"$H\"/sources/HAL-SRC-006-*.md | grep -cF 'add the booking to their calendar and show a map to the hall'", "1"),
            ("cat \"$H\"/sources/HAL-SRC-006-*.md | grep -c '^Kind: typed note$'", "1"),
            ("grep -c 'HAL-SRC-006' \"$H/sources/index.md\"", ONE)]),
        Line("Two Requirements from the one sentence, each citing the Source.",
             "grep -rhE '^- \\*\\*HAL-REQ-01(4|5)\\*\\* .* · Source: HAL-SRC-006 · Status: active$' \"$H\" | wc -l", "2"),
        Line("The amended wording is the one written.", [
            ("grep -rhE '^- \\*\\*HAL-REQ-01(4|5)\\*\\* ' \"$H\" | grep -c 'button that adds the booking'", "1"),
            ("grep -rhE '^- \\*\\*HAL-REQ-01(4|5)\\*\\* ' \"$H\" | grep -ciw 'map'", "1")]),
        Line("The new Question, scored.", [
            ('ls "$H"/questions/HAL-Q-014-*.md | wc -l', "1"),
            ("cat \"$H\"/questions/HAL-Q-014-*.md | grep -cE '^(Impact|Uncertainty|Score|Score reason): .+'", "4"),
            ("f=$(ls \"$H\"/questions/HAL-Q-014-*.md); i=$(sed -n 's/^Impact: //p' \"$f\"); "
             "u=$(sed -n 's/^Uncertainty: //p' \"$f\"); s=$(sed -n 's/^Score: //p' \"$f\"); "
             "[ \"$((i*u))\" = \"$s\" ] && echo ok", "ok"),
            ("cat \"$H\"/questions/HAL-Q-014-*.md | grep -cE '^Status: (open|parked)$'", "1"),
            ("cat \"$H\"/questions/HAL-Q-014-*.md | grep -c '^Raised from: HAL-SRC-006$'", "1"),
            ("grep -c 'HAL-Q-014' \"$H/questions/index.md\"", ONE)]),
        Line("Records stay canonical.",
             "git -C \"$WS\" diff \"$BASE\" HEAD | grep -ciwE 'initiatives?|programmes?|open items?|specs?'", "0"),
        Line("Other records untouched.",
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md outbox', ""),
    ]
