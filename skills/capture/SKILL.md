---
name: capture
description: Turn incoming material into Requirements, Questions and Answers. Use for `/capture`, when the Operator types, pastes or drops in material (a note, an email, meeting notes), pastes a story mapping session or a Miro card list, asks for the story map paste template, or gives a Confluence page URL and says to capture it, says "re-read <URL>", says "check <Jira key or Epic>" for a handed-off Epic, gives an answer to an open Question, or brings back a Stakeholder's Sign-off (their ticked Sign-off page, or what they agreed when they read their view with the Operator).
---

# Capture

One Capture is one operation under **Every write: confirm, then write** in the Tool-owned block of `AGENTS.md`. The record shapes are in [templates/](templates/).

A Capture writes Sources, Requirements (on an existing Feature or in `requirements/unplaced.md`), the story map and Milestones, Questions, Answers, withdrawals and their replacements, re-scores, new People in `project.md`, Sign-off entries in an Epic's `signoffs.md`, the folder indexes and the log, and sends the Jira reply to an in-build Question it answers. Features and Decision coverage belong to other skills: a Requirement with no fitting Feature goes to `unplaced.md`.

## Rare flows

Four flows live in their own files beside this one. Read a file when its flow starts, and follow it alongside these steps:

- [confluence.md](confluence.md): a Confluence page URL, captured or re-read.
- [signoff-readback.md](signoff-readback.md): material that brings back a Stakeholder's Sign-off.
- [story-map.md](story-map.md): a story mapping session pasted in, a Miro card list (a CSV export or copied board text), or a request for its paste template.
- [epic-check.md](epic-check.md): "check <Jira key or Epic>" for a handed-off Epic (the whole file); an Answer to a Question raised from an engineer's `Business question` (its **Jira reply** section alone).

## 1. Find the Project

For a Confluence page URL, first read the page as [confluence.md](confluence.md) says; a re-read belongs to the Project whose `sources/` holds the earlier reading, and a Sign-off page to the Project whose log names its URL, then is read as [signoff-readback.md](signoff-readback.md) says.

Above the batch, say in one plain sentence which Project you think the material belongs to and why, starting with its own name and code ("Deck linter `CDL`, because it is about the deck size rule"). When you cannot tell which Project it belongs to, ask and propose nothing yet.

Material that plainly bears on several Projects becomes one Source per Project, each holding only the parts that Project uses, with an `Also in:` line naming the others. Each Project's records go in that Project's own batch items, and each Project's log gets the entry.

Then read each Project's `index.md`, `project.md`, `storymap.md` when it has one, every active Requirement (each Feature file and `requirements/unplaced.md`) and `questions/index.md` with the files of its `open` and `chasing` Questions. Next IDs: one above the highest in use for each kind, found with `grep -rhoE '<CODE>-(SRC|REQ|Q|ANS|SO|MIL)-[0-9]{3}' projects/<slug>/ | sort -u`.

Done when: the Project is named with a reason, and you hold its active Requirements, open Questions, People and next free IDs.

## 2. Read the material into candidates

Go through the material in order and turn each point into candidates:

- **Requirement**: one testable need or constraint, restated as one plain sentence that carries its own terms: an option with its price or condition, a rule with the details that pin it down (which door, which month), a limit with its number. Two needs become two Requirements only when each still stands as a need with the other gone. Place each on the Feature it belongs to, or in `unplaced.md`.
- **Question**: something the material says is not known or not settled. Propose `Impact` and `Uncertainty` (1 to 3 each), `Score` (their product, as one number), a one-line `Score reason` in canonical terms, as the Veneer section of `AGENTS.md` says ("the booking Epic", never its shown name), and `Building on a guess`. A Score of 1 or 2 is proposed as `parked`; any other as `open`.
- **Answer**: a point that answers an open or chasing Question. See **Answers** below.
- **Person**: someone the records need (an owner, someone to ask) who is not in `project.md`. Ask for their role (`Operator`, `Stakeholder` or `engineer`) rather than guess.

Label each Requirement candidate against the Project's active Requirements:

- **new**: nothing active says it. Written as a new Requirement.
- **duplicate** of `<ID>`: an active Requirement already says it. It gets only a log line naming the Requirement and where it was said again.
- **refines** `<ID>`: the same need, stated more precisely or narrowed. Proposed as "withdraw `<ID>` and replace it with `<new ID>`: <new statement>", the one replacement stating the whole narrowed need; the replacement goes where `<ID>` is.
- **conflicts** with `<ID>`: the material says something an active Requirement contradicts. The Operator settles it, through a new Question that cites both Sources, with `Affects: <ID>`; `<ID>` stays active meanwhile. Say so in the item, and that the Operator can override it ("the new one's right"). An override records a Decision owned by the Operator as the Answer to that Question, then withdraws and replaces `<ID>`.

For a re-read, label the parts against the earlier reading first, as [confluence.md](confluence.md) says: its changed and new parts become candidates here, and its unchanged parts count as listed.

Done when: every point in the material is a candidate or is listed as not used, and every Requirement candidate has a label.

## 3. Propose

Settle every label, score and ID before you show the batch, so it states only the results. When the material quotes a third-party passage, run the **copy check** last, over the whole batch. The retellings are every line built from the passage: the Source's summary, each Answer's statement and its `Grounds:` line, and the statement of each Requirement such an Answer creates or puts in as a replacement. Copied text is a run of four or more of the passage's words in a row, a plural in -s counting as its singular. Check by command, with the passage and the retellings as the batch will show them, each retelling on one line; it prints each four-word run a retelling shares with the passage. Say each retelling holding a printed run again differently, and run the check again until it prints nothing.

```sh
awk 'function g(s,a,  n,w,i){s=tolower(s);gsub(/[^a-z0-9]+/," ",s);n=split(s,w," ");for(i=1;i<=n;i++)if(length(w[i])>3)sub(/s$/,"",w[i]);for(i=1;i+3<=n;i++)a[w[i]" "w[i+1]" "w[i+2]" "w[i+3]]=1} /^----[ \r]*$/{p=1;next} !p{q=q" "$0;next} {r[++m]=$0} END{if(!p){print "no ---- line";exit 1};g(q,A);for(j=1;j<=m;j++){split("",B);g(r[j],B);for(k in B)if(k in A)print k}}' <<'EOF'
<the passage, as given>
----
<every retelling, one per line>
EOF
```

Show the batch under the heading `Capture: <title of the Source>`, with that sentence above it. Order the items so the Operator can amend by number:

- **Item 1, the Source**, as [templates/source.md](templates/source.md) shapes it, with its ID and the exact text it will keep, shown in full in this reply, never by pointing back to an earlier one (a filled template is shown again whole):
  - Own organisation's material (the Operator's notes, colleagues' emails, meeting notes, internal pages): the parts used, word for word. Parts not used stay out of the Source and are listed in one line after the items.
  - Third-party material (articles, standards, rulebooks, codes of practice), including a passage quoted inside own material: cut the passage out and mark the cut `[…]`, keeping every own word around it exactly as given, then add its location (title, publisher, year, section, URL if any) and a summary in your own words. Records and the batch carry the passage only as that location and own words. Own words means the point retold plainly, as you would say it to the Operator: short, in your sentence shape and your vocabulary, keeping only names, numbers and section numbers from the original.
- **For a Sign-off read-back, item 2 is the Sign-off entry**, as [signoff-readback.md](signoff-readback.md) says.
- **For a Handed-off Epic check**, the items are as [epic-check.md](epic-check.md) says, and each Jira reply sits directly after the Answer it carries.
- **Then one item per candidate**, in the order the material raises them: its label, the record it will write (ID, statement, where it goes) and, for a Question, the proposed scores and reason.
- **The last item, indexes and log**: the folder indexes changed (`sources/index.md`, `questions/index.md` re-ranked, `features/index.md` for a placed Requirement), the `storymap.md` lines changed as **Story map** in 4 says, and the log entry's heading.

When everything in the material is a duplicate, the batch is only the log note and no Source is written.

After the items and any "not used" line, end every batch, and every showing again after an amend, with "Nothing is written yet." on its own line, word for word, then the ways on: accept all, edit by number, or reject.

Done when: for material quoting a third-party passage, the copy check prints nothing for the batch's retellings; and the batch is shown in that order, ending with "Nothing is written yet." and the ways on.

## 4. Amend, confirm, write, log, commit

As `AGENTS.md` says, numbering the items afresh after each amend and holding each proposed ID as `AGENTS.md`'s **Amend** step says. For material quoting a third-party passage, run the staged copy check below before the commit. Writing:

- **Source**: `sources/<ID>-<slug>.md`, from the template, leaving out lines and parts that do not apply.
- **Requirement line**: `- **<ID>** <statement> · Source: <SRC or ANS ID> · Status: active`, added at the end of its Feature's `## Requirements` list or of `unplaced.md` (replacing "None."). A withdrawal strikes the old line in place, as the Records rule in `AGENTS.md` says: `- ~~<the line as it was, with Status: withdrawn>~~ · Withdrawn <date> · Reason: <why> · Replaced by: <ID>`, leaving out ` · Replaced by: <ID>` when nothing replaces it.
- **Question**: `questions/<ID>-<slug>.md` from [templates/question.md](templates/question.md), and a row in `questions/index.md` in the rank order that file states.
- **Answer** and the Question's changed header lines: in the Question's file, as **Answers** says.
- **Person**: a row `| <name> | <role> | <what they look after, or blank> |` in the People table of `project.md`.
- **Sign-off entry**: added at the end of the Epic's `signoffs.md`, as [signoff-readback.md](signoff-readback.md) says.
- **Indexes**: a row in `sources/index.md`; the Requirement IDs in `features/index.md` when a placed Requirement is added or withdrawn. A folder index that does not exist yet is made from its template in [templates/](templates/) and linked from the Project's `index.md`, with that file's "No … yet" line updated.
- **Story map**: in a Project with `storymap.md`, each new Requirement a Capture writes outside a story map session, other than a replacement, is added under `## Not on the map` as `- <ID> · from <Source ID>`, replacing "None.". A replacement takes the withdrawn Requirement's place on the map; a Requirement withdrawn with no replacement is taken off it.
- **Jira reply**: posted or written to `outbox/` as **Jira reply** in [epic-check.md](epic-check.md) says.
- **Log**: `## [<date>] capture | <Source ID> <Source title>` (`capture | <Epic ID> handed-off Epic check` for a check) (or `capture | duplicate of <ID>, …` when nothing else is written), then one line per file written in canonical terms, as **Log** in `AGENTS.md` says, the IDs created, withdrawn or answered, one line per Sign-off entry (`Sign-off <SO ID> (<name> agreed <IDs>; not agreed <ID> → <Q ID>) in epics/<ID>-<slug>/signoffs.md`), and one line per duplicate: `Duplicate: <ID> said again in <Source ID>; nothing written`, naming the material by kind, owner and date when no Source is written. Material for several Projects writes the same heading in each Project's log, all in the one commit.

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
  - An Answer to a Question raised from an engineer's `Business question` (its `Raised from:` Source is `Kind: Jira item`) carries a Jira reply, as **Jira reply** in [epic-check.md](epic-check.md) says.

Done when: each Answer item has its Kind, an owner from People for a Decision, and one effect item per Requirement in `Affects:`.

### Embedded Capture

Another skill's batch may take the Operator's own typed words as an Answer. It adds, as items in its own batch: a `typed note` Source owned by the Operator holding their words, the Answer and its effects as above, a Jira reply included. It writes them in its own single commit.

Done when: the other skill's commit holds the Source, the Answer and its effects.
