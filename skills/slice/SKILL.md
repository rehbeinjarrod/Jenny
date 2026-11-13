---
name: slice
description: Group a Project's Requirements into Features, each with one Epic. Use for `/slice`, when the Operator says "slice the project" or "re-slice <Feature>", or asks which Requirements are unplaced.
---

# Slice

Two operations: **Unplaced**, which writes nothing, and **Slice**, one confirm-then-write operation following the rules in the Tool-owned block of `AGENTS.md`. Every reply uses Veneer names. Today is `date +%F`.

## Words used here

- **Vertical**: a Feature is vertical when a Stakeholder could see it working and sign it off on its own: a hirer books, the caretaker gets a list. Its description says what someone can do or see once it is delivered.
- **Horizontal**: a Feature that is only a layer, platform, quality or technical part running across other Features (works on phones, a database, all the emails), with no outcome a Stakeholder sees on its own. A horizontal Feature is a **pain point**.
- **Covers**: the Requirements an Epic delivers. Each Requirement is covered by exactly one Epic at most, the one the Operator picks as delivering it first. Another Epic that must obey it lists it under **Applies here too**; another Epic that needs it built first lists it under **Depends on**. When two Epics each need part of a Requirement, propose splitting it: its line stays in place, struck through as `AGENTS.md` says for a withdrawn line, and two new Requirements with new IDs and the same `Source:` take its place.
- **Second Epic**: a Feature normally has exactly one Epic. A second one in the same Feature is a **pain point**.
- **Pain point**: a horizontal Feature or a second Epic. Jenny keeps one out of the proposal until the Operator gives a reason for it, and suggests a re-slice in its place. One kept with a reason is recorded as a `Pain point:` line in its `epic.md` header.
- **Handed off**: an Epic whose `epic.md` has a `Tech face:` line under `## External items`. Its `epic.md` stays as it is, byte for byte, because engineers are building from its pack. A new Requirement that belongs to its Feature stays unplaced, waiting for that Epic's next pack version, unless the Operator wants a second Epic.

## Unplaced

Runs when the Operator asks what is unplaced, or what has not been sliced yet.

Find the one Project as the Lookup rules say. Read `requirements/unplaced.md` and list each active Requirement on its own line: `` `<ID>` `` and its statement in a few words. Then offer to slice them. An empty list says "Every active Requirement is in a Feature." The list is read-only.

Done when: every active Requirement in `requirements/unplaced.md` is listed, or the reply says there are none. Nothing is written.

## Slice

Runs on "slice <Project>" (the whole Project) or "re-slice <Feature>" (that Feature and its Epics, plus any unplaced Requirement that belongs with it). A re-slice may also move a placed Requirement to another Feature or a new one: its line moves byte for byte, and its Covers entry moves to that Feature's Epic. A Requirement covered by a handed-off Epic stays where it is.

1. **Gather.** Find the one Project as the Lookup rules say, and work in its folder only. Read `index.md`, `features/index.md`, every `features/*.md`, `requirements/unplaced.md`, and every `epics/*/epic.md`. Note the highest `-FEA-`, `-EPC-` and `-REQ-` number used anywhere in the Project (`grep -rhoE '<CODE>-(FEA|EPC|REQ)-[0-9]{3}' projects/<slug>/ | sort -u`); new IDs follow on from it.

   Done when: you hold every active Requirement with where it sits now (a Feature or unplaced), every Feature with its Epics, which Epics are handed off, and the list of Features that have no Epic yet.

2. **Group.** Work out the Features and Epics, in this order:
   1. Each unplaced active Requirement goes into an existing Feature where it belongs with what is there, or into a new vertical Feature with others that deliver one outcome together. One that belongs to a handed-off Epic's Feature stays unplaced (see **Handed off**). One that fits nowhere yet stays unplaced, with the reason.
   2. A Requirement that runs across several Features (it applies to every page, every email, every booking) goes into one Feature whose Epic is not handed off, and is covered by that Epic: propose the one that delivers it first, and the Operator picks. Every other Epic it bears on lists it under **Applies here too**. It sits in a vertical Feature like any other Requirement.
   3. Every Feature with no Epic, existing Features included, gets exactly one, covering every active Requirement in that Feature. Withdrawn Requirements are never covered.
   4. Check the grouping: every active Requirement in exactly one Feature (the cross-cutting one too, in the Feature whose Epic covers it) or unplaced with a reason, each covered by at most one Epic, each Epic covering only Requirements of its own Feature, every Feature with exactly one Epic (the list from Gather is now empty).

   When the Operator asks for a horizontal Feature or a second Epic, it is a pain point: leave it out of the grouping until they give a reason, then add it. When they ask for a Requirement in two Epics, suggest **Applies here too**, **Depends on** or a split instead.

   Done when: the grouping passes the check in item 4, and every pain point the Operator asked for has a suggested re-slice and either a reason from the Operator or a request for one.

3. **Propose** under the heading "Slice <shown name for Project> <Name>" (or "Re-slice <Feature ID> <title>"):
   1. Each new Feature: `features/<ID>-<slug>.md` from [templates/feature.md](templates/feature.md): its title, its one-line description, and the Requirement IDs moving into it.
   2. Each existing Feature that gains Requirements: the IDs moving in.
   3. `requirements/unplaced.md`: the IDs moving out, and each that stays with its reason. When none stay, its list becomes `None.`
   4. Each new Epic: `epics/<ID>-<slug>/epic.md` from [templates/epic.md](templates/epic.md), for which Feature (one for each Feature that had none, existing ones included), with its Covers, Applies here too, Depends on and Left out. For a cross-cutting Requirement, say which Epic covers it and that the Operator can pick another.
   5. Each existing Epic that changes, handed-off ones aside: what changes.
   6. `features/index.md`: a row per new Feature, and each changed row's Requirements. `index.md`: a link line per new Epic, in the shape of the ones there.
   7. Log entry `## [<date>] slice | <Features and Epics written, by ID and title>`, one line per file written and one for the Requirements moved.
   8. One commit.

   Then **Pain points**: each one the Operator asked for, named horizontal or second <shown name for Epic>, as one item in this shape, the three labels exactly as written:

   ```markdown
   1. **<what it is: a horizontal Feature for `<ID>`, or a second <shown name for Epic> in `<Feature ID>`>**
      - Why it is a pain point: <in plain words>
      - Suggested re-slice: <how you would slice it instead>
      - Reason: <the Operator's reason, or "waiting for your reason">
   ```

   Leave the section out when there are none. Then "Nothing is written yet."

   Done when: the batch is shown, ending with "Nothing is written yet."

4. **Amend, confirm, write, log, commit** as `AGENTS.md` says. A pain point still waiting for a reason when the Operator says yes: ask for it, or for the suggested re-slice, before writing anything.
   - A Requirement line moves byte for byte: cut it from where it was and paste it under `## Requirements` in its Feature.
   - A pain point kept with a reason gets `Pain point: <second Epic in <Feature ID> | horizontal Feature>: <the Operator's reason>` in its `epic.md` header, after `Feature:`. Every other `epic.md` leaves the line out.
   - `epic.md` has no status line: an Epic's state comes from which files exist.

   Done when: one commit whose message is the log heading; every Requirement line is still there, each in exactly one Feature file or `requirements/unplaced.md`, byte for byte: `diff <(git grep -h '^- \*\*<CODE>-REQ-' HEAD~1 -- projects/<slug>/features projects/<slug>/requirements | sort) <(grep -rh '^- \*\*<CODE>-REQ-' projects/<slug>/features projects/<slug>/requirements | sort)` prints nothing, or only a split's old line and its two new lines; and no Requirement is covered twice: `awk 'FNR==1{s=0} /^## /{s=($0=="## Covers")} s' projects/<slug>/epics/*/epic.md | grep -oE '<CODE>-REQ-[0-9]{3}' | sort | uniq -d` prints nothing.

5. **Hand on.** Say that each new Epic is ready for Decision coverage in `pack`, naming the first by ID. Done when: the Operator has been told.
