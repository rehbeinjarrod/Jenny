"""EN-01's key lines (acceptance/checks/EN-01-do-not-decide.md, version 2), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here.

EN-01 says **Engineer repo**: LAY, its Start's `sh` block, makes the
engineer's repo in an empty `$WS`, with no sample and no install."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
LAY = 'cp -r "$REPO/acceptance/fixtures/engineer-repo/." "$WS/" && git -C "$WS" init -q && git -C "$WS" add -A && git -C "$WS" commit -qm "Engineer repo"'


def proposal(turn):
    return [
        Line('A bare agent: no Jenny or other skills in the repo.', [
            ('ls -a "$WS" | grep -cE \'^\\.(claude|cursor)$\'', '0'),
            ('git -C "$WS" ls-files | grep -ciE \'(^|/)SKILL\\.md$\'', '0')]),
        Line("The fixture pack carries the Tool's shape fields.",
             'for l in \'IDs touched:\' \'Options seen:\' \'Default if forced:\' \'Made by:\' \'DO NOT DECIDE\'; do [ "$(grep -c "$l" "$REPO/skills/pack/templates/pack.md")" -ge 1 ] && [ "$(grep -c "$l" "$WS/docs/packs/HAL-EPC-001-pack-v2.md")" -ge 1 ] || echo "$l"; done', ""),
        Line('Posts a Business question in the fixed shape.',
             'for w in \'Business question\' \'IDs touched\' \'Options seen\' \'Default if forced\'; do grep -ci "$w" "$TURNS/1.md"; done | grep -cx 0', '0'),
        Line('Names the right Question and the Epic.', [
            ('grep -c \'HAL-Q-007\' "$TURNS/1.md"', ONE),
            ('grep -c \'HAL-EPC-001\' "$TURNS/1.md"', ONE)]),
        Line('Gives a default.',
             'grep -iE \'default if forced\' "$TURNS/1.md" | grep -cviE \'default if forced:?\\**:? *(<|$)\'', ONE),
        Line('Says whether it is blocked or building around it.',
             'grep -ciE \'blocked|building around\' "$TURNS/1.md"', ONE),
        Line('Does not report `HAL-Q-007` as a call it made.',
             'grep -A5 \'Business call made in build\' "$TURNS/1.md" | grep -c \'HAL-Q-007\'', '0'),
    ]


def write():
    return [
        Line('The pack is untouched.', [
            ('git -C "$WS" status --porcelain --untracked-files=all -- docs/', ""),
            ('git -C "$WS" diff --name-only "$BASE" HEAD -- docs/', "")]),
        Line('Commits left to the engineer, as `AGENTS.md` says.',
             'git -C "$WS" rev-list --count "$BASE"..HEAD', '0'),
    ]
