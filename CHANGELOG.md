# Changelog

Each entry says what changed for an Operator's Workspace and how older record shapes are read.

## 0.21.0 · 2026-11-19

Delivery planning, from a story map to a Gantt: `capture` reads a story mapping session, `slice` keeps Features within Milestones and turns enablers into work, `pack` writes Technical Enabler packs, and a new skill, `plan`, forecasts when Milestones and Epics will land.

- **Story maps.** `capture` reads a story mapping session into one Capture: a Source, the Requirements, the Project's `storymap.md` (the map, holding Requirement IDs only), a Milestone record per release line in `milestones/`, and Questions for each Milestone missing its outcome, success metric or target, each risky area and each technology idea. Ask for the story map paste template to get the shape to fill in. A session in looser text, or a Miro card list (a CSV export or copied board text, which keeps no order), is read once every gap is answered or every card slotted, and once every Miro card is placed or set aside, `capture` shows the whole filled template again, in the same reply as the batch. A later session amends the living map. Once a Project has a map, a Requirement captured outside a session goes under `## Not on the map`.
- **Slicing within Milestones.** In a Project with a story map, `slice` keeps each new Feature within one Milestone. A grouping that crosses a Milestone boundary is replaced by one Feature per Milestone, and the batch shows it under **Milestone boundary**. Each Milestone's `## Members` lists the Features holding its Requirements. A Requirement not on the map can still be placed, with a warning that no Milestone counts it. A Project with no map slices as before.
- **Enablers.** `slice` turns each enabler from the map, or one you ask for, into a Technical Enabler (an Epic of its own, with `Technical Enabler: yes` and an `Enables:` line, which the Epics covering those Requirements depend on) or an Enabler Story (an `<CODE>-ENS-<nnn>` line under `## Enabler Stories` in the Epic it serves, for the engineers: a pack never mentions one, by its ID, its name or what it does). A Technical Enabler is not a second-Epic pain point, but one enabling no Requirement is.
- **Technical Enabler packs.** `pack` covers a Technical Enabler on its own Questions and Answers only. Its section 4 lists each Requirement it enables with the Epic delivering it, and its section 9 says what each one makes possible. Several gaps that look N/A for one reason can be marked N/A together, once. An Epic depending on a Technical Enabler names it in section 7 as built first, and nothing more. `handoff`'s Drift for a handed-off Technical Enabler also reports Requirements it enables that are newly enabled or withdrawn.
- **Every pack** names people by their Role from People, in its Who line, its Decision owners and the gap Questions it drafts, never by name. A Delivery term your Veneer gives no shown name shows as its canonical term, never as another term's shown name. The pack's link line in `index.md` keeps a fixed canonical wording (`first pack, written <date>` or `replaces pack-v<N>.md, written <date>`). Before this, a pack could name a person, show a Technical Enabler by the shown name for Epic, and word its link line freely. Packs already written stay as they are.
- **An empty Sign-off view writes nothing.** When a Stakeholder has nothing to check in a pack (no guess, no call of theirs, no Decision they have not agreed), `signoff` says so in plain lines and writes no view, for any Epic. Before this, nothing stopped Jenny writing a view that held nothing to sign.
- **Plans, with Gantts and drift.** A new skill, `plan`, makes a Plan for a Project from weekly Throughput (Stories finished each week, typed or read from the team's Jira project) and each handed-off Epic's open and done Story counts, or an engineer's low to high range. A Forecast script runs the Monte Carlo forecast and writes the likely and very likely dates of every Epic and Milestone, each Milestone's chance of meeting its target, the critical path and a Mermaid Gantt, with steps for pasting it into Lucid. Every date Jenny gives is quoted from the Forecast, never worked out by her. Each Plan version is frozen in `plans/plan-v<N>/` with a Stakeholder view and an Operator view, and raises Questions for Epics with no Story count and Milestones likely to miss a target their Stakeholder set. Say when a Plan went out ("plan-v2 went to Margaret"), and the next Plan reports which dates have moved since. Ask "when will <Milestone> land?" for the latest Plan's dates.
- **The Guard** knows the new records: Milestone (`-MIL-`) and Enabler Story (`-ENS-`) IDs, and Plan folders, frozen once committed except for a `Shown:` line added to `plan.md`. It also rejects a commit whose record holds a Veneer shown name or alias in its `Score reason:` line, singular or plural, outside a code span, naming the file, the line and the canonical term to use. Only Jenny writes that line, so the rest of a record's text, a Source's quoted words and your titles included, stays unchecked. The Jenny block in `AGENTS.md` now also says each log line names a record by its canonical term and ID. Before this, `pack` could write "the booking spec" in a Score reason and `capture` could log "Open item".
- Your Workspace: `setup`'s Upgrade copies the new skill files, `plan` among them, updates the Jenny block in `AGENTS.md` (which now lists Milestone IDs and frozen Plan folders), and replaces the Guard, as usual. Older record shapes: unchanged, and read as they are. A Score reason already committed is checked when that record is next changed, and Jenny rewords a slip in it then. A Project with no story map, Milestones or Plans works as before.

## 0.20.1 · 2026-11-17

Fixes to `capture` and `pack` found by the 0.20.0 Gate run.

- `capture` keeps a Question's `Score reason` in canonical terms, like every other line of a record: a handed-off Epic is an Epic there, whatever your Veneer shows. Before this, a Score reason could carry a Veneer shown name, such as "spec".
- `capture`'s copy check counts a plural in -s as its singular, so "reasons within its control" now matches a passage's "reason within its control". Capture's write step now opens by saying the staged copy check runs before the commit. Before this, a retelling could copy four words of a third-party passage by changing one to its plural, and the staged check could be skipped.
- `pack`'s Decision coverage writes a gap Question's `Category` line as the category's name and nothing more, so a Quality Question reads `Category: Quality` and names its characteristic in the question itself. The Data category is settled only by records saying what the service keeps, for how long and who owns it, never by a Requirement on what a screen shows, and has a probe question of its own. Before this, a Quality Question's Category line could carry its characteristic, and Data could be marked settled by what a screen shows.
- An amend keeps each proposed ID. `AGENTS.md`'s Amend step now says how a record's ID behaves while it is proposed but not yet written: it keeps the ID it was first shown with, a dropped record's gap is closed up by the later IDs of its kind, and only then does a record the amend adds take the next ID of its kind. `capture` and `pack` both point to that step. Before this, `capture` said only to renumber the batch and `pack` to renumber its unwritten Question IDs, and Jenny could move an already-proposed Requirement or Question to a later ID, leaving its first ID never written.
- Your Workspace: `setup`'s Upgrade copies the new skill files and updates the Jenny block in `AGENTS.md` as usual. Older record shapes: unchanged. Questions and packs already written stay as they are.

## 0.20.0 · 2026-11-17

First-round usability fixes: Sign-off views explain themselves, Jenny keeps quiet about a matching Tool version, placeholders show what to write, and `capture` and `lookup` load cleanly in Cursor.

- A Sign-off view's diagrams explain themselves. Each diagram has a lead sentence saying which part of the flow it shows and why the Stakeholder is looking at it, nodes labelled in about 8 plain words with their IDs, and a walkthrough under it, one bullet per node, saying what happens there and why. A published page carries the lead sentence and walkthrough too. Before this, a diagram stood alone, with all its detail in the node labels.
- A Sign-off view's worked examples are laid out to follow. Each names a scenario in the Stakeholder's world, then its **Inputs:**, then one outcome per answer of a Question, or one **Outcome:** for a Decision. Its rates, fees and deposits come from the pack's rules, and where the pack gives no figure yet, the outcome says so in words. Before this, an example ran its inputs and outcomes together in one line.
- In the Jenny mode, a matching Tool version is silent: the reply opens on your request and says nothing of the version check. Before this, the step said only to go on, and Jenny could open a reply by reporting that the versions matched. A mismatch still stops her with the warning, as in 0.15.6.
- Where a template or skill asks Jenny for a short title, an option or a note in her own words, it now shows an example of one, such as "Who approves big refunds". This covers the Question, Epic, pack and Sign-off view templates, and the replies of `lookup`, `signoff`'s Standing, `slice` and `up-next`. Before this, the placeholder said only "a few words", with nothing to show what those words should be.
- `capture` keeps its three rare flows in reference files in its own folder: `confluence.md` (reading a Confluence page), `epic-check.md` (a handed-off Epic check and its Jira reply) and `signoff-readback.md` (a Stakeholder's Sign-off read-back). Capture reads one only when its flow starts. While any skill is held, the Jenny mode re-reads each reference file it sent Jenny to, every turn, along with its `SKILL.md`. Captures behave as before. Before this, `capture` held every flow in one long `SKILL.md`, which Cursor followed less reliably, so Captures there came out inconsistent.
- `capture`'s and `lookup`'s descriptions parse as plain YAML, so Cursor loads both skills. Before this, a colon inside each description broke Cursor's reading of the skill's header.
- Your Workspace: `setup`'s Upgrade copies the new skill files as usual. Older record shapes: unchanged. Sign-off views already written stay as they are and are not redrawn.

## 0.19.1 · 2026-11-16

Acceptance check SU-02 grades a Cursor Workspace correctly.

- SU-02's key line for files changed outside the skills folder now leaves out the run's own skills folder, `.claude/skills` or `.cursor/skills`. Before this, it always left out `.claude/skills`, so a correct Cursor upgrade failed the check.
- Your Workspace: unchanged. Older record shapes: unchanged.

## 0.19.0 · 2026-11-14

`pack` scans each drafted pack's shape with a script.

- Before proposing a pack, and again after each amend, Jenny runs the pack shape scan (`<skills>/pack/scripts/pack_shape.py`) on her draft. It names each section missing, out of order, repeated or not in the template, and a draft over the 300-line cap, one per line. Jenny fixes the sections and scans again; a draft over the cap still ends in a re-slice proposal. Before this, she counted the draft's lines and checked its sections by reading it over, and a pack could reach you with a section dropped or in the wrong place.
- Older record shapes: unchanged. Packs already written are frozen and are not scanned again.

## 0.18.0 · 2026-11-14

`setup` installs and upgrades through one script.

- `setup`'s Install and Upgrade still propose a batch, wait for your yes and report, but the file work after your yes is one script, `<clone>/skills/setup/scripts/install.sh`: copying the skills and `VERSION`, writing the Tool-owned block of `AGENTS.md`, `CLAUDE.md`'s `@AGENTS.md` line, `git init` and the Guard. It runs the Python check first, checks everything before it writes anything, and stops with one line saying why when it can't go on. Before this, Jenny ran each of those commands by hand, and could miss one.
- An upgrade's batch retells each CHANGELOG entry in your Veneer's shown names, filled in. Before this, it could show the skill's placeholder, such as "<shown name for Epic>", word for word.
- The Guard no longer leaves a `__pycache__/` folder in your skills folder after each commit, which left the Workspace with uncommitted files.
- Older record shapes: unchanged.

## 0.17.0 · 2026-11-14

A Guard checks every commit in the Workspace.

- `setup` installs the Guard: a git pre-commit hook that runs `<skills>/jenny/scripts/guard.py` on every commit, whichever runtime you use, Claude Code or Cursor. It rejects a commit that holds a malformed record (a missing title or required header line, an ID that is not the Project code and three digits, an ID defined twice, a log heading out of shape, or a Veneer shown name where a record's structure needs the canonical term), a `veneer.md` the Veneer scan can't read, or a canonical word the Veneer renames in `outbox/` text outside code. It names each file and problem, and Jenny fixes them and commits again. A clean commit passes with no output. Before this, those rules held only as far as Jenny followed them.
- `setup`'s Upgrade adds the Guard to an existing Workspace, and replaces it on each later upgrade. If your Workspace's git already has a pre-commit hook of your own, or sets `core.hooksPath`, your hook is kept and the Guard is not added; `setup` says so.
- **Every write: confirm, then write** in the Tool-owned block of `AGENTS.md` says a rejected commit is fixed and committed again, never bypassed with `--no-verify`. `setup`'s Upgrade replaces the block as usual.
- Older record shapes: unchanged, and read as they are. The Guard checks only the files a commit adds or changes, and in a log only the lines it adds, so an older log slip never blocks an upgrade or a later operation.

## 0.16.1 · 2026-11-14

Jenny's report after a write goes through the Veneer scan.

- **Every write: confirm, then write** in the Tool-owned block of `AGENTS.md` has a sixth step, **Report**: one reply after the commit, holding what the skill's own steps say to tell the Operator and the commit message, with every file it names as a full path in a code span. With a `veneer.md`, it goes through the Veneer scan before it is sent, and the operation is not done until it has been sent that way. Before this, the operation ended at the commit, so the short reply after it was often sent unscanned, and words such as "the questions index" reached the Operator. `setup`'s Upgrade replaces the block as usual.
- Older record shapes: unchanged.

## 0.16.0 · 2026-11-13

Jenny scans her own replies for Veneer slips, and needs Python 3.9 or later.

- Step to do first: install Python 3.9 or later, so that `python3 --version` prints it. `setup` refuses to install or upgrade without it.
- With a `veneer.md`, Jenny runs every draft reply through the Veneer scan (`<skills>/jenny/scripts/veneer_scan.py`) before sending it, the version-mismatch warning included, and rewords each canonical word it names outside a code span. Before this, she read the reply over once herself, and words such as "the deposit question" or a bare `Question:` label still reached the Operator.
- The Veneer section of the Tool-owned block of `AGENTS.md` is new: its **Veneer scan** paragraph replaces the read-through, and the section is now the one statement of the Veneer rule. The skills no longer restate it. `setup`'s Upgrade replaces the block as usual.
- If `veneer.md` can't be read, Jenny's reply opens with one line saying so and why, so the Operator can fix it.
- Older record shapes: unchanged. A `veneer.md` keeps its table header, `| Canonical term | Shown as | Also understood as |`, which the scan reads.

## 0.15.8 · 2026-11-13

A new pack version is linked from the Project's `index.md`.

- `pack`'s Pack batch carries one more item: the Project's `index.md`, with one link line for the new `pack-v<N>.md` under the Epic's line, after its earlier pack links, in their shape. Every other line of `index.md` stays as it is, earlier pack links included, and the batch shows the new line in full. Coverage still leaves `index.md` alone. Before this, the skill said only that `index.md` "keeps the links it has", so a new pack version could be written with or without a link to it, and one the index does not link cannot be found by reading `index.md` first.
- Older record shapes: an Epic pack version written before 0.15.8 with no link line in `index.md` stays unlinked and is read as it is.

## 0.15.7 · 2026-11-13

An upgrade names every version it skips.

- `setup`'s Upgrade proposal lists every CHANGELOG entry between the two versions, each led by its version number, with how older records are read. Entries the Operator would not notice may share a line, as long as it names each of their versions. Before this, an upgrade across many versions (0.2.0 to 0.15.6) could fold them into a few bullets that named no version in between.
- Older record shapes: unchanged.

## 0.15.6 · 2026-11-13

A Tool version mismatch stops Jenny before she answers.

- The Tool-owned block of `AGENTS.md` now carries the version check itself: under **Read first**, before anything else on every turn, Jenny runs the Jenny mode's version check. Until it passes, its warning is the whole reply and every other rule waits, Lookup included. This holds outside the Jenny mode too, in any chat that reads `AGENTS.md`, except for a request `setup` owns, such as an upgrade, which runs as `setup` says. In the Jenny mode, `setup` waits for the versions to match like every other skill. Before this, a question about the records could be answered in full from the Lookup rules, citations and all, with the mismatch never mentioned.
- The Jenny mode's version check says it runs before any rule in `AGENTS.md` and before the Operator's message is read as a request, and that the warning holds no answer, record ID or anything read from a Project.
- Older record shapes: unchanged.

## 0.15.5 · 2026-11-13

Every `capture` proposal ends with "Nothing is written yet."

- `capture`'s Propose step names the closing words itself: after the items and any "not used" line, the batch ends with "Nothing is written yet." on its own line, then the ways on (accept all, edit by number, or reject). This holds for every capture, the Confluence page reading, Sign-off read-back and Handed-off Epic check included, and for the batch shown again after an amend. Before this, a Sign-off read-back could put "(nothing is written yet)" in its heading and leave the sentence out at the end.
- Older record shapes: unchanged.

## 0.15.4 · 2026-11-13

Jenny names a renamed record by its topic in shown names.

- The Veneer rules in the Tool-owned block of `AGENTS.md` cover a record called by what it is about: its shown name, its ID, or both ("the Open item on deposits", "Open item `HAL-Q-014`"), and an engineer's ask can also be their `Business question`, in a code span. Before this, a reply could close with an offer such as "the deposit question" while every other line said "Open item".
- The read-through before sending covers the whole reply, offers, next steps and headings included.
- Older record shapes: unchanged.

## 0.15.3 · 2026-11-13

`setup` proves the Tool-owned block of `AGENTS.md` landed whole.

- Install and Upgrade copy the block from `agents-block.md` with a shell command instead of retyping it, into a new file that must pass a check before it replaces `AGENTS.md`: each marker appears once and the marked block equals the template. A failed check is built again, and `AGENTS.md` stays as it was until it passes. Install into a folder whose `AGENTS.md` already holds the markers replaces only the block. Before this, an install could commit a block cut off after its first paragraph, with no end marker and none of the rules, and still report done.
- Older record shapes: unchanged.

## 0.15.2 · 2026-11-13

`pack` writes only the files in its batch.

- Coverage and the pack write exactly the files their batch lists. A new Epic pack version lives in the Epic's folder, and the Project's `index.md` keeps the links it has. Before this, writing `pack-v2.md` could also add its link to `index.md`, a change the Operator never saw in the batch.
- Older record shapes: an `index.md` that links an earlier Epic pack version keeps that link and is read as it is.

## 0.15.1 · 2026-11-13

`pack` files a Question about how a stage shows under States, not Data.

- Coverage files an existing Question with no `Category:` line by the decision it asks for: a stage something is in, or how that stage shows, files under States; which facts are kept or shown, under Data. Before this, a Question asking whether a court closed for repairs shows as closed or as taken could be filed under Data, because Data said "shown".
- States now covers how each stage shows to the people looking at it, and its probe asks so.
- Older record shapes: unchanged.

## 0.15.0 · 2026-11-13

`capture` keeps a third party's phrases out of a Decision's grounds.

- A Decision resting on a third-party Source carries one `Grounds:` line under its Answer: the Source's title and section, then the one point the Decision rests on, retold from the Source's own-words summary in a short clause. Before this, grounds could retell the whole quoted passage and reuse its phrases ("withdraws a confirmed hire", "within its control"). The rule now holds whether or not the Source has a URL.
- The copy check runs a second time on what is written: after staging and before the commit and any Jira post, over every added line except the Source's kept quote lines. A run that is only a name or a title stays.
- Older record shapes: an Answer written before 0.15.0 may carry its grounds in any form, or none, and is read as it is.

## 0.14.3 · 2026-11-13

`lookup` doesn't guess answers under **Not known yet**.

- A gap line names the open Question in its own wording and says who it is waiting on: the person on its `Ask:` line and since when, that they are still to be asked, or that nobody has been asked yet. It offers no possible answers, options or likely outcomes, not even hedged. Before this, a reply could list "a credit towards another date" as one way the gap might go, which is another Project's rule.
- The Lookup rules in the Tool-owned block of `AGENTS.md` say the same, so plain-words lookups follow it too.
- Older record shapes: unchanged.

## 0.14.2 · 2026-11-13

`capture` keeps an option and its price as one Requirement.

- A Requirement carries its own terms: an option with its price or condition, a rule with the details that pin it down, a limit with its number. Before this, "tables set out on request, for a $20 fee" came out as two Requirements, and so did "the side door's code for the booking's month".
- A refinement's one replacement states the whole narrowed need, instead of a replacement plus a new Requirement for the rest.
- Older record shapes: unchanged.

## 0.14.1 · 2026-11-13

Fewer Delivery terms copied from skill wording into chat under a Veneer.

- `setup` Upgrade shows the `AGENTS.md` block diff in a fenced `diff` block and retells the block changes and the CHANGELOG entries in shown names, instead of copying their canonical phrases.
- `lookup` fills its reply shape with the shown name for Question, and says an open one asks its wording and is not settled yet. Before this, its shape said "the open Question that covers it", which Jenny copied as "the question is open".
- `capture` opens its batch with one plain sentence naming the Project and why, with no label in front. Engineers' shapes are named in code spans throughout (`Business question`, `Business call made in build`), and the reply after the commit leads each line with the record's shown name and ID.
- `handoff`'s hand-on says engineers post what they need from the business as a `Business question` on the work item.
- Older record shapes: unchanged.

## 0.14.0 · 2026-11-12

Check a handed-off Epic and reply through Jira.

- `capture` checks a handed-off Epic. "Check <Jira key>" (or "check <Epic>") reads the tech face named on the Epic's `Tech face:` line through the Atlassian MCP: the Jira Epic, its child Stories and all their comments. PRs and repos are not read. Only comments new since the last check (or edited since) are material; the rest are counted in one line. Descriptions are read as context.
- What comes back: a `Business question` becomes a Question, `Building on a guess: yes` and `Needed by: <Epic ID>` when the team builds around it; one about an open Question flags that Question instead. A `Business question` against an active Decision is pushback: a Question with `Affects: <Answer ID>`, and the Decision stays in force. A `Business call made in build` is a Decision owned by the engineer, flagged "decided during build", answering a Question raised in the same batch when none fits; an engineer not yet in People is proposed in the same batch.
- The check's Source is `Kind: Jira item`, with `URL:` and `Read:`, keeping each comment used word for word under `<key> · comment <ID> · <author> · <date>`. The log heading is `capture | <Epic ID> handed-off Epic check`, with a line naming every work item and comment ID read; `up-next` takes the last check date from it. A check with nothing new still logs, so the date is kept.
- Jira reply: an Answer to a Question raised from an engineer's `Business question` carries a reply on the same work item, in the same batch: it quotes the Answer ID in Veneer names, names people by role and never shows a Source ID. A `Business call made in build` gets no reply. After the yes the records are written, then the reply is posted through the MCP (a failed post falls back to `outbox/`), or under `Outbound: outbox` written to `outbox/<work item key>-reply-<Answer ID>.md`, all in the operation's one commit. The Operator can answer an in-build Question as an amend to the check's batch.
- `handoff`'s hand-on says "check <Jira key>" reads the team's business questions.
- Older record shapes: a check logged before 0.14.0 names no comment IDs, so every comment created before its date counts as seen.

## 0.13.0 · 2026-11-12

Sign-off read-back and standing.

- `capture` reads a Sign-off back. Capturing a Stakeholder's published Sign-off page (its URL in a `signoff | Publish` log entry), or a shoulder check the Operator types ("Tom read his view with me: …", its own Capture), proposes one batch: the Source, one `<CODE>-SO-<nnn>` entry added to the Epic's `signoffs.md`, a Question for each Decision pushed back on, and an Answer for each call the Stakeholder replied to. A later read-back adds a new entry holding only what is new since their last one; with nothing new there is no entry.
- The `signoffs.md` entry follows `skills/capture/templates/signoffs.md`: `## <CODE>-SO-<nnn> · <Full name> (<role>) · <date>`, then `Pack: … · View: … · Where: <page URL | in person | by email>`, `Agreed:`, `Not agreed: <Answer ID> → <Question ID>`, `Not yet looked at:` (a line with no IDs left out) and `Source:`. `signoffs.md` is only ever added to; capture makes it from the template when it is missing.
- Pushback becomes a Question with `Affects: <Answer ID>`, `Building on a guess: yes` when the Epic is handed off. The Decision stays in force until that Question is answered. A tick on a Decision withdrawn since the view is recorded against the old ID, and Jenny says its replacement is still unticked.
- New `signoff` operation **Standing**: "where does <Epic> stand?" reports, per Stakeholder in People, which Decisions of the latest pack (each followed to its active replacement) they agreed, dispute (with the Question) or have not yet looked at. Sign-off attaches to the Answer ID, so a replaced Decision starts unagreed. There is no "signed off" state and no deadline. It writes nothing.
- `signoff` hand-ons now say "capture <page URL>" brings the ticks back.
- "Where does <Epic> stand?" goes to `signoff`, not `lookup`: `lookup`'s description now leaves it out, and the Lookup rule in the Tool block of `AGENTS.md` lets a question a skill names follow that skill. The Tool block changes on upgrade.
- Older record shapes: a `signoffs.md` entry written before 0.13.0 with only `Agreed:` reads as agreeing those IDs and nothing else; an Epic with no `signoffs.md` has no Sign-offs yet.

## 0.12.0 · 2026-11-12

Record a Handoff and report drift.

- New skill `handoff`. "Hand off <Epic> v<N>, tech face <Jira key>" (or `/handoff` naming a version) records the Handoff as one line under `## External items` in `epic.md`: `- Tech face: [<key>](<URL>) · Pack: pack-v<N>.md · Handed off: <date>`, in one confirm-then-write batch and one commit `[<date>] handoff | <Epic ID> pack v<N> to the delivery team`. It replaces `None yet.` or the old `Tech face:` line and changes nothing else in `epic.md`; the Project index says the Epic is handed off. A key given alone takes its Jira site from the links already in the Project, or Jenny asks for the link. Still no status field.
- "What's changed since handoff?" (or `/handoff` alone) reports drift and writes nothing: the handed-off pack compared with the records now, as new or replaced Decisions (build Decisions flagged "decided during build"), facts, Questions raised or settled, Requirements, N/A marks, Sign-offs since the handoff date, and any newer pack not yet handed over. It leads with one line such as "Engineers have v1 (HALL-12, handed off 2026-11-07); since then: 2 Decisions, 1 decided during build" and offers the next step: hand off the newer pack, or write one.
- `pack`: writing a new version for a handed-off Epic now moves its `Tech face:` line to that version in the same commit, shown as one more batch item. Before this, the line stayed on the old version until a separate Handoff. A gap Question's `Score reason:` is written in canonical terms, like the rest of the record.
- The Epic template shows the `Tech face:` line shape.
- Older record shapes: a `Tech face:` line written before 0.12.0 in this shape is read as it is; an Epic with `None yet.` under `## External items` is not handed off.

## 0.11.0 · 2026-11-12

Sign-off view and publish.

- New skill `signoff`. "Sign-off view for <person>, <Epic>" (or `/signoff`) writes a frozen `epics/<ID>-<slug>/signoff-view-v<N>-<person>.md` from the Epic's latest pack, in one confirm-then-write batch and one commit `[<date>] signoff | <Epic ID> <title> signoff-view-v<N>-<person>`. The person must be a Stakeholder in People; N counts that person's views of the Epic.
- The view follows `skills/signoff/templates/signoff-view.md`, addressed to the Stakeholder by name: 🔴 being built on a guess → 🟠 your calls (the open items whose `Ask:` names them, with why and Needed by; others' named in one line, unasked ones in another) → ✅ did we get these right (each Decision they have not yet agreed, with ID, owner, date and a checkbox; engineer-owned ones say "decided during build"; agreed ones listed once without a box) → ⚪ we think these don't matter (the pack's N/A rows) → flow diagrams in Mermaid, at most 7 nodes each besides start and stop → also worth knowing (other pain points, Left out, Depends on).
- Checkboxes sit only on Decisions. Worked examples are made up, marked so, in a one-line shape that cites the ID they show, with every number from the pack's rules.
- "Publish it" posts a view to Confluence after confirm: one whiteboard per diagram, then a page with each checkbox as a task item and each diagram embedded with its Mermaid source in an expand. Under `Outbound: outbox` it writes the exact page body to `outbox/<Epic ID>-signoff-view-v<N>-<person>.html` instead. The Confluence parent page is a new `Sign-off pages: <URL>` line under `## External links` in `project.md`, asked for the first time.
- `pack` now points at the Sign-off view once a pack is written.
- Older record shapes: a `project.md` without `Sign-off pages:` has no publish location yet; Jenny asks for one.

## 0.10.1 · 2026-11-12

Decision coverage files each existing Question under one category.

- Coverage's walk, which `pack` also runs, files each existing Question under one category before giving states: the one its `Category:` line names, or, when it has none, the one its own wording is about. Filing it there settles no other category; each still answers its own probe and is a gap where nothing covers it. Before this, a captured Question with no `Category:` line could land under the wrong category and hide a real gap.
- Older record shapes: unchanged. A Question without `Category:` files by its wording.

## 0.10.0 · 2026-11-12

Write the Epic pack.

- `pack` writes an Epic's pack on "write the pack for <Epic>" (or `/pack` asking for the pack). It runs Decision coverage first, then proposes the gap Questions and a new `epics/<ID>-<slug>/pack-v<N>.md` in one confirm-then-write batch and one commit `[<date>] pack | <Epic ID> <title> pack v<N>`.
- The pack follows `skills/pack/templates/pack.md`: header, **For the agent reading this**, then 1 Problem and outcome, 2 Words used here, 3 Settled Decisions (with "Agreed by" lines from `signoffs.md`), 4 Rules and examples per covered Requirement, 5 Still open: `DO NOT DECIDE` (parked listed apart), 6 Constraints, 7 Depends on, 8 Scope, 9 Acceptance criteria, Appendix A Decision coverage, Appendix B Pain points.
- The For-the-agent block tells the engineer's agent that Decisions are final and that `DO NOT DECIDE` items and uncovered business decisions come back as a `Business question`; calls made anyway come back as a `Business call made in build`. Both shapes are fixed code blocks in every pack.
- A pack uses Veneer names, names people by role, carries no Source IDs and no engineering sections. It may carry open Questions. A pack over 300 lines is never split: Jenny writes nothing and proposes a re-slice.
- Packs are frozen once written; a new version is a new file. The `AGENTS.md` block now says so for Sources, packs and Sign-off views.
- Older record shapes: a `pack-v*.md` written before 0.10.0 is read as it is and never rewritten.

## 0.9.0 · 2026-11-12

Decision coverage on an Epic.

- `pack` runs Decision coverage on one Epic, through `/pack`, "check coverage for <Epic>" or asking whether an Epic is ready for its pack. It walks all 11 categories every run (rules, boundaries, unwanted behaviour, states, variants, data, permissions, downstream, quality, rollout, examples) and shows each as settled (citing IDs), open (citing Questions), N/A (with the Operator's reason) or a gap. Quality is walked by the ISO/IEC 25010:2023 names: performance, reliability, security, interaction capability, compatibility, and safety where harm is possible. Writing the Epic pack itself comes later.
- Every gap gets a scored Question in one confirm-then-write batch and one commit `[<date>] pack | Decision coverage …`. A gap Question has `Category:`, `Needed by:` and `Affects:` naming the Epic, and `Raised from: Decision coverage of <Epic ID>`.
- Jenny may say a category looks N/A, but only the Operator marks it, with a one-line reason. The mark is a line under a new `## Not applicable` section at the end of `epic.md` (its shape is in the Epic template), which a later pack and Sign-off view read; a handed-off Epic takes marks too. A mark taken back is struck through, not deleted.
- Older record shapes: an `epic.md` without `## Not applicable` has no N/A marks; a Question without `Category:` was not raised by coverage.

## 0.8.0 · 2026-11-12

Capture from Confluence and re-read a page.

- `capture` takes a Confluence page URL, reads the page through the Atlassian MCP and proposes a batch as for any Capture. The Source is `Kind: Confluence page`, keeps the parts used word for word, and carries `URL:`, `Page version:` and `Read:` (the date read) in place of `Captured:`. A failed read proposes nothing.
- A URL already in a Source is a re-read ("re-read <URL>", or just the URL again). Jenny compares the page with the latest earlier reading and proposes only what changed. The new reading is a new Source with `Previous reading: <SRC id>`, holding every part it uses; the earlier Source is never changed. A Requirement built on changed text is withdrawn and replaced; one built on text that has gone comes up as a "withdraw?" item and stays active unless the Operator says to withdraw it. An unchanged page version proposes nothing.
- A withdrawn Requirement line with nothing replacing it leaves out ` · Replaced by:`.
- Older record shapes: none yet. Sources from 0.7.0 and earlier have no `URL:` line and are never re-reads.

## 0.7.0 · 2026-11-12

Slice a Project into Features.

- `slice` proposes how one Project's Requirements group into Features, through `/slice`, "slice the project" or "re-slice <Feature>", as one confirm-then-write batch and one commit `[<date>] slice | …`. Each Feature is a vertical slice a Stakeholder can see and sign off on its own, with exactly one Epic. Requirement lines move byte for byte from `requirements/unplaced.md` into `features/<ID>-<slug>.md`; each new Epic is `epics/<ID>-<slug>/epic.md` with Covers, Applies here too, Depends on, External items and Left out, and no status line.
- Each Requirement is covered by at most one Epic, the one the Operator picks as delivering it first. A Requirement that runs across Features sits in one, and the other Epics list it under **Applies here too**; one two Epics each need part of is split (withdrawn and replaced by two new Requirements). A re-slice can move a placed Requirement, its Covers entry with it. A handed-off Epic's `epic.md` stays as it is.
- A second Epic in a Feature, or a horizontal Feature, is flagged as a pain point with a re-slice suggested, and is written only with the Operator's reason, kept as a `Pain point:` header line in its `epic.md`.
- Asking what is unplaced lists the active Requirements in `requirements/unplaced.md`; it writes nothing.
- Older record shapes: none yet.

## 0.6.0 · 2026-11-11

Capture typed and pasted material.

- `capture` takes a typed note, a pasted email or meeting notes and proposes one numbered batch: the Project it belongs to and why, the Source, Requirements with their Feature placement, scored Questions, Answers to open Questions, and new People. Item 1 is always the Source; the rest follow the material's order, so the Operator can amend by number. Nothing is written before the yes; a no writes nothing.
- Own-organisation material is kept word for word (the parts used); third-party material, even a passage quoted inside own material, is kept as its location and an own-words summary. A copy check holds that summary, and every Answer and Requirement built from the passage, clear of four or more of its words in a row.
- Each Requirement is labelled new, duplicate, refines or conflicts against the active ones. A duplicate writes only a log line; refines withdraws and replaces under a new ID; a conflict becomes a Question citing both Sources and leaves the Requirement active, unless the Operator overrides it as their own Decision.
- Answers are marked `fact` or `decision`; a Decision needs an owner from People, and Jenny asks rather than guesses. Each Answer says "unchanged" or "withdraw and replace" for every Requirement it affects, and proposes re-scores for Questions touching what changed.
- The Tool-owned block of `AGENTS.md` points every skill at Embedded Capture, so the Operator's own typed words can answer a Question inside any batch. Its Veneer rule now keeps a renamed term's canonical word inside code spans in every sense, ordinary English included, and says how to reword: an ask of the Operator ("what I need from you", or the ask itself), "you didn't say", a record by its shown name, and a shown name with no canonical gloss beside it.
- Older record shapes: none yet.

## 0.5.0 · 2026-11-11

What to chase next.

- `up-next` answers "what should I chase next?" for one Project, through `/up-next` or plain words, with two lists. **Chase now**: every `chasing` Question, overdue first, with who was asked and days overdue, plus a nudge for each handed-off Epic (one whose `epic.md` has a `Tech face:` line) with the date of its last check from the log. **Shape next**: the top 5 `open` Questions, building-on-a-guess first, then Score, then soonest `Needed by`. `parked`, `answered` and `withdrawn` Questions never show. The list writes nothing.
- **Shape** ("shape 3") proposes `Ask:` from People, `Technique:` and `Chase by:` as one confirm-then-write batch that moves the Question to `chasing`, and drafts the ask in chat for the Operator to paste; the draft is not stored. **Asked** sets `Asked:` once the Operator says the ask has gone out. Each is one commit `[<date>] up-next | …`.
- Older record shapes: none yet.

## 0.4.0 · 2026-11-11

Upgrade a Workspace.

- `setup` gains **Upgrade**: after the Operator pulls a newer release into the clone, Jenny reads the clone path from `workspace.md`, compares versions and follows the clone's own `setup`, so the new version runs its own upgrade. One confirm-then-write batch, one commit `[<date>] upgrade | Tool <old> → <new>`. It replaces the Tool's skill folders, the `AGENTS.md` block between the markers and the copied `VERSION`, sets `Tool version:`, adds new settings with their defaults and MCP template changes. It never changes Operator setting values, `AGENTS.md` text outside the markers, MCP entries the Operator added, or any record. A Tool skill a later version drops is removed; the Operator's own skill folders stay. The batch ends with the restart: a new chat in the Jenny mode on Cursor, a new session on Claude Code.
- Rollback is reverting the upgrade commit; there is no downgrade.
- From 0.3.0 or earlier, which have no Upgrade: pull this version into the clone, then tell an agent in the Workspace to follow `<clone>/skills/setup/SKILL.md` to upgrade. From 0.4.0 on, asking Jenny to upgrade is enough.
- Older record shapes: none yet.

## 0.3.0 · 2026-11-11

The Jenny mode.

- On Cursor the Operator works in a Custom Mode named Jenny. `setup` hands on its settings at install; the mode's text points at the `jenny` skill, so later versions change the skill, never the mode.
- On every turn the mode checks the copied `VERSION` against `Tool version:` in `workspace.md`, and stops with a warning when they differ or the copy is missing.
- The mode routes each request to a skill by its `/name` or the triggers in its description, Veneer words included, so a skill added later routes without changing the mode. It re-reads that skill every turn until its operation is committed.
- The Tool-owned block of `AGENTS.md` spells out that a commit message keeps the log heading's bracketed date.
- The copied `VERSION` moves from `<skills folder>/setup/VERSION` to `<skills folder>/jenny/VERSION`. Install still treats a folder holding either as installed.
- Older record shapes: none yet.

## 0.2.0 · 2026-11-11

Look things up.

- `lookup` answers what one Project's records say, through `/lookup` or a plain question, in a fixed shape: **In short**, **Based on** (each ID with its file) and **Not known yet** (each gap with the open Question that covers it). It writes nothing.
- The Tool-owned block of `AGENTS.md` gains the Lookup rules, so plain questions follow them too: one Project, index first, active records only, gaps stay gaps, cite every ID and file. It also says how a withdrawn line is kept.
- Every batch is shown under a heading that names the operation in shown names, and keeps that heading when it is shown again after an amend.
- Older record shapes: none yet.

## 0.1.0 · 2026-11-11

First version: install a Workspace and create Projects.

- `setup` installs Jenny into an empty folder (or one holding Workspace records but no Tool copy) for Cursor or Claude Code: the skills, `AGENTS.md` with the Tool-owned block (plus a `CLAUDE.md` that imports it, on Claude Code), `workspace.md`, the runtime's MCP config, local git and a first commit.
- The copied `VERSION` sits at `<skills folder>/setup/VERSION` until the Jenny mode exists to hold it.
- `setup` creates a Project (code, slug, `index.md`, `project.md` with People and roles), changes People, and sets or changes the Veneer in `veneer.md`.
- Workspace-wide operations (install, Veneer) log to `log/YYYY-MM.md` at the Workspace root; Project operations log to the Project's own `log/`.
- Older record shapes: none yet.
