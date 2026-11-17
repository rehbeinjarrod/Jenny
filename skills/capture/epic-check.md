# Capture: Handed-off Epic check

Part of Capture, read when [SKILL.md](SKILL.md) sends you here. A section named in bold (**1. Find the Project**, **2. Read the material into candidates**, **3. Propose**, **Answers**) is in SKILL.md.

Checking a handed-off Epic is a Capture of its **tech face**: the engineers' Jira Epic named on the `Tech face:` line in `epic.md`, its child work items (Stories), and all their comments. PRs and repos are never read. Engineers post two fixed shapes there, as the pack's "For the agent" block tells them: a `Business question` and a `Business call made in build`. Say each shape's name in a code span, as here, every time, and call an engineer's ask by its shape's name: their `Business question`.

1. **Gather.** Find the Epic: for a Jira key, `grep -l 'Tech face: \[<key>\]' projects/*/epics/*/epic.md`; for an Epic named in words, as the Lookup rules say. An Epic with no `Tech face:` line is not handed off: say so and propose nothing. Read what **1. Find the Project** reads, plus `epic.md` and the handed-off pack it names. The **last check** is the latest log entry headed `capture | <Epic ID> handed-off Epic check` in `log/*.md`; with none, the `Handed off:` date.

   Read the tech face through the Atlassian MCP's Jira tools: the Epic, every work item whose parent it is, and each one's comments, with their IDs, authors and created and updated dates. When your instructions name a file standing in for the MCP for the tech face's URL, read that file instead: it is what the MCP returned. When the read fails, say so in one line and propose nothing.

   Done when: you hold the Epic's records, the last check, and every work item and comment on the tech face.

2. **Only what changed.** A comment is **seen** when its ID is named in an earlier check's log entry for this Epic, or it was created before the date of an earlier check whose entry names no comment IDs. Every other comment is **new**. A seen comment whose own updated date is on or after the last check is **changed**: read it again whole, and only what the records do not already hold is material. Epic and Story descriptions are context for reading the comments; engineers post both shapes as comments. Say in one line how many comments were seen already, without restating them.

   Done when: every comment is seen, new or changed.

3. **Candidates**, from the new and changed comments alone, in work-item order, then comment order:
   - **A `Business question`** about something no record settles: a new Question, what the engineer asked, put plainly, with `Affects:` the Requirement and Answer IDs it touches, scored as **2. Read the material into candidates** says. `building around it` means `Building on a guess: yes` and `Needed by: <Epic ID>`; `blocked` means `Needed by: <Epic ID>`.
   - **A `Business question` about an open Question** it names: no new Question. Propose `Building on a guess: yes` (when building around it) and `Needed by: <Epic ID>` on that Question, re-ranked in `questions/index.md`.
   - **Pushback**: a `Business question` against an active Decision it names. A new Question with `Affects: <Answer ID>`, `Building on a guess: yes` when they build around it, `Needed by: <Epic ID>`. The Decision stays in force: its Answer line is not touched, and the item says so ("`<Answer ID>` stays in force until `<Q ID>` is answered").
   - **A `Business call made in build`**: a Decision, owned by the engineer who made it or posted it (`Made by: agent` is owned by the engineer who posted it). Every Decision starts life as a Question: it answers the open Question its IDs name, or else a new Question is raised and answered in the same batch, with `Status: answered`. Its item says "decided during build". It shows as a pain point in the next pack and Sign-off view, from the owner's People role. An engineer not in People is proposed as a Person with role `engineer`, in an item before the Answer.
   - Anything else (status updates, PR links, chat): not used, listed in one line after the items.

   Done when: every new and changed comment is a candidate or listed as not used.

4. **Propose** as **3. Propose** says, under the heading `Capture: <shown name for Epic> <Epic ID> check of <key>`:
   - **Item 1, the Source**: `Kind: Jira item`, `Owner:` the authors of the comments kept, `Date:` the newest comment kept, `URL:` the tech face's URL and `Read:` today, in place of `Captured:`. It keeps each comment used word for word, under its own line `<key> · comment <ID> · <author> · <date>`. The batch shows each kept comment in a fenced `text` block, exactly as it will be kept. A check's Source holds only this check's comments, so it has no `Previous reading:`.
   - Each Question item leads with "<shown name for Question> <ID>: <its wording>", then its header values, so its wording never sits under a field label.
   - With nothing new or changed, the batch is the log entry alone, so the check date is kept.
   - **The Operator answers in the same batch** (an amend such as "Margaret says each booking takes its own deposit"): add a `typed note` Source owned by the Operator holding their words, the Answer and its effects as **Answers** says, and its Jira reply, then show the batch again in full.
   - **The last item, indexes and log**: the log heading is `## [<date>] capture | <Epic ID> handed-off Epic check`, with one line naming every work item and comment ID read (`Read <Epic key>, <Story keys>; comments <every comment ID, used or not>`), so the next check knows them all as seen. Show the heading and each log line in code spans. `up-next` takes the last check date from it.

   Done when: the batch is shown, every Answer to a Question raised from a `Business question` directly followed by its Jira reply, ending with "Nothing is written yet." and the ways on as **3. Propose** says.

## Jira reply

An Answer to a Question raised from an engineer's `Business question` goes back to the engineers on the same work item. A `Business call made in build` gets no reply: the engineer made that Decision and holds it already. The reply goes in the same batch as the Answer: the Answer and its reply are one, so amending one out takes the other out too.

- **Body**, in Markdown, Veneer names throughout and every canonical term of a renamed word in a code span, exactly as the pack writes them:

  ```markdown
  Reply to the `Business question` of <date> on <work item key> (<shown name for Question> <Q ID>, <shown name for Epic> <Epic ID>)

  **<Answer ID>** <the Answer's statement> · <Decision | fact> · Owner: <role, and the note from People> · <date>

  <one line per Requirement it created or replaced: **<REQ ID>** <statement>, or "Requirements unchanged.">

  <for a Decision:> This is settled: build on it as written. If it looks wrong, post a `Business question` quoting <Answer ID>.
  ```

  People are named by role, as in the pack. It cites only Requirement, Question, Answer and Epic IDs: never a Source ID.
- **Item**: the work item key, and the body in full in a fenced block. `Outbound:` in `workspace.md` decides where it goes: under `post`, a comment posted on that work item; under `outbox`, the file `outbox/<work item key>-reply-<Answer ID>.md` holding the body exactly as it would be posted, and nothing goes to Jira.
- **After the yes**, write the records first. Then, under `post`, post each reply with the MCP's Jira comment tool. A reply whose post fails goes to `outbox/` instead, as under `outbox`, so every Answer still has its reply: say which went to Jira and which to `outbox/`. Under `outbox`, `mkdir -p outbox` and write each file. Then log and commit: the log names each posted comment's URL or outbox file.

Done when: every reply in the batch is posted or in `outbox/`, the log names where each went, and nothing went to Jira or `outbox/` before the yes.
