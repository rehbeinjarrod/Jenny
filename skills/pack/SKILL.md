---
name: pack
description: Run Decision coverage on one Epic, raising a scored Question for every business decision left unsettled, or write the Epic's pack after it. Use for `/pack`, when the Operator says "check coverage for <Epic>" or "write the pack for <Epic>", or asks whether an Epic is ready for its pack.
compatibility: Python 3.9 or later, as python3, for the pack shape scan (scripts/pack_shape.py).
---

# Pack

Two operations, each a confirm-then-write operation following the rules in the Tool-owned block of `AGENTS.md`:

- **Coverage** on "check coverage for <Epic>", on asking whether an Epic is ready for its pack, and on `/pack` alone.
- **Pack** on "write the pack for <Epic>", and on `/pack` with words asking for the pack itself. It runs Coverage's walk first and proposes the gap Questions and the pack in one batch.

Each writes exactly the files its batch lists. Pack's batch carries one Project `index.md` item, adding the new `pack-v<N>.md`'s link line (Pack step 4) and changing no other line. Coverage's batch carries no `index.md` item; its new Questions are listed in `questions/index.md`.

**A Technical Enabler** (`Technical Enabler: yes` in its `epic.md`): read [technical-enabler.md](technical-enabler.md) before step 1 of either operation. It changes Gather, the Walk, N/A marks and sections 4 and 9.

Today is `date +%F`.

## The 11 categories

Coverage walks all 11, in this order, every run. Each asks what an engineer would otherwise decide on the spot. The probes follow the EARS patterns (always, when, while, if … then, where) and are only for finding gaps: when a probe has no answer in the records, that is a gap. What you write stays plain: a Requirement is one plain line, a Question one plain sentence a Stakeholder could answer.

1. **Rules**: the business rules and sums the Epic carries out. Probe: what must always be true? What is the amount, limit or formula?
2. **Boundaries**: the edges of each rule: exactly at a limit, zero, the first and last day, an hour already started, rounding. Probe: at exactly <the limit>, which side wins?
3. **Unwanted behaviour**: what goes wrong and what the service does then: a failed payment, two people at once, a mistake, misuse. Probe: if <the unwanted thing> happens, then what?
4. **States**: the stages a thing passes through, what can happen in each, and how each stage shows to the people looking at it. Probe: while <it is in this state>, what can and cannot happen, and how does it show? What moves it on?
5. **Variants**: kinds of person, item, channel or time that change a rule. Probe: where <this kind>, what is different?
6. **Data**: which facts are kept, shown or reported, for how long, and who owns them. Settled only by records saying what the service keeps, for how long and who owns it; a Requirement on what a screen shows is not one. Probe: what does it keep, for how long, and who owns it?
7. **Permissions**: who can see and do what, and who cannot.
8. **Downstream**: other people, systems and processes that must know or act. Probe: when this happens, who else needs to hear of it, and what do they do?
9. **Quality**: how well it must work, by the ISO/IEC 25010:2023 names in business words: **performance** (how fast, how many at once), **reliability** (when it must be up, what happens when it is down), **security** (what must be protected, from whom), **interaction capability** (who must be able to use it, on what, with what needs), **compatibility** (what it must work alongside), and **safety** only where harm to a person is possible. Walk each by name.
10. **Rollout**: how it goes live: what exists today and moves over, who is told, the date or order of switching on.
11. **Examples**: worked cases with real numbers that a Stakeholder has agreed. Settled only by a Source or Answer holding such a case; a rule that an example could be worked from is not one.

Each category takes one **state**:

- **settled**: active Requirements or Answers say everything an engineer would need here. Cite each ID.
- **open**: an `open`, `chasing` or `parked` Question files under it. Cite each Question, and any settled IDs beside it.
- **N/A**: the Operator has marked it, in the `## Not applicable` section of `epic.md`. Show their reason.
- **gap**: blank, or a part that no Requirement, Answer or Question covers. Every gap gets a proposed Question in the batch. A category with an open Question and an uncovered part is "open, and a gap", citing both.

**Each existing Question files under one category.** That is the one its `Category:` line names; without that line, the one category whose subject is the decision the Question asks for. A stage something is in, or how that stage shows, is **States** (a parcel held at the depot); which facts are kept or shown is **Data**. It settles nothing elsewhere: every other category still answers its own probe, and is a gap wherever nothing covers it.

**N/A is the Operator's call.** When a category looks like it does not apply, say so and why ("looks N/A: the timetable keeps nothing of its own"), and still propose its gap Question; it would most likely score as `parked`. The Operator turns it into an N/A mark by giving a one-line reason ("data is N/A: …"); without one, ask for it. Only a gap can be marked N/A: a category with an open Question stays open until that Question is answered or withdrawn through `capture`.

## Coverage

1. **Gather.** Find the one Project and Epic as the Lookup rules say: the Epic by ID, title or the words used, asking when two could fit. Work in that Project's folder only. Read its `index.md`, `project.md`, the Epic's `epic.md`, its Feature file, every Requirement under **Covers** and **Applies here too** (in its Feature file), `questions/index.md`, and every Question file whose `Affects:` or `Needed by:` names the Epic, its Feature, one of those Requirements, or an Answer to one of them; a Question naming a Technical Enabler other than this Epic bears on that Technical Enabler alone. Read the Sources those Requirements and Answers cite. Note the highest `-Q-` number in the Project (`grep -rhoE '<CODE>-Q-[0-9]{3}' projects/<slug>/ | sort -u`); new IDs follow on from it.

   Done when: you hold the Epic's active Requirements, the active Answers and the Questions bearing on it, any N/A marks already in `epic.md`, whether the Epic is handed off (a `Tech face:` line under `## External items`), and the next free Question ID.

2. **Walk.** File each existing Question under its one category, as **The 11 categories** says. Then take the 11 categories in order and give each its state, with what it cites. For each gap, draft the Questions that would settle it, one decision each. Each question names people as the **People by role** drafting rule says, never by name, so a pack can quote it word for word. Score them as `capture` does: `Impact` and `Uncertainty` 1 to 3, `Score` their product, a one-line `Score reason` in canonical terms, as the Veneer section of `AGENTS.md` says ("the enabled Epics", never their shown name); a Score of 1 or 2 is `parked`, any other `open`. A Question that an existing one already asks is no gap: cite the existing one.

   Done when: every existing Question bearing on the Epic sits under exactly one category, every one of the 11 categories has a state, and every gap has at least one drafted Question that no existing Question repeats and that names no person by name.

3. **Propose** under the heading "Decision coverage: <shown name for Epic> <ID> <title>":
   1. **The checklist**: a table of all 11 categories in order, with columns `#`, `Category`, `State` and `Cites`. For a gap, `Cites` names the batch items that raise it; for a category that looks N/A, the state says "gap, looks N/A" with the reason in a short clause of your own, for example "gap, looks N/A: every refund follows the same steps". For Quality, a line under the table gives each characteristic's state.
   2. **The batch**, numbered so the Operator can amend by number:
      - Each gap Question: its ID, its category, the question, and its proposed scores and reason. It is written as `questions/<ID>-<slug>.md` from the `capture` skill's [question template](../capture/templates/question.md), with `Category: <the category's name exactly as in the list above, and nothing more>` (a Quality Question names its characteristic in the question itself, so its line is `Category: Quality`), `Needed by: <Epic ID>`, `Affects: <Epic ID>` plus the Requirement IDs it bears on, `Building on a guess: yes` when the Epic is handed off and `no` otherwise, and `Raised from: Decision coverage of <Epic ID>`.
      - Each N/A the Operator has given a reason for: the line it adds to `epic.md`, in place of that category's gap Question.
      - `questions/index.md`: each new row in its rank order.
      - Log entry `## [<date>] pack | Decision coverage <Epic ID> <title>`, one line per file written and the IDs raised, in canonical terms as **Log** in `AGENTS.md` says.
      - One commit.

   When nothing is a gap, there is no batch: show the checklist, say coverage is complete, and write nothing. Otherwise end with the ask for a reason for each category that looks N/A, then "Nothing is written yet."

   Done when: the checklist shows all 11 categories, and every gap is either a batch item or an N/A mark with the Operator's reason.

4. **Amend, confirm, write, log, commit** as `AGENTS.md` says, showing the checklist and the batch again in full after each amend, numbering the items afresh and holding each proposed ID as `AGENTS.md`'s **Amend** step says. When the Operator's reply answers a gap, keep its Question and add their words as its Answer by **Embedded Capture** in the `capture` skill.
   - An N/A mark is a line under `## Not applicable` in `epic.md`, in the shape [the Epic template](../slice/templates/epic.md) gives. Make the section the first time, after every other section, and add nothing else to `epic.md`. A handed-off Epic's `epic.md` takes N/A marks too, for its next pack version; the rest of it stays byte for byte. Taking a mark back strikes its line through, as the Records rule in `AGENTS.md` says for a withdrawn line, and the category is a gap again.

   Done when: one commit whose message is the log heading; `git diff --name-only HEAD~1` lists only files the batch named; every new Question file has a `Category:` line and a row in `questions/index.md`; and `epic.md` lost no line: `git diff --numstat HEAD~1 -- projects/<slug>/epics/ | cut -f2 | sort -u` prints `0` or nothing (a taken-back mark is the one exception: its line is replaced by the struck-through one).

5. **Hand on.** Say which categories are still open, point at `up-next` for what to chase first, and say the pack comes next ("write the pack for <shown name for Epic> <ID>"). Done when: the Operator has been told.

## Pack

Writes `epics/<ID>-<slug>/pack-v<N>.md` from [the pack template](templates/pack.md): the Epic's business half of the engineers' spec. A pack is **frozen**: once written it is never edited, and a new version is a new file, N one more than the highest `pack-v*.md` in the Epic's folder (1 when there is none). A new version is written only when the Operator asks for it. For a handed-off Epic, writing one is also its next Handoff: the same commit moves the `Tech face:` line to the new version, as the `handoff` skill's Record does.

1. **Gather** as Coverage step 1, and also: the People table in `project.md`; the Epic's `signoffs.md`, if it exists; the `pack-v*.md` names in its folder; any `Pain point:` line in `epic.md`; other Epics in the same Feature (`grep -lx 'Feature: <Feature ID>' projects/<slug>/epics/*/epic.md`); the title of each Technical Enabler under `## Depends on`; and each cited Source's `Kind:`, `URL:`, `Owner:` and `Date:`.

   **Too big**: an Epic covering more than 50 Requirements is certain to give a pack over 300 lines, with no need to draft it. Stop here, as step 3 says for a draft over 300 lines, giving the number of Requirements in place of a line count.

   Done when: you hold what Coverage step 1 names, plus the People, Sign-offs, the next version number and the pain points above.

2. **Walk** as Coverage step 2. Done when: Coverage step 2's criterion holds.

3. **Draft** the pack in your own working, writing no file, as it will read once the batch is written: each gap Question exists with its new ID, and each N/A mark the Operator has given is in place. Fill [the template](templates/pack.md) section by section, by the **Drafting rules** below. Then run the **pack shape scan** on it, writing no file: `python3 <skills>/pack/scripts/pack_shape.py <<'PACK'`, the draft, then `PACK` alone on the last line. It prints `<count> lines` for a good draft. Otherwise it names one problem per line: a section `missing`, `out of order`, `repeated` or `not a pack section`, or the draft `over 300 lines`. Fix the draft's sections and run it again, until it prints `<count> lines` or names only the cap.

   **Over 300 lines** (the scan names the cap): packs are never split. Write nothing and propose no batch. Say the pack would be <count> lines, over the 300-line cap, and propose a re-slice: a seam that would cut the Feature into two vertical Features, each small enough for one pack, naming the Requirements on each side, and that `slice` makes it ("re-slice <Feature ID>"). This ends the operation.

   Done when: the draft has every template section in order, each covered active Requirement has its section 4 entry, every `open` or `chasing` Question bearing on the Epic is a `DO NOT DECIDE` item in section 5, the scan's last run on this draft printed `<count> lines` (or you stopped), and the **Enabler Stories** trace check, run on the draft the same way (`<<'PACK'`), prints `0`.

4. **Propose** under the heading "<shown name for Epic pack> v<N>: <shown name for Epic> <ID> <title>": the coverage checklist as Coverage step 3 shows it, then the numbered batch:
   - each gap Question and each N/A mark, as in Coverage step 3;
   - `epics/<ID>-<slug>/pack-v<N>.md`, <count> lines: one line per section saying what it carries (the IDs, and "Not stated yet" where the records say nothing);
   - for a handed-off Epic, `epic.md`: its `Tech face:` line in the shape the `handoff` skill gives, with the same work item, now naming `pack-v<N>.md` and today, shown in full;
   - `index.md`: one link line for `pack-v<N>.md`, shown in full. It is a record line, so it keeps this exact canonical wording whatever shown names the rest of the proposal uses:
     - v1: `  - [pack-v1.md](epics/<ID>-<slug>/pack-v1.md): first pack, written <today>`
     - a later version: `  - [pack-v<N>.md](epics/<ID>-<slug>/pack-v<N>.md): replaces pack-v<N-1>.md, written <today>`

     It goes under the Epic's line, after its last pack link line, or first under the Epic's line when there is none. Every earlier pack's link line stays as it is;
   - `questions/index.md`: each new row in its rank order;
   - log entry `## [<date>] pack | <Epic ID> <title> pack v<N>`, one line per file written and the IDs raised, in canonical terms as **Log** in `AGENTS.md` says;
   - one commit.

   End with the ask for a reason for each category that looks N/A, then "Nothing is written yet."

   Done when: the checklist shows all 11 categories, every gap is a batch item, and the pack is an item with its line count.

5. **Amend, confirm, write, log, commit** as Coverage step 4. After each amend, draft again and run the scan on it as step 3 says, and show the checklist and the batch again in full. On the yes, write the pack exactly as last drafted, its link line in `index.md`, and for a handed-off Epic its new `Tech face:` line.

   Done when: Coverage step 4's criterion holds (for a handed-off Epic, the `Tech face:` line is the one more line replaced in `epic.md`, and `grep -c 'Pack: pack-v<N>.md'` on it prints `1`); `git diff --numstat HEAD~1 -- projects/<slug>/index.md | cut -f1,2` prints `1	0` and the added line names `pack-v<N>.md` (`git diff HEAD~1 -- projects/<slug>/index.md | grep '^+ ' | grep -c 'pack-v<N>.md'` prints `1`); and in that commit `pack-v<N>.md` is the one pack file added and none changed (`git diff --name-status HEAD~1 -- 'projects/<slug>/epics/*/pack-v*.md'` prints one `A` line), `python3 <skills>/pack/scripts/pack_shape.py <the pack file>` prints `<count> lines`, `grep -c '<CODE>-SRC-'` on it prints `0`, and the **Enabler Stories** trace check on it prints `0`.

6. **Hand on.** Say how many `DO NOT DECIDE` items the pack carries and point at `up-next` for what to chase first. For a handed-off Epic, say the `Tech face:` line now gives the delivery team v<N>, and that they should be told so on that work item. Say each Stakeholder's <shown name for Sign-off view> comes next ("sign-off view for <person>, <shown name for Epic> <ID>"). Done when: the Operator has been told.

### Drafting rules

- **IDs in full**, every one, everywhere in the pack: no ranges.
- **Shown names.** The pack is read outside the Workspace: every Delivery term in it is its Veneer shown name, the template's `{Term}` slots included. A term the Veneer gives no shown name shows as its canonical term, never as another term's shown name. Epic pack shows as its own shown name, or else as "<shown name for Epic> pack". IDs, file names, `DO NOT DECIDE` and the shape labels inside the code blocks stay exactly as the template writes them.
- **Records only.** Every line says what the records say. Where they say nothing (a non-goal, an outcome), write "Not stated yet." A worked example uses the rules' own numbers and is marked "worked from the rules, not yet agreed", unless a Source or Answer holds that case.
- **People by role**, never by name: their `Role` from People, with its `Notes` when there are any ("Stakeholder, hall committee chair"); the Operator is "the Operator". Someone not in People is named by the role their Source gives them.
- **No Source IDs.** A Requirement's `From:` is the link to its Confluence page or Jira item (from `URL:`), else its Source's owner by role and date; one created by an Answer cites that Answer's ID.
- **Settled Decisions** are the active Answers of `Kind: decision` whose Question's `Affects:` names the Epic, its Feature or a covered Requirement, or that created a covered Requirement, leaving out a Technical Enabler's own (its Question names a Technical Enabler other than this Epic). Answers of `Kind: fact` go under their Requirement in section 4.
- **Agreed by**: one line under a Decision for each `signoffs.md` entry whose `Agreed:` line names that Answer ID, giving the Stakeholder's role and the entry's date. A Decision with none has no Agreed by line. The header's Sign-off row counts the Decisions with at least one.
- **Section 7**: a line naming a Technical Enabler reads `- <shown name for Technical Enabler> <ID> <title>: must be built first.` and says nothing more of it: no Handoff state, none of its Questions. With no shown name for Technical Enabler, it is `- Technical Enabler <ID> <title>: must be built first.`, as **Shown names** says, never the shown name for Epic.
- **Enabler Stories** stay in `epic.md`, for the engineers. The pack says what the Requirements, Questions and Answers say, so every Enabler Story the Epic holds is **traceless** in it: no `<CODE>-ENS-` ID, no term (canonical or shown name), no title (the plain words after the bold ID on its line, up to ` · `), and nothing of what it does. The **trace check** catches the ID, term and title: `grep -ciF -e '<CODE>-ENS-' -e 'enabler stor'`, plus `-e '<shown name for Enabler Story>'` when the Veneer gives one and `-e '<first five words of its title>'` per Enabler Story, prints `0` on the pack. Catch what it does by reading the draft against those records.
- **Section 5** lists the `open` and `chasing` Questions bearing on the Epic in `questions/index.md` rank order, building on a guess first. Parked ones go only on its Parked line.
- **Appendix A** is the checklist as it will stand after the write, each N/A row with the Operator's reason. **Appendix B** lists each pain point: the Questions built on a guess (one line for each guess the records name, then one line listing the rest), the Epic's `Pain point:` line, another Epic in the same Feature besides a Technical Enabler, a Decision owned by an engineer ("decided during build"), and a Decision resting on a third-party Source with no URL; or "None."
