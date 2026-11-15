"""SU-01's key lines (acceptance/checks/SU-01-new-project-veneer.md, version 11),
each command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 2)
PRELUDE = ('P="$WS/projects/riverside-allotments"',)


def proposal(turn):
    lines = [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Shows the Veneer name.',
             'sed \'s/`[^`]*`//g\' "$TURNS/<n>.md" | grep -ciw initiative', ONE),
        Line('Code and slug.', [
            ('grep -c \'RAL\' "$TURNS/<n>.md"', ONE),
            ('grep -c \'riverside-allotments\' "$TURNS/<n>.md"', ONE)]),
        Line('People and roles.',
             'for p in \'Priya Shah\' \'Tom Okafor\' \'Dana Wells\'; do grep -c "$p" "$TURNS/<n>.md"; done | grep -cx 0', '0'),
    ]
    if turn == 1:
        return lines
    if turn == 2:
        return lines + [
            Line('After turn 2 only: the amend is in.',
                 'grep -c \'Lee Chen\' "$TURNS/2.md"', ONE),
        ]
    raise ValueError(f"SU-01 grades no proposal after turn {turn}")


def write():
    return [
        Line('One commit.',
             'git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
        Line('Commit message is the log heading.',
             'git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] setup \\| .*RAL\'', '1'),
        Line('Clean tree.',
             'git -C "$WS" status --porcelain --untracked-files=all', ""),
        Line("Exactly these files changed, the log in the run's month.",
             'diff <(git -C "$WS" diff --name-only "$BASE" HEAD) <(printf \'%s\\n\' projects/riverside-allotments/index.md "projects/riverside-allotments/log/$(date +%F | cut -c1-7).md" projects/riverside-allotments/project.md workspace.md)', ""),
        Line('Fixed code and slug.', [
            ('grep -c \'^Code: RAL$\' "$P/project.md"', '1'),
            ('grep -c \'^Slug: riverside-allotments$\' "$P/project.md"', '1')]),
        Line('People with canonical roles.', [
            ('grep -cE \'Dana Wells *\\| *Operator\' "$P/project.md"', '1'),
            ('grep -cE \'Priya Shah *\\| *Stakeholder\' "$P/project.md"', '1'),
            ('grep -cE \'Lee Chen *\\| *Stakeholder\' "$P/project.md"', '1'),
            ('grep -cE \'Tom Okafor *\\| *engineer\' "$P/project.md"', '1')]),
        Line('Files start with ID and title.', [
            ('head -1 "$P/index.md" | grep -c \'RAL\'', '1'),
            ('head -1 "$P/project.md" | grep -c \'RAL\'', '1')]),
        Line('Log entry.',
             'grep -cE \'^## \\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] setup \\| .*RAL\' "$P"/log/*.md', '1'),
        Line('Listed in the Workspace.',
             'grep -cE \'RAL.*projects/riverside-allotments/\' "$WS/workspace.md"', '1'),
        Line('Records stay canonical.', [
            ('git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiative|programme\'', '0'),
            ('git -C "$WS" diff --name-only "$BASE" HEAD | grep -ci initiative', '0')]),
        Line('Other records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/hall-bookings veneer.md', ""),
    ]
