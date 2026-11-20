# Capture: story map sessions

Part of Capture, read when [SKILL.md](SKILL.md) sends you here. A section named in bold (**1. Find the Project**, **2. Read the material into candidates**, **3. Propose**) is in SKILL.md.

A story mapping session's wall comes into Jenny as one Capture: a Source, Requirements, the Project's `storymap.md`, a Milestone record per release line, and Questions. The map holds Requirement IDs only, never card text of its own.

## The paste template

When the Operator asks for the paste template, show [templates/storymap-session.md](templates/storymap-session.md) in one code block for them to fill in and paste back, with these rules in a few plain lines under it, and write nothing:

- Activities and steps go in the wall's order, left to right; cards go top card first under their step.
- A `--- <name>` line sits under the cards it releases, the way the line runs across the wall; every card sits above a release line.
- `@<user group>` names who a card is for; `[enabler]` marks an engineer's card.
- Each release line is listed once at the end, top first, with its outcome, metric and target where known. `Walking skeleton (<user group>)` marks a Walking skeleton.

## Reading the session

Read the pasted template this way:

- **Card**: each `- ` line under a step. It belongs to the first `--- <name>` line below it in its step, and its rank is its place in that band, top first.
- **Enabler**: a card tagged `[enabler]`. It is held on the map under `## Enablers`, never made a Requirement.
- **Release line**: each `--- <name>`, in the order the end list gives. A name starting `Walking skeleton` is an internal Milestone for the user group it names.
- **Engineers' notes**: each risky area and each technology idea becomes a Question.
- **Estimates**: a size or time on a card (`(3 days)`, points, T-shirt sizes) is left out of every record but the Source, and named in the "not used" line.

**Looser text.** Material said to come from a story mapping session that is not in the template's shape is read the same way, once its gaps are filled. Before any batch, ask about each gap in one numbered list, and propose nothing until the Operator answers:

- the order of activities, steps or cards, where the text does not make it plain;
- each card with no release line, naming the card;
- a release line with no name, and which cards an enabler serves when the text does not say;
- which user group a card is for, when the text does not say.

The Operator's answers in chat are part of the material: the Source keeps them word for word after the session text, under the line `Answers given in chat:`.

## A Miro card list

A Miro CSV export (a row per item: text, description, tags) or text copied from a Miro board (a line per item) is an unordered card list. Miro keeps no position, frame or colour, so each card's step, rank and release line are lost; the Operator gives them back by slotting each card into the paste template.

- **Say so first**, in one plain line: Miro does not keep the board's order, so every card needs a place.
- **Cards**: each row's text, or each copied line, is a card, read with its description. A tag named `enabler` makes the card `[enabler]`; a tag naming a user group gives its `@<user group>`.
- **Slotting**: show the template in one code block holding only what the Operator has said, with every other card listed at its foot under `Not placed yet:`, and the cards the Operator leaves out under `Set aside:`. Under it, ask about the gaps as **Looser text** says, plus which cards are activities and steps. A step a card's text plainly fits may be suggested in a question; the card stays under `Not placed yet:` until the Operator places it.
- **Each answer** shows the template again with the questions left.
- **Propose nothing** while any card is under `Not placed yet:`. Then show the filled template and the batch in the same reply. The Source keeps the filled template word for word, then the list as given under the line `Miro card list as given:`.
- **The batch shows the template again**: the reply that ends the slotting holds the whole filled template, `[enabler]` tags and `Set aside:` included, in its own code block, even when the last reply showed nearly the same one. Never point back to an earlier reply ("as shown in my last reply"): item 1 shows the exact text the Source keeps.

## The batch

The batch is shown as **3. Propose** says, under `Capture: Story map session of <date>`, with these items in this order:

- **Item 1, the Source**: `Kind: story map session`, owned by the Operator unless they say whose it is, the whole session kept word for word, and shown in full in this reply.
- **One item per card**, labelled as **2. Read the material into candidates** says. The map places each card by the ID the label gives it: a **new** card by its new ID, a **duplicate** by the existing ID, a **refines** by the replacement's ID, a **conflicts** by the existing ID, which stays active while its Question is open. Two cards that say the same thing are one Requirement, placed once at the higher-ranked card.
- **The map**: `storymap.md` in full for a first session, from [templates/storymap.md](templates/storymap.md), or the changes to it for a later one (below).
- **One item per Milestone**, top release line first: `milestones/<CODE>-MIL-<nnn>-<slug>.md` from [templates/milestone.md](templates/milestone.md).
- **Questions**: as **2. Read the material into candidates** shapes them, raised from the session's Source.
  - A Milestone missing its outcome, success metric or target gets one Question for the business owner naming each missing part, with `Affects:` and `Needed by:` the Milestone's ID. A Walking skeleton too.
  - Each risky area and each technology idea gets a Question, with `Affects:` only the Requirements its cards became; the Milestone it bears on goes in `Needed by:`.
- **The last item, indexes and log**, with a link line in the Project's `index.md`, `- [storymap.md](storymap.md): the story map, with its Milestones in [milestones/](milestones/)`, the first time.

## The map

- **Headings**: one `## <Activity>` per activity and one `### <Step>` per step under it, in the session's order. `## Enablers` and `## Not on the map` follow the last activity.
- **Card lines**: under each step, one line per Milestone that has cards there, in release order: `- <CODE>-MIL-<nnn>: <CODE>-REQ-<nnn> (<user group>), …`, the IDs in rank order.
- **Enablers**: `- **<card text>** · Kind: <kind> · Enables: <IDs> · Depends on: <names>`, with no ID. `Enables:` is the Requirements of the business cards in the enabler's step, in its release band and the bands below it, unless the session says which. Propose the kind from that: **Technical Enabler** when it enables cards in more than one band or step, **Enabler Story** when they all sit in one band of one step; `Depends on:` names other enablers the session says come first, or `none`. With no enablers the section reads `None.`
- **Not on the map** reads `None.` after a first session, even when the Project has active Requirements no card holds. The section is for Requirements captured after the map exists (SKILL.md, **Story map**) and cards a later session takes off the wall; slice counts a Requirement on no card line as not on the map either way.

## Milestones

One record per release line, numbered in release order. A `Walking skeleton (<user group>)` line's record is an internal Milestone (`Internal: yes`), and there is one per user group:

- `Outcome:` and `Success metric:` as the session gives them, or `not given yet; asked in <Question ID>`.
- `Target:` is `<YYYY-MM-DD> set by <name>` when a named Stakeholder set it (propose adding them to People as a Stakeholder first when they are not there), or `none` when someone else gave the date: then the Milestone's Question asks the business owner to set it. `derived from plan-v<N>` is written only by planning, never at capture.
- `## Members` reads `Not sliced yet.`

## A later session

A later session is a new Source whose batch amends the living map, item by item:

- `Sources:` gains the new Source ID, and the brief changes only when the session changes it.
- New activities, steps and card lines go in their places; a card moved to another release line moves its ID to that Milestone's line.
- A Requirement under `## Not on the map` that the session places moves onto the map.
- A card taken off the wall moves its ID to `## Not on the map`; the Requirement stays active.
- A new release line is a new Milestone. A changed outcome, metric or target edits that Milestone's line, shown in its item as old → new.
- Enablers are matched by name: a new one is added, a changed one edited.

Done when: the template is shown and nothing written, or every gap in looser text is asked about before any batch, or every card of a Miro card list is placed or set aside before any batch; and the batch places every card on the map by an ID, holds one Milestone per release line, and raises a Question for each missing Milestone part, risky area and technology idea.
