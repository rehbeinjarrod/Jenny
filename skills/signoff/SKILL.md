---
name: signoff
description: Report where an Epic stands with its Stakeholders, write one Stakeholder's Sign-off view of an Epic's latest pack, or publish a view to Confluence. Use when the Operator asks "where does <Epic> stand?", who has agreed an Epic or its Decisions, or what is still to be signed off; for `/signoff`; when they say "sign-off view for <person>, <Epic>"; or "publish it" after a view.
---

# Sign-off

Two confirm-then-write operations, following the rules in the Tool-owned block of `AGENTS.md`, and one that writes nothing:

- **View** on "sign-off view for <person>, <Epic>", and on `/signoff` naming a person or an Epic. It writes a frozen `epics/<ID>-<slug>/signoff-view-v<N>-<person>.md` from the Epic's latest pack, addressed to one Stakeholder and shaped as their to-do list.
- **Publish** on "publish it", "publish the view" or `/signoff publish`. It posts a written view to Confluence, or under `Outbound: outbox` writes the exact page body to `outbox/` instead.
- **Standing** on "where does <Epic> stand?", "who has agreed <Epic>?" or `/signoff standing`. It reports, per Stakeholder, which of the latest pack's Decisions they agreed, dispute or have not yet looked at, and writes nothing.

A Stakeholder's ticks and pushback come back through `capture` (its **Sign-off read-back**), which adds each Sign-off to the Epic's `signoffs.md`.

Every reply uses Veneer names. Today is `date +%F`.

## View

The view is the Stakeholder's to-do list, read in this order: 🔴 what is being built on a guess, 🟠 their calls, ✅ the Decisions to check, ⚪ what we think does not matter, the flow, then what else is worth knowing. It renders [the template](templates/signoff-view.md) from the latest pack, with the records read only to know which Stakeholder each Question is with, who owns each Decision, and what this Stakeholder has already agreed.

1. **Gather.** Find the one Project and Epic as the Lookup rules say, asking when two could fit. Find the person in the People table of `project.md` by name or first name. They must have the role `Stakeholder`: someone else, or someone not in People, gets no view; say so, and that `setup` adds a Stakeholder to People. Then read:
   - the latest pack: the highest `pack-v<N>.md` in the Epic's folder. With none, stop: say the pack comes first ("write the pack for <shown name for Epic> <ID>");
   - `epic.md`, for whether the Epic is handed off (a `Tech face:` line);
   - each Question file the pack names in its section 5, for `Ask:`, `Score reason:`, `Needed by:` and `Status:`;
   - each Answer the pack names in its section 3, in its Question file, for its `Owner:` name and `Status:`;
   - `signoffs.md`, if it exists: the IDs on the `Agreed:` lines of this person's entries, and each entry's date;
   - the `signoff-view-v*-<person>.md` names in the Epic's folder.

   `<person>` is the first name in lower case (`margaret`), or the whole name in lower case with hyphens (`margaret-osei`) when another person in People shares that first name. The new view's N is one more than the highest N for that `<person>` in the Epic's folder, or 1.

   **Records moved on since the pack**: when a Question in its section 5 is now answered or withdrawn, or a Decision in its section 3 now withdrawn, say so in the proposal and suggest writing a new pack first. The view still renders the pack as written, if the Operator wants it.

   Done when: you hold the pack, this Stakeholder's agreed IDs, which Stakeholder each Question is with, who owns each Decision and their People role, and the view's file name.

2. **Sort.** Put each item from the pack in exactly one place:
   - **🔴** each section 5 item marked **Already being built on a guess**, whoever it is with.
   - **🟠 table** each other section 5 item whose Question's `Ask:` names this Stakeholder. Why it matters is its `Score reason:`, in business words. Needed by is the `Needed by:` date written `D Mon`, "before this <shown name for Epic> is built" when `Needed by:` names an ID, or "—".
   - **🟠 others** each other section 5 item, in one line per person: those whose `Ask:` names someone else ("<first name> is handling …"), then those with no `Ask:` ("Not yet put to anyone: …"). The Parked line stays out.
   - **✅ checkbox** each section 3 Decision this Stakeholder has not agreed: no `Agreed:` line of theirs names its ID. Owner is "your call" when it is this Stakeholder, else the owner's name; a Decision whose owner has the People role `engineer` adds "decided during build".
   - **✅ agreed** each section 3 Decision this Stakeholder has agreed, in the one "You agreed already" line with its Sign-off date, and no checkbox.
   - **⚪** each N/A row of the pack's Appendix A: what the category covers, in plain words ("Who else hears of a booking"), and the Operator's reason.
   - **Also worth knowing** each Appendix B line that is not about a Question or Decision placed above, each `Left out` line from section 8, and each section 7 `Depends on` line.

   Done when: every section 5 item (not parked), section 3 Decision, Appendix A N/A row and remaining Appendix B line sits in exactly one place.

3. **Draft** the view in your own working, writing no file, by the template and these rules:
   - **Checkboxes are for Decisions only.** A `- [ ]` line holds exactly one Decision this Stakeholder has not agreed. Facts, Questions, options and agreed Decisions are plain lines: a Question's options go on one "Reply with one:" line.
   - **Addressed by name.** The header names them in full; the opening line speaks to them by first name, and counts the 🔴 items, the 🟠 table rows and the ✅ checkboxes. Minutes: 2 for each of those items, at least 5. Other people are named by name too.
   - **Worked examples**, made up and marked as such, each in the one-line shape the template gives, sitting under the item it shows and citing that item's ID: one under each 🔴 item; one under a 🟠 row or a ✅ Decision wherever a case with numbers shows what the answer changes. Take every number from the pack's rules (section 4 and the Decisions), and work each sum through: hours, rate, fee, deposit. For a Question, give the outcome under each answer and call none of them settled.
   - **Flow diagrams** in Mermaid `flowchart LR`, drawn from the pack's section 4 rules and the Decisions. Each diagram has at most 7 nodes, not counting its start and stop, which are stadium-shaped (`start([…])`, `stop([…])`); a flow that needs more is cut at a natural seam into several diagrams, each under its own `###` heading. Each node is a step in plain words, citing with 🔴, 🟠 or ✅ the IDs that bear on it; `classDef` colours the guessed and open nodes.
   - **Plain words, shown names.** The view is read outside the Workspace: every Delivery term in it is its Veneer shown name, the template's `{Term}` slots included. IDs, file names and the emoji stay as they are. Write each Question and Decision as a plain sentence a Stakeholder would say, with its ID beside it in a code span.
   - **Cite only Requirement, Question and Decision IDs**, so no Source ID leaves the Workspace.

   Done when: the draft follows the template's sections in order, the checkboxes are exactly the ✅ checkbox Decisions, every 🔴 item has an example, every example's numbers come from the pack's rules, and no diagram has more than 7 nodes besides start and stop.

4. **Propose** under the heading "<shown name for Sign-off view> for <full name>: <shown name for Epic> <ID> <title>", from <shown name for Epic pack> v<N>, as a numbered batch:
   1. `epics/<ID>-<slug>/signoff-view-v<N>-<person>.md`: one line per section saying what it holds, with the IDs (and how many diagrams).
   2. Log entry `## [<date>] signoff | <Epic ID> <title> signoff-view-v<N>-<person>`, one line for the file written.
   3. One commit.

   Then any records that moved on since the pack (step 1), and "Nothing is written yet."

   Done when: the batch names the view file and every section's IDs.

5. **Amend, confirm, write, log, commit** as `AGENTS.md` says, drafting again and showing the batch in full after each amend. On the yes, write the view exactly as last drafted.

   Done when: one commit whose message is the log heading, adding `signoff-view-v<N>-<person>.md` and changing only the log (`git diff --name-status HEAD~1` prints one `A` line for the view and one `M` line for the log, or one `A` for a new month's log), and `grep -cE '^\s*[-*] \[[ xX]\]'` on the view equals the ✅ checkbox count.

6. **Hand on.** Say the view is written, that "publish it" puts it on Confluence (or in `outbox/`, as `workspace.md` says), that each tick the Stakeholder makes on the published page is their Sign-off of that Decision, and that "capture <page URL>" brings their ticks and pushback back. Done when: the Operator has been told.

## Publish

Puts one written view where the Stakeholder reads it: a Confluence page, with each checkbox a task item they can tick and each diagram a native whiteboard. Nothing is posted and nothing goes in `outbox/` before the Operator's yes.

1. **Gather.**
   - The view: the one written in this chat, else the one the Operator names, else the latest `signoff-view-v*-<person>.md` for the person named. When it is unclear which, ask. The view is never changed.
   - `Outbound:` in `workspace.md`: `post` or `outbox`.
   - Under `post`: where the page goes. The `Sign-off pages: <URL>` line under `## External links` in `project.md` names the Confluence page the views sit under. With no such line, ask the Operator for that page's URL; the batch then adds the line to `project.md` (replacing `None yet.`).
   - Whether this view was published before: a log entry `signoff | Publish …` naming it. If so, say where and ask before making a second page.

   Done when: you hold the view, the outbound setting, and under `post` the parent page.

2. **Build the page body**, writing no file: the view as Confluence HTML, a body fragment with no `<html>`, `<head>` or `<body>`, in the markup the MCP's page format guide gives (when the MCP is connected, read it with `executeRead`: `name: getContentFormatGuide`, `inputs: {toolName: createConfluencePage}`):
   - headings as `<h1>`–`<h3>`; the header quote as `<div data-type="panel-info"><p>…</p></div>`; paragraphs, lists and tables as plain HTML; code spans as `<code>`.
   - each `- [ ]` Decision as a task item: `<ul data-type="task-list"><li data-type="task-item"><input type="checkbox"> …</li></ul>`, its example as a plain list under the task list. Task items are for those Decisions alone.
   - each Mermaid diagram as its `###` heading, then the whiteboard embed `<a href="<whiteboard URL>" data-card-appearance="embed"></a>`, then its source in an expand: `<details><summary>Diagram source (Mermaid)</summary><pre><code class="language-mermaid">…</code></pre></details>`. Under `outbox`, `<whiteboard URL>` stays as `{whiteboard-<n>}`, numbered in page order.
   - the page title: "<Epic title>: <full name>'s calls (<Epic ID>, view v<N>)".

   Done when: the body has one task item per checkbox in the view, and one embed and one expand per diagram.

3. **Propose** under the heading "Publish <shown name for Sign-off view>: <full name>, <shown name for Epic> <ID>", as a numbered batch:
   - Under `post`: each whiteboard to create under the parent page, drawn from its diagram; the page to create under the parent page, with its title; the `Sign-off pages:` line for `project.md`, when it is new.
   - Under `outbox`: `outbox/<Epic ID>-signoff-view-v<N>-<person>.html`, holding the page body exactly as it would be posted; say nothing goes to Confluence, because this Workspace's outbound is the outbox.
   - Log entry `## [<date>] signoff | Publish <Epic ID> signoff-view-v<N>-<person>`, with one line for each thing made: the page's URL and each whiteboard's under `post`, the outbox file under `outbox`.
   - One commit.

   Then "Nothing is written yet."

   Done when: the batch names every page, whiteboard or file it makes.

4. **Amend, confirm**, as `AGENTS.md` says. Then, only after the yes:
   - Under `post`: read the whiteboard format guide (`executeRead`, `name: getContentFormatGuide`, `inputs: {toolName: createConfluenceWhiteboard}`) and follow its flowchart reference. Create each whiteboard with `createConfluenceContent` (`contentType: whiteboard`, `body.format: svg`) under the parent page, one per diagram, its shapes, connectors and labels matching the Mermaid, and its guessed and open nodes filled in the `classDef` colours so 🔴 and 🟠 still show. Then create the page (`contentType: page`, `body.format: html`) with each `<whiteboard URL>` set to the URL its whiteboard returned. A failed create stops the operation: say what was made and what was not, and log only what exists.
   - Under `outbox`: `mkdir -p outbox` and write the body to the file.

   Then log and commit as `AGENTS.md` says.

   Done when: one commit whose message is the log heading, the view unchanged in it, and under `outbox` the file added (`git diff --name-only HEAD~1 -- outbox` prints it); under `post` the log names the page URL.

5. **Hand on.** Under `post`, give the page link and say a tick on a task item, with the Stakeholder's name and date, is their Sign-off of that Decision, and that "capture <page link>" brings the ticks back once they have read it. Under `outbox`, name the file and say it is the page body to paste or post by hand. Done when: the Operator has been told.

## Standing

Where an Epic's Sign-off stands, worked out from `signoffs.md` against the Decisions in the latest pack as they are now. There is no yes/no "signed off" state: each Stakeholder stands Decision by Decision. Read-only: it writes nothing, so it proposes no batch.

1. **Gather.** Find the one Project and Epic as the Lookup rules say, asking when two could fit. Read:
   - the People table in `project.md`: every person with the role `Stakeholder`;
   - the latest pack (the highest `pack-v<N>.md`) and its section 3 Decisions. With no pack, say the pack comes first and stop;
   - each of those Decisions' Answer lines now, following `Replaced by:` from a withdrawn one to the active one at the end of the chain;
   - `signoffs.md`, if it exists: every entry, oldest first;
   - each Question named on a `Not agreed:` line, for its `Status:`.

   Done when: you hold each Stakeholder, each Decision in force now with any ID it replaced, and every entry.

2. **Work out** each Stakeholder's standing on each Decision in force. Agreement attaches to the Answer ID: a Decision withdrawn since the pack counts as its replacement, which starts unagreed by everyone, whoever agreed the old ID. A Decision withdrawn with no replacement drops out, and is named after the Stakeholders' blocks. For each Stakeholder and Decision, read their entries naming that ID on `Agreed:` or `Not agreed:` lines, and the latest of those decides (a `Not yet looked at:` line never undoes an earlier agreement):
   - an `Agreed:` line: **Agreed**, with that entry's date and ID. It carries forward for as long as that Answer ID is active;
   - a `Not agreed:` line, with the Question there `open`, `chasing` or `parked`: **Disputed**, with the Question's ID. Once that Question is answered or withdrawn, the dispute is over and the Decision is **Not yet looked at** again;
   - neither: **Not yet looked at**. Unticked is never agreement.

   Done when: every Stakeholder has every Decision in force in exactly one of the three.

3. **Reply** in this shape, in shown names, the three line labels exactly as written:

   ```markdown
   **<shown name for Epic> <ID> <title>**: <shown name for Epic pack> v<N>, <d> Decisions. <First name> agreed <a> of <d>; <first name> agreed <a> of <d>.

   **<Full name>** (<People notes, or Stakeholder>)
   - Agreed: <a few words> `<ANS ID>` (<D Mon>, `<SO ID>`); …, or none
   - Disputed: <a few words> `<ANS ID>` → `<Q ID>` (<its status>); …, or none
   - Not yet looked at: <a few words> `<ANS ID>`; …, or none

   <one block per Stakeholder, in People order>
   ```

   In the Not yet looked at line, a replacement whose old ID the Stakeholder had agreed reads "`<new ID>` (replaced `<old ID>`, which <first name> agreed on <D Mon>; that agreement does not carry)". After the blocks, when a pack Decision has been withdrawn since the pack, say v<N> still shows `<old ID>` and suggest writing a new pack ("write the pack for <shown name for Epic> <ID>"). Then offer the next step: a <shown name for Sign-off view> for each Stakeholder with something not yet looked at.

   Never call the Epic, or anyone, "signed off", and never call an unticked Decision late or overdue.

   Done when: the reply has one block per Stakeholder with all three lines, cites every Decision and Sign-off ID it rests on, and nothing is written (`git status --porcelain` is empty).
