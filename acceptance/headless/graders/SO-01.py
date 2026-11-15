"""SO-01's key lines (acceptance/checks/SO-01-view-and-publish.md, version 6), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1, 3)
PRELUDE = (
    'P="$WS/projects/hall-bookings"',
    'V="$P/epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret.md"',
    'O="$WS/outbox/HAL-EPC-001-signoff-view-v1-margaret.html"',
    'sec() { awk -v h="^## $1" \'$0 ~ h {f=1; next} /^## /{f=0} f\' "$V"; }',
    'prose() { awk \'/^```/{f=!f;next} !f\' "$V" | sed \'s/`[^`]*`//g\'; }',
    'nodes() { awk \'/^```mermaid/{f=1; split("", s); next} f && /^```/{f=0; c=0; for (k in s) c++; print c; next} f { t=$0; while (match(t, /[A-Za-z0-9_]+(\\[|\\{|\\(\\()/)) { id=substr(t, RSTART, RLENGTH); sub(/[\\[{(]+$/, "", id); s[id]=1; t=substr(t, RSTART+RLENGTH) } }\' "$V"; }',
)
AFTER_INSTALL = 'cp -r "$REPO/acceptance/fixtures/signoff/hall-bookings/." "$WS/projects/hall-bookings/" && git -C "$WS" add -A && git -C "$WS" commit -qm "Overlay: HAL-EPC-001 pack v2 for Sign-off"'


def proposal(turn):
    if turn == 1:
        return [
            Line('Nothing written.', [
                ('git -C "$WS" status --porcelain --untracked-files=all', ""),
                ('git -C "$WS" rev-parse HEAD', '$BASE')]),
            Line('The view is a new file for Margaret.',
                 'grep -c \'signoff-view-v1-margaret.md\' "$TURNS/1.md"', ONE),
            Line('A batch.',
                 'grep -ci \'nothing is written yet\' "$TURNS/1.md"', ONE),
            Line('No court items.',
                 'grep -c \'CRT-\' "$TURNS/1.md"', '0'),
        ]
    if turn == 3:
        return [
            Line('The view is written; nothing posted or put in the outbox yet.', [
                ('git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
                ('git -C "$WS" status --porcelain --untracked-files=all', ""),
                ('test -e "$WS/outbox" && echo yes', "")]),
            Line('The proposal names the outbox file.',
                 'grep -c \'outbox/HAL-EPC-001-signoff-view-v1-margaret.html\' "$TURNS/3.md"', ONE),
            Line('A batch.',
                 'grep -ci \'nothing is written yet\' "$TURNS/3.md"', ONE),
        ]
    raise ValueError(f"SO-01 grades no proposal after turn {turn}")


def write():
    return [
        Line('Two commits, one per operation.',
             'git -C "$WS" rev-list --count "$BASE"..HEAD', '2'),
        Line('Both messages are log headings.', [
            ('git -C "$WS" log -2 --format=%s | grep -cE \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] signoff \\| \'', '2'),
            ('for m in "$(git -C "$WS" log -1 --format=%s)" "$(git -C "$WS" log -1 --skip=1 --format=%s)"; do cat "$P"/log/*.md | grep -cxF "## $m"; done | sort -u', '1')]),
        Line('Clean tree.',
             'git -C "$WS" status --porcelain --untracked-files=all', ""),
        Line('The view commit adds the view and the log only.', [
            ('git -C "$WS" diff --name-status "$BASE" HEAD~1 | grep -vE \'^(A\tprojects/hall-bookings/epics/HAL-EPC-001-book-and-pay/signoff-view-v1-margaret\\.md|M\tprojects/hall-bookings/log/[0-9]{4}-[0-9]{2}\\.md)$\'', ""),
            ('git -C "$WS" diff --name-status "$BASE" HEAD~1 | grep -c \'^A\'', '1')]),
        Line('The publish commit adds the outbox file and the log only, and leaves the view as written.', [
            ('git -C "$WS" diff --name-status HEAD~1 HEAD | grep -vE \'^(A\toutbox/HAL-EPC-001-signoff-view-v1-margaret\\.html|M\tprojects/hall-bookings/log/[0-9]{4}-[0-9]{2}\\.md)$\'', ""),
            ('test -s "$O" && echo ok', 'ok')]),
        Line('The order.',
             'grep -E \'^## \' "$V" | grep -oE \'🔴|🟠|✅|⚪|How it works|Also worth knowing\' | tr \'\\n\' \' \'', '🔴 🟠 ✅ ⚪ How it works Also worth knowing '),
        Line('Addressed to Margaret by name.',
             'head -8 "$V" | grep -c \'Margaret\'', ONE),
        Line('The guess is in 🔴.',
             "sec 🔴 | grep -c 'HAL-Q-007'", ONE),
        Line("Her calls are in 🟠's table; others' are named but not in it.", [
            ("sec 🟠 | grep '^|' | grep -oE 'HAL-Q-0(04|13)' | sort -u | wc -l", '2'),
            ("sec 🟠 | grep '^|' | grep -cE 'HAL-Q-0(07|08|10)'", '0'),
            ("sec 🟠 | grep -v '^|' | grep -c 'HAL-Q-008'", ONE)]),
        Line('Checkboxes only on the Decisions she has not agreed, one each.', [
            ('grep -cE \'^\\s*[-*] \\[[ xX]\\]\' "$V"', '2'),
            ('grep -E \'^\\s*[-*] \\[[ xX]\\]\' "$V" | grep -cvE \'HAL-ANS-00[45]\'', '0'),
            ('for a in HAL-ANS-004 HAL-ANS-005; do grep -E \'^\\s*[-*] \\[ \\]\' "$V" | grep -c "$a"; done | sort -u', '1')]),
        Line('The Decisions are in ✅, the agreed one without a box.',
             "sec ✅ | grep -oE 'HAL-ANS-00[145]' | sort -u | wc -l", '3'),
        Line("The engineer's Decision is flagged.",
             'grep \'HAL-ANS-004\' "$V" | grep -ci \'decided during build\'', ONE),
        Line('The three N/A rows.',
             "sec ⚪ | grep -cE '^\\s*[-*] '", '3'),
        Line('Left out is worth knowing.',
             "sec 'Also worth knowing' | grep -c 'HAL-REQ-008'", ONE),
        Line('At least one diagram, none over about 7 nodes (8 at most, besides start and stop).', [
            ('grep -c \'^```mermaid\' "$V"', ONE),
            ("nodes | awk '$1 > 8' | wc -l", '0')]),
        Line('No Source IDs.',
             'grep -c \'HAL-SRC-\' "$V"', '0'),
        Line('Shown names, no renamed canonical term outside code.', [
            ("prose | grep -oiwE 'projects?|epics?|questions?' | wc -l", '0'),
            ("prose | grep -ciw 'spec'", ONE)]),
        Line('The same order, addressed to Margaret.', [
            ('grep -oE \'<h2>[^<]*\' "$O" | grep -oE \'🔴|🟠|✅|⚪|How it works|Also worth knowing\' | tr \'\\n\' \' \'', '🔴 🟠 ✅ ⚪ How it works Also worth knowing '),
            ('grep -c \'Margaret\' "$O"', ONE)]),
        Line('Task items only on the two Decisions.', [
            ('grep -o \'data-type="task-item"\' "$O" | wc -l', '2'),
            ('tr -d \'\\n\' < "$O" | sed \'s/<li data-type="task-item"/\\n&/g\' | grep \'^<li data-type="task-item"\' | sed \'s/<\\/li>.*//\' | grep -cvE \'HAL-ANS-00[45]\'', '0')]),
        Line('No Markdown checkboxes left.',
             'grep -c \'\\[ \\]\' "$O"', '0'),
        Line('Each diagram is a whiteboard embed with its Mermaid source in an expand.', [
            ('[ "$(grep -o \'data-card-appearance="embed"\' "$O" | wc -l)" -ge "$(grep -c \'^```mermaid\' "$V")" ] && echo ok', 'ok'),
            ('[ "$(grep -o \'<details\' "$O" | wc -l)" -ge "$(grep -c \'^```mermaid\' "$V")" ] && echo ok', 'ok'),
            ('grep -c \'flowchart\' "$O"', ONE)]),
        Line('A body fragment.',
             'grep -ciE \'<html|<body|<head\' "$O"', '0'),
        Line('No Source IDs.',
             'grep -c \'HAL-SRC-\' "$O"', '0'),
        Line('Records untouched.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects/court-bookings veneer.md workspace.md projects/hall-bookings/questions projects/hall-bookings/project.md', ""),
    ]
