# Capture: Sign-off read-back

Part of Capture, read when [SKILL.md](SKILL.md) sends you here. A section named in bold (**1. Find the Project**, **2. Read the material into candidates**, **Answers**) is in SKILL.md; **1. Gather** to **4. Write** are this file's own steps.

A Sign-off is a Stakeholder's recorded shoulder-check of specific Decisions. It attaches to Decision IDs, never to a pack version. Material is a read-back when it brings back what a Stakeholder said about the Decisions on their Sign-off view:

- **Their page**: a Confluence page whose URL a `signoff | Publish` log entry names, or whose title ends `(<Epic ID>, view v<N>)`. Read it as [confluence.md](confluence.md) says; a later read of the same page is a re-read, with `Previous reading:`.
- **A shoulder check**: the Operator types what a Stakeholder said while reading their view or pack with them ("Tom read his view with me: …"). Its Source is a `typed note` owned by the Operator, and its own Capture, never an item in another operation's batch.

1. **Gather**, with what **1. Find the Project** reads: the view the page or the Operator names, else the Stakeholder's latest `signoff-view-v*-<person>.md` in the Epic's folder (for a shoulder check on a pack alone, that pack); the pack the view came from; the Epic's `signoffs.md`, if it exists; `epic.md`, for a `Tech face:` line; and, for each Decision on the view's checkboxes or its "You agreed already" line, its Answer line, to know whether it is active or withdrawn and what replaced it.

   Done when: you hold the view and its pack, the Stakeholder's earlier entries, and each of the view's Decisions with its status now.

2. **Sort** each Decision with a checkbox on the view into exactly one of:
   - **agreed**: ticked (`[x]`), or the Stakeholder says they agree;
   - **not agreed**: unticked, with the Stakeholder's words against it or a reason they do not agree;
   - **not yet looked at**: unticked, with nothing said. Unticked is never agreement, and it has no deadline: chase nothing and set no date.

   Then drop what an earlier entry of this Stakeholder already records the same way: a later read-back adds only the new ticks and new pushback. A Decision on the "You agreed already" line stays out.

   Done when: every checkbox Decision is sorted, and only the new ones are left.

3. **Candidates**, on top of those **2. Read the material into candidates** makes from the rest of the material:
   - **The entry**: one Sign-off entry, item 2 of the batch, in the shape of [templates/signoffs.md](templates/signoffs.md): `<CODE>-SO-<nnn>`, the Stakeholder's full name and People role, and the date of the ticks (the page's last-updated date, or the day of the shoulder check); `Pack:` the pack the view came from; `View:` the view file, or `none`; `Where:` the page URL, `in person` or `by email`; one line each for `Agreed:`, `Not agreed:` and `Not yet looked at:`, a line with no IDs left out; and `Source:` this read-back's Source. With nothing new left after **2. Sort**, there is no entry: say nothing new was ticked since `<last SO ID>`.
   - **Pushback**: each not-agreed Decision raises a new Question, the Stakeholder's point asked as a plain question, with `Affects: <Answer ID>` and `Raised from: <this Source>`, scored as **2. Read the material into candidates** says. When work already depends on the Decision (the Epic is handed off, with a `Tech face:` line in `epic.md`, or the records or the Operator say it is being built): `Building on a guess: yes`, `Needed by: <Epic ID>`. The entry's `Not agreed:` line points each Decision at its Question (`<Answer ID> → <Q ID>`). The Decision stays in force: its Answer line is not touched, and the item says so ("`HAL-ANS-004` stays in force until `HAL-Q-014` is answered").
   - **Their calls**: the Stakeholder's reply to a Question on their view (🔴 or 🟠) is an Answer, as **Answers** says. A business choice is a Decision owned by that Stakeholder when the Question's `Ask:` names them.
   - **A withdrawn Decision ticked**: record it against the ID on the view, in `Agreed:`, and say in the item that it was replaced by `<new ID>` on `<date>`, which this Stakeholder has not yet ticked. Agreement never moves to a replacement.

   Done when: there is one entry (or none, said so), one Question per not-agreed Decision, and one Answer item per call they replied to.

4. **Write** the entry by adding it at the end of `signoffs.md`, after a blank line. `signoffs.md` is only ever added to: an earlier entry is never edited, even when its Decision is later withdrawn or replaced. With no `signoffs.md` yet, the batch makes it from the template, with the entry as its first, and links it from the Project's `index.md` under the Epic.

   Done when: `git diff HEAD~1 -- <signoffs.md>` holds no removed line.
