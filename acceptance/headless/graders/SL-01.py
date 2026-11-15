"""SL-01's key lines (acceptance/checks/SL-01-vertical-features.md, version 5), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line, at_least

PROPOSAL_TURNS = (1,)
PRELUDE = (
    'P="$WS/projects/hall-bookings"',
    'NEW=$(git -C "$WS" diff --name-only --diff-filter=A "$BASE" HEAD -- \'projects/hall-bookings/epics/*/epic.md\')',
    'cov() { awk \'FNR==1{s=0} /^## /{s=($0=="## Covers")} s\' "$@" | grep -oE \'HAL-REQ-[0-9]{3}\'; }',
)


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Places every new Requirement.', [
            ('grep -c \'HAL-REQ-009\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-010\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-011\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-012\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-REQ-013\' "$TURNS/1.md"', ONE)]),
        Line('Gives the Feature with no Epic its Epic.',
             'grep -c \'HAL-FEA-002\' "$TURNS/1.md"', ONE),
        Line('A batch.',
             'grep -ci \'nothing is written yet\' "$TURNS/1.md"', ONE),
        Line('No leak-trap items.',
             'grep -c \'CRT-\' "$TURNS/1.md"', '0'),
    ]


def write():
    return [
        Line('One commit.',
             'git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
        Line('Commit message is the log heading.', [
            ('git -C "$WS" log -1 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] slice \\| \'', '1'),
            ('grep -cxF "## $(git -C "$WS" log -1 --format=%s)" "$P"/log/*.md', '1')]),
        Line('Clean tree.',
             'git -C "$WS" status --porcelain --untracked-files=all', ""),
        Line('Only slicing files changed.',
             'git -C "$WS" diff --name-only "$BASE" HEAD | grep -vE \'^projects/hall-bookings/(features/[^/]+\\.md|epics/[^/]+/epic\\.md|requirements/unplaced\\.md|index\\.md|log/[0-9]{4}-[0-9]{2}\\.md)$\'', ""),
        Line('Every new Requirement is in exactly one Feature, its line moved byte for byte.', [
            ('for r in HAL-REQ-009 HAL-REQ-010 HAL-REQ-011 HAL-REQ-012 HAL-REQ-013; do grep -l "^- \\*\\*$r\\*\\*" "$P"/features/HAL-FEA-*.md | wc -l; done | sort -u', '1'),
            ('diff <(git -C "$WS" show "$BASE":projects/hall-bookings/requirements/unplaced.md | grep -E \'^- \\*\\*HAL-REQ-(009|01[0-3])\\*\\*\' | sort) <(grep -hE \'^- \\*\\*HAL-REQ-(009|01[0-3])\\*\\*\' "$P"/features/HAL-FEA-*.md | sort)', "")]),
        Line('Gone from unplaced.',
             'grep -cE \'HAL-REQ-(009|01[0-3])\\b\' "$P/requirements/unplaced.md"', '0'),
        Line('Every Feature has exactly one Epic.',
             'for f in "$P"/features/HAL-FEA-*.md; do grep -lx "Feature: $(basename "$f" | cut -c1-11)" "$P"/epics/*/epic.md | wc -l; done | sort -u', '1'),
        Line('No Requirement covered by two Epics.',
             'cov "$P"/epics/*/epic.md | sort | uniq -d', ""),
        Line('Every new and active Requirement of the cancel Feature is covered.', [
            ('for r in HAL-REQ-005 HAL-REQ-007 HAL-REQ-009 HAL-REQ-010 HAL-REQ-011 HAL-REQ-012 HAL-REQ-013; do cov "$P"/epics/*/epic.md | grep -cx "$r"; done | sort -u', '1'),
            ('cov "$P"/epics/*/epic.md | grep -c \'HAL-REQ-006\'', '0')]),
        Line('An Epic covers only Requirements of its own Feature.',
             'for e in "$P"/epics/*/epic.md; do f=$(sed -n \'s/^Feature: //p\' "$e"); for r in $(cov "$e"); do grep -q "^- \\*\\*$r\\*\\*" "$P"/features/"$f"-*.md || echo "$r not in $f"; done; done', ""),
        Line("The handed-off Epic's Covers is unchanged.",
             'cov "$P"/epics/HAL-EPC-001-book-and-pay/epic.md | tr \'\\n\' \' \'', 'HAL-REQ-001 HAL-REQ-002 HAL-REQ-003 HAL-REQ-004 '),
        Line('The phone-screen Requirement is not a Feature on its own, and applies to another Epic.', [
            ('grep -cE \'^- \\*\\*HAL-REQ-\' $(grep -l \'^- \\*\\*HAL-REQ-013\\*\\*\' "$P"/features/HAL-FEA-*.md) </dev/null', at_least(2)),
            ('awk \'FNR==1{s=0} /^## /{s=($0=="## Applies here too")} s\' "$P"/epics/*/epic.md | grep -c \'HAL-REQ-013\'', ONE)]),
        Line('Each new Epic has the `epic.md` shape, no status, and its folder starts with its ID.', [
            ('for e in $NEW; do grep -E \'^## \' "$WS/$e" | tr \'\\n\' \'|\'; echo; done | sort -u', '## Covers|## Applies here too|## Depends on|## External items|## Left out|'),
            ('for e in $NEW; do grep -c \'^Status:\' "$WS/$e"; done | sort -u', '0'),
            ('for e in $NEW; do id=$(sed -n \'s/^Epic: //p\' "$WS/$e"); case "$e" in */epics/"$id"-*/epic.md) ;; *) echo "$e";; esac; done', "")]),
        Line('No pain point recorded.',
             'grep -l \'^Pain point:\' "$P"/epics/*/epic.md "$P"/features/*.md | wc -l', '0'),
        Line('IDs unique.', [
            ('ls "$P/features" | grep -oE \'^HAL-FEA-[0-9]{3}\' | sort | uniq -d', ""),
            ('ls "$P/epics" | grep -oE \'^HAL-EPC-[0-9]{3}\' | sort | uniq -d', "")]),
        Line('Indexes list every Feature and Epic.', [
            ('for f in "$P"/features/HAL-FEA-*.md; do grep -c "\\[$(basename "$f" | cut -c1-11)\\]" "$P/features/index.md"; done | sort -u', '1'),
            ('for e in "$P"/epics/*/epic.md; do grep -c "epics/$(basename "$(dirname "$e")")/epic.md" "$P/index.md"; done | sort -u', '1')]),
        Line('Records stay canonical.',
             'git -C "$WS" diff "$BASE" HEAD | grep -ciwE \'initiative|open item|spec\'', '0'),
    ]
