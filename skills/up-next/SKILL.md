---
name: up-next
description: What to chase next in one Project, and shaping a Question's ask. Use for `/up-next`, when the Operator asks what to chase, shape or do next, says "shape <n>", or says an ask has gone out.
---

# Up next

Three operations: **The list**, which writes nothing; **Shape** and **Asked**, each one confirm-then-write operation following the rules in the Tool-owned block of `AGENTS.md`. Today is `date +%F`; every date is shown as `YYYY-MM-DD`.

## The list

1. **Gather.** Find the one Project as the Lookup rules say, and work in its folder only. Read `questions/index.md`, then every `open` and `chasing` Question file whole: rank from the files' own header lines. Read every `epics/*/epic.md`: one with a `Tech face:` line under `## External items` is handed off. Its last check is the date of the latest log heading `## [<date>] capture | <Epic ID> handed-off Epic check` in `log/*.md`; with none, it has not been checked since the handoff date on the `Tech face:` line.

   Done when: you hold each `chasing` Question's `Ask:`, `Asked:` and `Chase by:`, each `open` Question's `Score:`, `Score reason:`, `Building on a guess:` and `Needed by:`, and each handed-off Epic's last check.

2. **Rank.**
   - **Chase now**: every `chasing` Question. Overdue ones (`Chase by:` before today) first, most days overdue first; then the rest by soonest `Chase by:`.
   - **Shape next**: `open` Questions only. `Building on a guess: yes` first, then higher Score, then soonest `Needed by:`; a `Needed by:` that is an Epic or Milestone ID sorts before every date, since work is already waiting on it. Keep the top 5.

   `parked`, `answered` and `withdrawn` Questions stay out of both lists.

   Done when: both lists are in order.

3. **Reply** in this shape, the two labels exactly as written:

   ```markdown
   **Chase now**
   - `<ID>` <gist in a few words> · asked <Ask> on <Asked> · <N> days overdue (chase by <Chase by>)
   - `<ID>` <gist> · <Ask> not asked yet · due <Chase by>, in <N> days
   - `<Epic ID>` <title>, handed off as <tech face link text>: last checked <date>. Worth checking for anything the build has raised.

   **Shape next**
   1. `<ID>` <gist> · building on a guess · Score <n>: <score reason in a few words> · needed by <Needed by>
   2. `<ID>` <gist> · Score <n>: <score reason in a few words> · needed by <Needed by>

   Shall I shape `<top ID>`? Or say "shape <n>" for another.
   ```

   Each Question is one line holding its ID, so its facts stay together. Write "1 day" for one day. An empty list says so in one line: "Nothing to chase." or "Nothing left to shape." The Shape next numbers are the ones "shape <n>" refers to. When the list is empty, end without the offer.

   The list is read-only. When a record looks off (a stored Score that is not Impact × Uncertainty, a `chasing` Question with no `Chase by:`), add a one-line note after the offer and leave the file as it is.

   Done when: the reply has both lists and, with a Shape next list, ends with the offer. Nothing is written.

## Shape

Runs on "shape <n>" (item n of the last Shape next list), "shape `<ID>`", or a yes to the offer. One Question at a time.

1. **Gather.** Read the Question file whole, `project.md` for People, and the records in its `Affects:`.
   - **Ask**: the one person in People best placed to answer, from their role and note: usually the Stakeholder who owns that area, an engineer for what the system can do. When two fit equally, name both and ask the Operator. When the right person is not in People, say so and ask the Operator to add them through `setup`; the shape waits until they are in.
   - **Technique**, one of: `message` (a fact or a yes/no one person can give), `conversation` (a choice that needs talking through), `workshop` (several people must agree), `document review` (the answer is in a document someone must read), `demo or prototype` (behaviour easier shown than described), `delivery-team Spike` (a technical unknown).
   - **Chase by**: when to chase if no answer has come, a few working days from today for a message, longer for the others, and before a dated `Needed by:`.

   Done when: you hold an Ask from People, a Technique and a Chase by, each with a one-line reason.

2. **Propose** under the heading "Shape <shown name for Question> `<ID>`":
   1. `questions/<file>`: `Status: chasing`, `Ask: <name>`, `Technique: <one of the six above>` and `Chase by: <YYYY-MM-DD>`, each followed, in chat only, by its reason: the file gets the value only. Every other line stays as it is.
   2. `questions/index.md`: that row's Status becomes `chasing`.
   3. Log entry `## [<date>] up-next | Shape <ID> <short title>`, one line per file written: the Question file with its four new values, and `questions/index.md`.
   4. One commit.

   Then **Draft ask**: the wording of the ask, addressed to the Ask person, ready for the Operator to paste or say. Plain words, citing only the Question's ID so the Answer can be matched. Say the draft is not stored. Then "Nothing is written yet."

   Done when: the batch and draft are shown, ending with "Nothing is written yet."

3. **Amend, confirm, write, log, commit** as `AGENTS.md` says. In the Question file, change the `Status:` line and set the three plan lines after `Affects:`, replacing any that exist, each as its step 2 template with the value only. Every other line of the file stays byte for byte; the draft and the reasons live only in chat.

   Done when: one commit whose message is the log heading, and `git diff HEAD~1 -- <file>` shows only `Status:`, `Ask:`, `Technique:` and `Chase by:` lines, each plan line its step 2 template with the value only.

4. **Hand on.** Say that when the ask has gone out, telling Jenny sets the date it was asked. Done when: the Operator has been told.

## Asked

Runs when the Operator says the ask for a Question has gone out. A Question with no `Ask:` is shaped first.

1. **Propose** under the heading "Asked <shown name for Question> `<ID>`":
   1. `questions/<file>`: `Asked: <date>` after `Chase by:`, today unless the Operator gives a date.
   2. Log entry `## [<date>] up-next | Asked <ID> <short title>`, one line for the Question file and its date.
   3. One commit.

   Then "Nothing is written yet."

   Done when: the batch is shown, ending with "Nothing is written yet."

2. **Amend, confirm, write, log, commit** as `AGENTS.md` says.

   Done when: one commit whose message is the log heading, and `git diff HEAD~1 -- <file>` shows only the `Asked:` line.
