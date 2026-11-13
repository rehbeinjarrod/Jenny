---
name: capture
description: Turn incoming material into Requirements, Questions and Answers. Use for `/capture`, when the Operator types, pastes or drops in material (a note, an email, meeting notes) or gives a Confluence page URL and says to capture it, says "re-read <URL>", says "check <Jira key or Epic>" for a handed-off Epic, gives an answer to an open Question, or brings back a Stakeholder's Sign-off: their ticked Sign-off page, or what they agreed when they read their view with the Operator.
---

# Capture

One Capture is one operation under **Every write: confirm, then write** in the Tool-owned block of `AGENTS.md`. The record shapes are in [templates/](templates/).

A Capture writes Sources, Requirements (on an existing Feature or in `requirements/unplaced.md`), Questions, Answers, withdrawals and their replacements, re-scores, new People in `project.md`, Sign-off entries in an Epic's `signoffs.md`, the folder indexes and the log, and sends the Jira reply to an in-build Question it answers. Features and Decision coverage belong to other skills: a Requirement with no fitting Feature goes to `unplaced.md`.

## 1. Find the Project

For a Confluence page URL, first read the page as **Confluence pages** says; a re-read belongs to the Project whose `sources/` holds the earlier reading, and a Sign-off page to the Project whose log names its URL. Material that brings back a Stakeholder's Sign-off is read as **Sign-off read-back** says. "Check <Jira key or Epic>" is read as **Handed-off Epic check** says.

Above the batch, say in one plain sentence which Project you think the material belongs to and why, starting with its own name and code ("Deck linter `CDL`, because it is about the deck size rule"). When you cannot tell which Project it belongs to, ask and propose nothing yet.

Material that plainly bears on several Projects becomes one Source per Project, each holding only the parts that Project uses, with an `Also in:` line naming the others. Each Project's records go in that Project's own batch items, and each Project's log gets the entry.

Then read each Project's `index.md`, `project.md`, every active Requirement (each Feature file and `requirements/unplaced.md`) and `questions/index.md` with the files of its `open` and `chasing` Questions. Next IDs: one above the highest in use for each kind, found with `grep -rhoE '<CODE>-(SRC|REQ|Q|ANS|SO)-[0-9]{3}' projects/<slug>/ | sort -u`.

Done when: the Project is named with a reason, and you hold its active Requirements, open Questions, People and next free IDs.

## 2. Read the material into candidates

Go through the material in order and turn each point into candidates:

- **Requirement**: one testable need or constraint, restated as one plain sentence that carries its own terms: an option with its price or condition, a rule with the details that pin it down (which door, which month), a limit with its number. Two needs become two Requirements only when each still stands as a need with the other gone. Place each on the Feature it belongs to, or in `unplaced.md`.
- **Question**: something the material says is not known or not settled. Propose `Impact` and `Uncertainty` (1 to 3 each), `Score` (their product, as one number), a one-line `Score reason`, and `Building on a guess`. A Score of 1 or 2 is proposed as `parked`; any other as `open`.
- **Answer**: a point that answers an open or chasing Question. See **Answers** below.
- **Person**: someone the records need (an owner, someone to ask) who is not in `project.md`. Ask for their role (`Operator`, `Stakeholder` or `engineer`) rather than guess.

Label each Requirement candidate against the Project's active Requirements:

- **new**: nothing active says it. Written as a new Requirement.
- **duplicate** of `<ID>`: an active Requirement already says it. It gets only a log line naming the Requirement and where it was said again.
- **refines** `<ID>`: the same need, stated more precisely or narrowed. Proposed as "withdraw `<ID>` and replace it with `<new ID>`: <new statement>", the one replacement stating the whole narrowed need; the replacement goes where `<ID>` is.
- **conflicts** with `<ID>`: the material says something an active Requirement contradicts. The Operator settles it, through a new Question that cites both Sources, with `Affects: <ID>`; `<ID>` stays active meanwhile. Say so in the item, and that the Operator can override it ("the new one's right"). An override records a Decision owned by the Operator as the Answer to that Question, then withdraws and replaces `<ID>`.

For a re-read, label the parts against the earlier reading first, as **Confluence pages** says: its changed and new parts become candidates here, and its unchanged parts count as listed.

Done when: every point in the material is a candidate or is listed as not used, and every Requirement candidate has a label.

## 3. Propose

Settle every label, score and ID before you show the batch, so it states only the results. When the material quotes a third-party passage, run the **copy check** last, over the whole batch. The retellings are every line built from the passage: the Source's summary, each Answer's statement and its `Grounds:` line, and the statement of each Requirement such an Answer creates or puts in as a replacement. Copied text is a run of four or more of the passage's words in a row. Check by command, with the passage and the retellings as the batch will show them, each retelling on one line; it prints each four-word run a retelling shares with the passage. Say each retelling holding a printed run again differently, and run the check again until it prints nothing.

```sh
awk 'function g(s,a,  n,w,i){s=tolower(s);gsub(/[^a-z0-9]+/," ",s);n=split(s,w," ");for(i=1;i+3<=n;i++)a[w[i]" "w[i+1]" "w[i+2]" "w[i+3]]=1} /^----[ \r]*$/{p=1;next} !p{q=q" "$0;next} {r[++m]=$0} END{if(!p){print "no ---- line";exit 1};g(q,A);for(j=1;j<=m;j++){split("",B);g(r[j],B);for(k in B)if(k in A)print k}}' <<'EOF'
<the passage, as given>
----
<every retelling, one per line>
EOF
```

Show the batch under the heading `Capture: <title of the Source>` (in shown names), with that sentence above it. Order the items so the Operator can amend by number:

- **Item 1, the Source**, as [templates/source.md](templates/source.md) shapes it, with its ID and the exact text it will keep:
  - Own organisation's material (the Operator's notes, colleagues' emails, meeting notes, internal pages): the parts used, word for word. Parts not used stay out of the Source and are listed in one line after the items.
  - Third-party material (articles, standards, rulebooks, codes of practice), including a passage quoted inside own material: cut the passage out and mark the cut `[…]`, keeping every own word around it exactly as given, then add its location (title, publisher, year, section, URL if any) and a summary in your own words. Records and the batch carry the passage only as that location and own words. Own words means the point retold plainly, as you would say it to the Operator: short, in your sentence shape and your vocabulary, keeping only names, numbers and section numbers from the original.
- **For a Sign-off read-back, item 2 is the Sign-off entry**, as **Sign-off read-back** says.
- **For a Handed-off Epic check**, the items are as **Handed-off Epic check** says, and each Jira reply sits directly after the Answer it carries.
- **Then one item per candidate**, in the order the material raises them: its label, the record it will write (ID, statement, where it goes) and, for a Question, the proposed scores and reason.
- **The last item, indexes and log**: the folder indexes changed (`sources/index.md`, `questions/index.md` re-ranked, `features/index.md` for a placed Requirement) and the log entry's heading.

When everything in the material is a duplicate, the batch is only the log note and no Source is written.

After the items and any "not used" line, end every batch, and every showing again after an amend, with "Nothing is written yet." on its own line, word for word, then the ways on: accept all, edit by number, or reject.

Done when: for material quoting a third-party passage, the copy check prints nothing for the batch's retellings; and the batch is shown in that order, ending with "Nothing is written yet." and the ways on.

## 4. Amend, confirm, write, log, commit

As `AGENTS.md` says, renumbering the batch after each amend. Writing:

- **Source**: `sources/<ID>-<slug>.md`, from the template, leaving out lines and parts that do not apply.
- **Requirement line**: `- **<ID>** <statement> · Source: <SRC or ANS ID> · Status: active`, added at the end of its Feature's `## Requirements` list or of `unplaced.md` (replacing "None."). A withdrawal strikes the old line in place, as the Records rule in `AGENTS.md` says: `- ~~<the line as it was, with Status: withdrawn>~~ · Withdrawn <date> · Reason: <why> · Replaced by: <ID>`, leaving out ` · Replaced by: <ID>` when nothing replaces it.
- **Question**: `questions/<ID>-<slug>.md` from [templates/question.md](templates/question.md), and a row in `questions/index.md` in the rank order that file states.
- **Answer** and the Question's changed header lines: in the Question's file, as **Answers** says.
- **Person**: a row `| <name> | <role> | <what they look after, or blank> |` in the People table of `project.md`.
- **Sign-off entry**: added at the end of the Epic's `signoffs.md`, as **Sign-off read-back** says.
- **Indexes**: a row in `sources/index.md`; the Requirement IDs in `features/index.md` when a placed Requirement is added or withdrawn. A folder index that does not exist yet is made from its template in [templates/](templates/) and linked from the Project's `index.md`, with that file's "No … yet" line updated.
- **Jira reply**: posted or written to `outbox/` as **Jira reply** says.
- **Log**: `## [<date>] capture | <Source ID> <Source title>` (`capture | <Epic ID> handed-off Epic check` for a check) (or `capture | duplicate of <ID>, …` when nothing else is written), then one line per file written, the IDs created, withdrawn or answered, one line per Sign-off entry (`Sign-off <SO ID> (<name> agreed <IDs>; not agreed <ID> → <Q ID>) in epics/<ID>-<slug>/signoffs.md`), and one line per duplicate: `Duplicate: <ID> said again in <Source ID>; nothing written`, naming the material by kind, owner and date when no Source is written. Material for several Projects writes the same heading in each Project's log, all in the one commit.

For material quoting a third-party passage, run the copy check again on what is written, after staging and before the commit and any Jira post. Its retellings are every added line of the staged diff except the Source's kept `>` lines:

```sh
{ cat <<'EOF'
<the passage, as given>
----
EOF
git diff --cached --no-color -U0 | sed -n 's/^+\([^+>].*\)/\1/p'; } | awk '<the copy check program from 3. Propose>'
```

A printed run that is only a name or a title stays as it is. Say each other line holding a printed run again differently, in its file, restage, and run it again until it prints only names and titles.

The reply after the commit has one line per record written, each led by the record's shown name and ID ("<shown name for Question> `HAL-Q-014` is answered by `HAL-ANS-004`: …"), with the commit message in a code span.

Done when: for material quoting a third-party passage, the copy check prints only names and titles for the staged lines; and the operation's one commit is made, as `AGENTS.md` says.

## Confluence pages

The material is the page as the Atlassian MCP returns it: read it with the MCP's Confluence page tool, the page ID taken from the URL and the body as Markdown. When your instructions name a file standing in for the MCP for that URL, read that file instead: it is what the MCP returned. When the read fails, say so in one line and propose nothing; the Operator can paste the page instead.

A page is own-organisation material unless it quotes a third party, and its Owner is the page's last author. Its Source is `Kind: Confluence page` and keeps the parts used word for word, with `URL:`, `Page version:` and `Read:` (the date of this read) in place of `Captured:`, and `Date:` the page's last-updated date.

**Re-read.** A URL already in a Source's `URL:` line is a re-read, whether or not the Operator says "re-read": `grep -rlxF 'URL: <url>' projects/*/sources/`. In each Project that holds the URL, the earlier reading is the latest of its Sources, the one no other names in `Previous reading:`; a page in several Projects is re-read in each, as **1** says for material bearing on several Projects. When its `Page version:` matches the page's, say the page is unchanged since that reading and propose nothing. Otherwise the batch proposes only what changed:

- **Item 1** is a new Source with `Previous reading: <earlier Source ID>`, holding every part this reading uses, unchanged parts included, so each reading stands alone. The earlier Source stays as it is.
- Each part of the earlier reading is **unchanged**, **changed** or **gone**. A Requirement is built on a part when it cites this page's earlier reading or an older one, and its statement comes from that part. One built on a changed part and a gone part is treated as changed.
  - **unchanged**: nothing proposed; name these parts in one line after the items.
  - **changed**: each Requirement built on the old text is withdrawn and replaced ("withdraw `<ID>` and replace it with `<new ID>`: …"), the replacement citing the new Source. The page has changed its own text, so its newer wording stands; a change that bears on a Requirement from another Source is labelled against it as in **2**.
  - **gone**: each Requirement built only on it is a "withdraw? `<ID>`" item: say what has gone, and that `<ID>` stays active unless the Operator says to withdraw it. Accept all leaves it active. When the Operator says to withdraw it, the item becomes a withdrawal with no replacement, its `Reason:` naming the new Source.
- A part new to the page becomes candidates as in **2**.

Done when: the page is read (or the failed read is reported), and on a re-read every part of the earlier reading is unchanged, changed or gone, with an item for each Requirement built on a changed or gone part.

## Handed-off Epic check

Checking a handed-off Epic is a Capture of its **tech face**: the engineers' Jira Epic named on the `Tech face:` line in `epic.md`, its child work items (Stories), and all their comments. PRs and repos are never read. Engineers post two fixed shapes there, as the pack's "For the agent" block tells them: a `Business question` and a `Business call made in build`. Say each shape's name in a code span, as here, every time, and call an engineer's ask by its shape's name: their `Business question`.

1. **Gather.** Find the Epic: for a Jira key, `grep -l 'Tech face: \[<key>\]' projects/*/epics/*/epic.md`; for an Epic named in words, as the Lookup rules say. An Epic with no `Tech face:` line is not handed off: say so and propose nothing. Read what **1. Find the Project** reads, plus `epic.md` and the handed-off pack it names. The **last check** is the latest log entry headed `capture | <Epic ID> handed-off Epic check` in `log/*.md`; with none, the `Handed off:` date.

   Read the tech face through the Atlassian MCP's Jira tools: the Epic, every work item whose parent it is, and each one's comments, with their IDs, authors and created and updated dates. When your instructions name a file standing in for the MCP for the tech face's URL, read that file instead: it is what the MCP returned. When the read fails, say so in one line and propose nothing.

   Done when: you hold the Epic's records, the last check, and every work item and comment on the tech face.

2. **Only what changed.** A comment is **seen** when its ID is named in an earlier check's log entry for this Epic, or it was created before the date of an earlier check whose entry names no comment IDs. Every other comment is **new**. A seen comment whose own updated date is on or after the last check is **changed**: read it again whole, and only what the records do not already hold is material. Epic and Story descriptions are context for reading the comments; engineers post both shapes as comments. Say in one line how many comments were seen already, without restating them.

   Done when: every comment is seen, new or changed.

3. **Candidates**, from the new and changed comments alone, in work-item order, then comment order:
   - **A `Business question`** about something no record settles: a new Question, what the engineer asked, put plainly, with `Affects:` the Requirement and Answer IDs it touches, scored as **2** says. `building around it` means `Building on a guess: yes` and `Needed by: <Epic ID>`; `blocked` means `Needed by: <Epic ID>`.
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

### Jira reply

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

## Sign-off read-back

A Sign-off is a Stakeholder's recorded shoulder-check of specific Decisions. It attaches to Decision IDs, never to a pack version. Material is a read-back when it brings back what a Stakeholder said about the Decisions on their Sign-off view:

- **Their page**: a Confluence page whose URL a `signoff | Publish` log entry names, or whose title ends `(<Epic ID>, view v<N>)`. Read it as **Confluence pages** says; a later read of the same page is a re-read, with `Previous reading:`.
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
   - **The entry**: one Sign-off entry, item 2 of the batch, in the shape of [templates/signoffs.md](templates/signoffs.md): `<CODE>-SO-<nnn>`, the Stakeholder's full name and People role, and the date of the ticks (the page's last-updated date, or the day of the shoulder check); `Pack:` the pack the view came from; `View:` the view file, or `none`; `Where:` the page URL, `in person` or `by email`; one line each for `Agreed:`, `Not agreed:` and `Not yet looked at:`, a line with no IDs left out; and `Source:` this read-back's Source. With nothing new left after **2**, there is no entry: say nothing new was ticked since `<last SO ID>`.
   - **Pushback**: each not-agreed Decision raises a new Question, the Stakeholder's point asked as a plain question, with `Affects: <Answer ID>` and `Raised from: <this Source>`, scored as **2. Read the material into candidates** says. When work already depends on the Decision (the Epic is handed off, with a `Tech face:` line in `epic.md`, or the records or the Operator say it is being built): `Building on a guess: yes`, `Needed by: <Epic ID>`. The entry's `Not agreed:` line points each Decision at its Question (`<Answer ID> → <Q ID>`). The Decision stays in force: its Answer line is not touched, and the item says so ("`HAL-ANS-004` stays in force until `HAL-Q-014` is answered").
   - **Their calls**: the Stakeholder's reply to a Question on their view (🔴 or 🟠) is an Answer, as **Answers** says. A business choice is a Decision owned by that Stakeholder when the Question's `Ask:` names them.
   - **A withdrawn Decision ticked**: record it against the ID on the view, in `Agreed:`, and say in the item that it was replaced by `<new ID>` on `<date>`, which this Stakeholder has not yet ticked. Agreement never moves to a replacement.

   Done when: there is one entry (or none, said so), one Question per not-agreed Decision, and one Answer item per call they replied to.

4. **Write** the entry by adding it at the end of `signoffs.md`, after a blank line. `signoffs.md` is only ever added to: an earlier entry is never edited, even when its Decision is later withdrawn or replaced. With no `signoffs.md` yet, the batch makes it from the template, with the entry as its first, and links it from the Project's `index.md` under the Epic.

   Done when: `git diff HEAD~1 -- <signoffs.md>` holds no removed line.

## Answers

Every capture reads the open and chasing Questions and proposes an Answer item for each point that answers one ("item 4 looks like it answers `CDL-Q-014`").

- **Kind**: `fact` (how things are) or `decision` (a business choice someone made). A Decision names an `Owner:` from the Project's People. When the material does not make the owner plain, ask in one line after the batch, led by the item number ("Item 3: who owns this Decision?"), and show the owner in the item as "asked below"; when the owner is not in People, propose adding them first. A Decision is written only once it has an owner from People.
- **Line**, under `## Answers` in the Question's file (replacing "None yet."): `- **<ANS ID>** <the answer in one plain sentence> · Kind: <fact | decision> · Owner: <name> · Date: <YYYY-MM-DD> · Source: <SRC ID> · Status: active`, then, for a Decision resting on a third-party Source, an indented `Grounds:` line as **Grounds** says, then an indented line naming the Requirements it created, withdrew or left unchanged. A fact may leave out `Owner:`.
- **Grounds**: `Grounds: <title>, section <n>: <the one point the Decision rests on>`. Write it from the Source's own-words summary, keeping only the point this Decision needs, in one short clause; the passage's other conditions and details stay in the Source's summary.
- **Effects**, each its own item in the batch:
  - For every active Requirement in the Question's `Affects:`, either "unchanged" or "withdraw and replace with `<new ID>`: …".
  - A new rule the Answer sets becomes a new Requirement with `Source: <ANS ID>`.
  - The Question's `Status:` becomes `answered`, and its row in `questions/index.md` moves down to the answered rows. Its title and wording stay as written; a `Clarified <date>:` line may be added.
  - A partial Answer still closes the Question, and a new Question is raised for the part left open, with `Affects:` copied.
  - Every other Question whose `Affects:` names a record this batch changes gets a proposed re-score (new Impact, Uncertainty, Score and reason) or "score unchanged".
  - An Answer to a Question raised from an engineer's `Business question` (its `Raised from:` Source is `Kind: Jira item`) carries a Jira reply, as **Jira reply** says.

Done when: each Answer item has its Kind, an owner from People for a Decision, and one effect item per Requirement in `Affects:`.

### Embedded Capture

Another skill's batch may take the Operator's own typed words as an Answer. It adds, as items in its own batch: a `typed note` Source owned by the Operator holding their words, the Answer and its effects as above. It writes them in its own single commit.

Done when: the other skill's commit holds the Source, the Answer and its effects.
