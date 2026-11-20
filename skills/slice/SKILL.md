---
name: slice
description: Group a Project's Requirements into Features, each with one Epic. Use for `/slice`, when the Operator says "slice the project" or "re-slice <Feature>", or asks which Requirements are unplaced.
---

# Slice

Two operations: **Unplaced**, which writes nothing, and **Slice**, one confirm-then-write operation following the rules in the Tool-owned block of `AGENTS.md`. Today is `date +%F`.

## Words used here

- **Vertical**: a Feature is vertical when a Stakeholder could see it working and sign it off on its own: a hirer books, the caretaker gets a list. Its description says what someone can do or see once it is delivered.
- **Horizontal**: a Feature that is only a layer, platform, quality or technical part running across other Features (works on phones, a database, all the emails), with no outcome a Stakeholder sees on its own. A horizontal Feature is a **pain point**.
- **Covers**: the Requirements an Epic delivers. Each Requirement is covered by exactly one Epic at most, the one the Operator picks as delivering it first. Another Epic that must obey it lists it under **Applies here too**; another Epic that needs it built first lists it under **Depends on**. When two Epics each need part of a Requirement, propose splitting it: its line stays in place, struck through as `AGENTS.md` says for a withdrawn line, and two new Requirements with new IDs and the same `Source:` take its place.
- **Second Epic**: a Feature normally has exactly one Epic. A second one in the same Feature is a **pain point**, unless it is a Technical Enabler.
- **Enabler**: engineers' enabling work. *Mapped*, each line under `## Enablers` in `storymap.md` is a **pending enabler**, with a name and no ID. A slice turns it into one of two things, as its `Kind:` says unless the Operator picks the other:
  - **Technical Enabler**: an Epic of its own, `epic.md` from the template with `Technical Enabler: yes` and `Enables: <Requirement IDs>` after `Feature:`, and `## Covers` reading `None.` It belongs to the Feature that needs it first: *mapped*, the one holding an enabled Requirement in the earliest Milestone; otherwise propose one, and the Operator picks. Every other Epic covering a Requirement it enables lists it under **Depends on**. A Technical Enabler that enables no Requirement is a **pain point**.
  - **Enabler Story**: a line under `## Enabler Stories` (made after `## Depends on` the first time) in the `epic.md` of the Epic covering the Requirements it enables (the first to need it, when several do): `- **<CODE>-ENS-<nnn>** <name> · Enables: <Requirement IDs | none> · Depends on: <Enabler Story or Epic IDs | none>`.

  `Enables:` comes from the map's line; with no map, or `Enables: none` there, ask the Operator which Requirements it enables. `Depends on:` turns the map's enabler names into the IDs they become. The Operator can ask for either on a Project with no map, and the same rules apply.
- **Pain point**: a horizontal Feature, a second Epic, or a Technical Enabler enabling no Requirement. Jenny keeps one out of the proposal until the Operator gives a reason for it, and suggests a re-slice in its place. One kept with a reason is recorded as a `Pain point:` line in its `epic.md` header.
- **Mapped**: a Project with a `storymap.md`. A rule marked *mapped* applies only there; a Project with no story map slices without them.
- **A Requirement's Milestone**: the Milestone of the card line it sits on in `storymap.md` (`- <CODE>-MIL-<nnn>: <CODE>-REQ-<nnn> (<user group>), …`). A Requirement under `## Not on the map`, or on no card line, is **not on the map** and has no Milestone.
- **Straddles**: a Feature straddles when its Requirements have two or more Milestones between them. Requirements not on the map never make a Feature straddle.
- **Handed off**: an Epic whose `epic.md` has a `Tech face:` line under `## External items`. Its `epic.md` stays as it is, byte for byte, because engineers are building from its pack. A new Requirement that belongs to its Feature stays unplaced, waiting for that Epic's next pack version, unless the Operator wants a second Epic.

## Unplaced

Runs when the Operator asks what is unplaced, or what has not been sliced yet.

Find the one Project as the Lookup rules say. Read `requirements/unplaced.md` and list each active Requirement on its own line: `` `<ID>` `` and a short title for it in your own words, for example "Refunds over $500 need a manager". Then offer to slice them. An empty list says "Every active Requirement is in a Feature." The list is read-only.

Done when: every active Requirement in `requirements/unplaced.md` is listed, or the reply says there are none. Nothing is written.

## Slice

Runs on "slice <Project>" (the whole Project) or "re-slice <Feature>" (that Feature and its Epics, plus any unplaced Requirement that belongs with it). A re-slice may also move a placed Requirement to another Feature or a new one: its line moves byte for byte, and its Covers entry moves to that Feature's Epic. A Requirement covered by a handed-off Epic stays where it is.

1. **Gather.** Find the one Project as the Lookup rules say, and work in its folder only. Read `index.md`, `features/index.md`, every `features/*.md`, `requirements/unplaced.md`, and every `epics/*/epic.md`. Note the highest `-FEA-`, `-EPC-`, `-REQ-` and `-ENS-` number used anywhere in the Project (`grep -rhoE '<CODE>-(FEA|EPC|REQ|ENS)-[0-9]{3}' projects/<slug>/ | sort -u`); new IDs follow on from it. Build the **no-Epic list** by running this. It prints each Feature ID that no `epic.md` names in its `Feature:` line. Technical Enablers don't count; handed-off Epics do.

   ```sh
   find projects/<slug>/features -name '<CODE>-FEA-*.md' | sed -E 's|.*/(<CODE>-FEA-[0-9]{3}).*|\1|' | sort | while read -r id; do grep -rlx --include=epic.md "Feature: $id" projects/<slug>/epics 2>/dev/null | xargs -r grep -Lx 'Technical Enabler: yes' | grep -q . || echo "$id"; done
   ```

   *Mapped*: also read `storymap.md` and every `milestones/*.md`.

   Done when: you hold every active Requirement with where it sits now (a Feature or unplaced), every Feature with its Epics (which are Technical Enablers too), which Epics are handed off, and the no-Epic list: exactly the Feature IDs that command printed; *mapped*, also each Requirement's Milestone, each Milestone's `## Members`, and each pending enabler.

2. **Group.** Work out the Features and Epics, in this order:
   1. Each unplaced active Requirement goes into an existing Feature where it belongs with what is there, or into a new vertical Feature with others that deliver one outcome together. One that belongs to a handed-off Epic's Feature stays unplaced (see **Handed off**). One that fits nowhere yet stays unplaced, with the reason. *Mapped*: a Requirement joins only a Feature none of whose Requirements is in another Milestone; one not on the map can join any Feature.
   2. A Requirement that runs across several Features (it applies to every page, every email, every booking) goes into one Feature whose Epic is not handed off, and is covered by that Epic: propose the one that delivers it first, and the Operator picks. Every other Epic it bears on lists it under **Applies here too**. It sits in a vertical Feature like any other Requirement.
   3. Every Feature with no Epic, each on the no-Epic list and each new one, gets exactly one, covering every active Requirement in that Feature. Withdrawn Requirements are never covered.
   4. Each pending enabler, and each the Operator asks for, becomes a Technical Enabler or an Enabler Story (see **Enabler**). An Enabler Story whose Epic is handed off, or whose Requirements all stay unplaced, stays on the map with the reason. A handed-off Epic never gains a **Depends on** line: name it as waiting for its next pack version.
   5. Check the grouping: every active Requirement in exactly one Feature (the cross-cutting one too, in the Feature whose Epic covers it) or unplaced with a reason, each covered by at most one Epic, each Epic covering only Requirements of its own Feature, every Feature with exactly one Epic besides its Technical Enablers (each ID on the no-Epic list has a new Epic), each Technical Enabler's enabled Requirements depending on it, and, *mapped*, no new or changed Feature straddles and no pending enabler is left without a reason.

   When the Operator asks for a horizontal Feature, a second Epic, or a Technical Enabler that enables no Requirement, it is a pain point: leave it out of the grouping until they give a reason, then add it. When they ask for a Requirement in two Epics, suggest **Applies here too**, **Depends on** or a split instead.

   *Mapped*: when the Operator asks for a grouping that straddles, leave it out and put its re-slice in the grouping instead: one Feature per Milestone, each holding that Milestone's Requirements. It is not a pain point, and a reason does not keep it: to deliver those Requirements together, the Operator first moves a card to the other Milestone by capturing a later story map session. An existing Feature that already straddles stays as it is unless the Operator asks for its re-slice.

   Done when: the grouping passes the check in item 5, and every pain point the Operator asked for has a suggested re-slice and either a reason from the Operator or a request for one.

3. **Propose** under the heading "Slice <shown name for Project> <Name>" (or "Re-slice <Feature ID> <title>"):
   1. Each new Feature: `features/<ID>-<slug>.md` from [templates/feature.md](templates/feature.md): its title, its one-line description, and the Requirement IDs moving into it.
   2. Each existing Feature that gains Requirements: the IDs moving in.
   3. `requirements/unplaced.md`: the IDs moving out, and each that stays with its reason. When none stay, its list becomes `None.`
   4. Each new Epic: `epics/<ID>-<slug>/epic.md` from [templates/epic.md](templates/epic.md), for which Feature, with its Covers, Applies here too, Depends on, Enabler Stories and Left out. For a cross-cutting Requirement, say which Epic covers it and that the Operator can pick another. Each Technical Enabler says so, with its `Enables:` line and which Epics depend on it. Then **Features with no <shown name for Epic> yet**: each ID on the no-Epic list, then each new Feature, one `- <FEA ID> · <title> → <EPC ID>` line each. Leave the list out when it is empty.
   5. Each existing Epic that changes, handed-off ones aside: what changes.
   6. *Mapped*: each Milestone whose members change: `milestones/<ID>-<slug>.md`, its `## Members` listing every Feature that holds one of its Requirements after the slice, existing Features included, in ID order, one `- <FEA ID> · <Feature title>` line each, in place of `Not sliced yet.` A Milestone none of whose Requirements is in a Feature keeps `Not sliced yet.` And `storymap.md`: each pending enabler leaving `## Enablers`, by name, and what it becomes; with none left the section reads `None.`
   7. `features/index.md`: a row per new Feature, and each changed row's Requirements. `index.md`: a link line per new Epic, in the shape of the ones there.
   8. Log entry `## [<date>] slice | <Features and Epics written, by ID and title>`, one line per file written and one for the Requirements moved.
   9. One commit.

   Then, *mapped*, **Milestone boundary**: each grouping the Operator asked for that straddles, and each existing Feature that straddles, as one item in this shape:

   ```markdown
   1. **<the Feature ID, or the grouping asked for> across `<MIL ID>` and `<MIL ID>`**
      - Requirements: `<REQ ID>` in `<MIL ID>`; `<REQ ID>` in `<MIL ID>`
      - Suggested re-slice: <one Feature per Milestone, as the batch above has it, or would for an existing Feature>
   ```

   And **Not on the map**: a warning naming each active Requirement this slice places or leaves unplaced that is not on the map, `` `<ID>` `` and a short title, saying that no Milestone counts it and that the slice goes ahead all the same; the Operator can map it first by capturing a later story map session. Leave each section out when it has nothing.

   Then **Pain points**: each one the Operator asked for, named horizontal, second <shown name for Epic>, or Technical Enabler enabling no Requirement, as one item in this shape, the three labels exactly as written:

   ```markdown
   1. **<what it is: a horizontal Feature for `<ID>`, a second <shown name for Epic> in `<Feature ID>`, or a Technical Enabler enabling no Requirement>**
      - Why it is a pain point: <in plain words>
      - Suggested re-slice: <how you would slice it instead>
      - Reason: <the Operator's reason, or "waiting for your reason">
   ```

   Leave the section out when there are none. Then "Nothing is written yet."

   Done when: the batch is shown, ending with "Nothing is written yet."; each ID on the no-Epic list, and each new Feature, is named with its new Epic, both as an Epic item and in **Features with no <shown name for Epic> yet**; *mapped*, it names every straddle, every Requirement not on the map that the slice places or leaves unplaced, and what each pending enabler becomes.

4. **Amend, confirm, write, log, commit** as `AGENTS.md` says. A pain point still waiting for a reason when the Operator says yes: ask for it, or for the suggested re-slice, before writing anything.
   - A Requirement line moves byte for byte: cut it from where it was and paste it under `## Requirements` in its Feature.
   - A pain point kept with a reason gets `Pain point: <second Epic in <Feature ID> | horizontal Feature | Technical Enabler enabling no Requirement>: <the Operator's reason>` in its `epic.md` header, after `Feature:` (and a Technical Enabler's lines). Every other `epic.md` leaves the line out.
   - `epic.md` has no status line: an Epic's state comes from which files exist.
   - *Mapped*: each Milestone's `## Members` lists exactly the Features holding its Requirements, as item 6 says. In `storymap.md`, only the converted enablers' lines leave `## Enablers` (`None.` when none is left); nothing else changes.

   Done when: one commit whose message is the log heading; every Requirement line is still there, each in exactly one Feature file or `requirements/unplaced.md`, byte for byte: `diff <(git grep -h '^- \*\*<CODE>-REQ-' HEAD~1 -- projects/<slug>/features projects/<slug>/requirements | sort) <(grep -rh '^- \*\*<CODE>-REQ-' projects/<slug>/features projects/<slug>/requirements | sort)` prints nothing, or only a split's old line and its two new lines; and no Requirement is covered twice: `awk 'FNR==1{s=0} /^## /{s=($0=="## Covers")} s' projects/<slug>/epics/*/epic.md | grep -oE '<CODE>-REQ-[0-9]{3}' | sort | uniq -d` prints nothing; and, *mapped*, no Feature written straddles, each Milestone's members are its Features, and `## Enablers` holds only enablers kept with a reason.

5. **Hand on.** Say that each new Epic is ready for Decision coverage in `pack`, naming the first by ID. Done when: the Operator has been told.
