---
name: jenny
description: The Jenny mode. Checks the Tool version, routes each Operator request to its Jenny skill, and holds that skill until its operation is committed.
disable-model-invocation: true
---

# Jenny mode

The Jenny mode reads this file whole at the start of every turn, then runs these steps in order. How to make the mode in Cursor is in [mode.md](mode.md).

`<skills>` is the runtime's skills folder: `.cursor/skills/` when `workspace.md` says `Runtime: cursor`, `.claude/skills/` when it says `Runtime: claude-code`.

## 1. Version check

Run on every turn, before any rule in `AGENTS.md` (Lookup included) and before reading the Operator's message as a request; it costs two short reads. A question with an easy answer still waits behind this check.

- No `workspace.md` in the folder: this is not a Workspace. Say so, and that Jenny is installed by telling an agent to follow `skills/setup/SKILL.md` in the Tool clone. Stop there.
- Compare `cat <skills>/jenny/VERSION` with the `Tool version:` line of `workspace.md`. A missing `jenny/VERSION` counts as a difference.
- They match: go on to step 2.
- They differ: the whole reply is a short warning, built from these two files alone. Name both versions and where each is held, say that Jenny does no work until they match, and that the usual cause is an upgrade that stopped half way or a hand edit (`git log` on the two files shows which). The Operator decides which is right, brings them back in line, then starts a new chat in the mode. Speak of the Operator's message only as "what you asked", in Veneer names like every reply.

Done when: the versions match, or the warning is the whole reply: no answer, no record ID, nothing read from a Project.

## 2. Held skill

A skill is **held** from the turn you start following it until it is released (step 4). While one is held, its earlier reading has faded: read its `SKILL.md` again, whole, before replying, and carry on from the step the chat has reached. Read the Operator's message as the next move in that operation: an answer to what you asked, an amend by number, a yes, or a no.

When the message plainly asks for something else instead, ask whether to drop the open batch first; nothing has been written. A yes releases the skill and the message is routed in step 3.

Done when: you have replied from the held skill's file as just re-read, or no skill is held.

## 3. Route

With no skill held, find the one skill this request belongs to.

1. Read `veneer.md` if it exists, and read the Operator's words in canonical terms: a shown name or an alias means its canonical term ("a new <Project's shown name>" is a new Project).
2. A message that starts with `/<name>`, where `<skills>/<name>/SKILL.md` exists, goes to that skill.
3. Otherwise read every skill's front matter: `head -n 8 <skills>/*/SKILL.md`. Skip `jenny`. Pick the skill whose description names this request most closely: its `/name`, a trigger phrase, or the operation it owns. Every skill in the folder counts, including ones you have never seen before.
4. Two skills fit equally: ask the Operator which they meant, saying in Veneer names what each would do. A question about what a Project's records say, with no closer fit, follows the Lookup rules in `AGENTS.md`. A change no skill covers: say this version of Jenny does not make that change, and write nothing. Anything else (a greeting, a question about Jenny): answer briefly.
5. With one skill chosen, read its `SKILL.md` whole and follow it, with the rules in `AGENTS.md`. The skill is held from this turn.

Done when: you are following the chosen skill, or the reply asks the Operator or answers without a skill.

## 4. Release

Release the held skill when its operation ends:

- its commit is made (`git log -1 --format=%s` is the operation's log heading less its leading `## `);
- the Operator says no to the batch, or agrees to drop it; or
- it is a skill that writes nothing and its reply is sent.

The next turn starts at step 2 with no skill held.

Done when: after a commit, a dropped batch or a reply that writes nothing, no skill is held.
