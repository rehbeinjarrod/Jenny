"""SU-02's key lines (acceptance/checks/SU-02-upgrade.md, version 11), each
command word for word from the Check. test_key_parity.py holds the two in
step: a change to the Check's keys is a change here.

SU-02 says **No install**: LAY, its Start's `sh` block, lays Tool 0.2.0's
install over the committed sample in place of an install."""

from grade import AT_LEAST_ONE as ONE, Line

PROPOSAL_TURNS = (1,)
PROPOSAL_PRELUDE = ('V="$(cat "$REPO/VERSION")"',)
PRELUDE = ('V="$(cat "$REPO/VERSION")"',)
LAY = 'cp -r "$REPO/acceptance/fixtures/workspace-0.2.0/." "$WS/" && mkdir -p "$WS/.claude" && mv "$WS/skills" "$SK" && sed -i "s|^Clone path: .*|Clone path: $REPO|" "$WS/workspace.md" && git -C "$WS" add -A && git -C "$WS" commit -qm "[2026-11-11] install | Tool 0.2.0 for claude-code"'


def proposal(turn):
    return [
        Line('Nothing written.', [
            ('git -C "$WS" status --porcelain --untracked-files=all', ""),
            ('git -C "$WS" rev-parse HEAD', '$BASE')]),
        Line('Names both versions.', [
            ('grep -c \'0\\.2\\.0\' "$TURNS/1.md"', ONE),
            ('grep -cF "$V" "$TURNS/1.md"', ONE)]),
        Line('Shows the CHANGELOG entries in between.',
             'grep -c \'0\\.3\\.0\' "$TURNS/1.md"', ONE),
        Line('Says nothing is written yet.',
             'grep -c \'Nothing is written yet\' "$TURNS/1.md"', ONE),
        Line('The restart instruction is in the batch, outside fenced blocks, before "Nothing is written yet": '
             'a new or fresh chat, session or conversation in any wording ("a new Claude Code session", '
             '"a new chat in the Jenny mode"), or restarting Claude Code or Cursor.',
             'awk \'/^ *```/{f=!f;next} f{next} /(^|[^A-Za-z])([Nn]ew|[Ff]resh) ([^ ]+ )?([^ ]+ )?([^ ]+ )?(chat|session|conversation)([^A-Za-z]|$)|[Rr]estart (Claude Code|Cursor)|[Ss]tart Claude Code again/ && !r {r=NR} /Nothing is written yet/ {n=NR} END {print (r && r < n) ? "ok" : "no"}\' "$TURNS/1.md"', 'ok'),
    ]


def write():
    return [
        Line('One commit.',
             'git -C "$WS" rev-list --count "$BASE"..HEAD', '1'),
        Line('Commit message is the log heading.',
             'git -C "$WS" log -1 --format=%s | grep -E \'^\\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] upgrade \\| Tool 0\\.2\\.0 → \' | grep -cF "→ $V"', '1'),
        Line('Log entry.',
             'grep -cE \'^## \\[[0-9]{4}-[0-9]{2}-[0-9]{2}\\] upgrade \\| Tool 0\\.2\\.0 → \' "$WS"/log/*.md', '1'),
        Line('Clean tree.',
             'git -C "$WS" status --porcelain --untracked-files=all', ""),
        Line("The Tool version setting is this version's.",
             'grep -cx "Tool version: $V" "$WS/workspace.md"', '1'),
        Line('Only the Tool version setting changed.',
             'git -C "$WS" diff -U0 "$BASE" HEAD -- workspace.md | grep -E \'^[-+]\' | grep -vE \'^(\\+\\+\\+|---) \' | grep -v \'^[-+]Tool version: \'', ""),
        Line("Operator's MCP entry kept.",
             'git -C "$WS" diff --name-only "$BASE" HEAD -- .mcp.json CLAUDE.md', ""),
        Line('No record changed.',
             'git -C "$WS" diff --name-only "$BASE" HEAD -- projects veneer.md', ""),
        Line("Exactly these files outside the skills folder changed, the log in the run's month.",
             'diff <(git -C "$WS" diff --name-only "$BASE" HEAD | grep -v "^${SK#"$WS"/}/") <(printf \'%s\\n\' AGENTS.md "log/$(date +%F | cut -c1-7).md" workspace.md)', ""),
    ]
