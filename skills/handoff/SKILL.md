---
name: handoff
description: Record the Handoff of an Epic pack version to the delivery team, or report what has changed since an Epic was handed off. Use for `/handoff`, when the Operator says "hand off <Epic> v<N>, tech face <Jira key>", or asks "what's changed since handoff?" on an Epic.
---

# Handoff

A Handoff is one line under `## External items` in the Epic's `epic.md`: the engineers' own Jira work item (the **tech face**) and the pack version they were given. It is the only record of a Handoff; there is no status field.

```
- Tech face: [<Jira key>](<URL>) · Pack: pack-v<N>.md · Handed off: <YYYY-MM-DD>
```

Two operations:

- **Record** on "hand off <Epic> v<N>, tech face <Jira key or URL>", and on `/handoff` naming a version. A confirm-then-write operation following the rules in the Tool-owned block of `AGENTS.md`.
- **Drift** on "what's changed since handoff?" and on `/handoff` alone. A report that writes nothing: no file, no log entry, no commit.

Today is `date +%F`.

## Record

1. **Gather.** Find the one Project and Epic as the Lookup rules say, asking when two could fit. Work in that Project's folder only. Read the Epic's `epic.md`, the `pack-v*.md` names in its folder, and the Project's `index.md`.
   - **The version** must be a written pack: `pack-v<N>.md` in the Epic's folder. With none, stop and say the pack comes first ("write the pack for <shown name for Epic> <ID>"). When a higher version than the one given exists, say so in the proposal.
   - **The tech face** is a Jira work item. Given a URL, use it, and its key is the last part of the path. Given a key alone, build the URL from the Jira site the Project already links to: `grep -rhoE 'https://[^/ )]+/browse/' projects/<slug>/ | sort -u`. One site: `<site>/browse/<key>`. None or several: ask the Operator for the link.
   - **Already handed off**: a `Tech face:` line exists. The new line replaces it. When the version given is lower than the one it names, ask whether the delivery team is really going back to it. When both the version and the work item match, there is nothing to record: say so and stop.

   Done when: you hold the Epic, a written pack version, the work item's key and URL, and the `Tech face:` line it replaces, if any.

2. **Propose** under the heading "<shown name for Handoff>: <shown name for Epic> <ID> <title>, v<N>", as a numbered batch:
   1. `epics/<ID>-<slug>/epic.md`: the `Tech face:` line as it will read, in a code span, and what it replaces: the old `Tech face:` line, or `None yet.` under `## External items`. Every other line of `epic.md` stays byte for byte.
   2. `index.md`: when the Epic's line does not already say "handed off", `, handed off` added to its end. Otherwise no change, and no item.
   3. Log entry `## [<date>] handoff | <Epic ID> pack v<N> to the delivery team`, one line per file written.
   4. One commit.

   Then a short line saying the delivery team should be told on the work item that v<N> is the one to build from, then "Nothing is written yet."

   Done when: the batch shows the `Tech face:` line in full and what it replaces.

3. **Amend, confirm, write, log, commit** as `AGENTS.md` says.

   Done when: one commit whose message is the log heading, changing only `epic.md`, `index.md` and the log; `git diff --numstat HEAD~1 -- projects/<slug>/epics/` prints `1	1` for `epic.md` alone; and `grep -c 'Tech face:'` on `epic.md` prints `1`.

4. **Hand on.** Say the delivery team builds from v<N>, that the engineers post what they need from the business on that work item, each as a `Business question`, and "check <Jira key>" reads them, and that "what's changed since handoff?" reports drift from v<N>. Done when: the Operator has been told.

## Drift

Drift is the difference between the frozen pack the delivery team holds and the records now. Work it out by comparing that pack with the records, item by item, as below.

1. **Gather.** Find the one Project and Epic as the Lookup rules say. Read `epic.md`. With no `Tech face:` line, the Epic is not handed off: say so, say how to record one ("hand off <shown name for Epic> <ID> v<N>, tech face <key>"), and stop. Otherwise read:
   - the **handed-off pack**: the `pack-v<N>.md` its `Tech face:` line names, and the `Handed off:` date;
   - for a Technical Enabler (`Technical Enabler: yes`), the Requirements it enables: each one in its `Enables:` line or under a `###` heading in the pack's section 4, read from the file that holds it (a Feature file or `requirements/unplaced.md`);
   - the Epic's Feature file, `questions/index.md`, and every Question file whose `Affects:` or `Needed by:` names the Epic, its Feature, a Requirement under **Covers** or **Applies here too**, or an Answer to one of them. For a Technical Enabler, every Question file whose `Affects:` or `Needed by:` names the Technical Enabler itself, and no other, as its pack does;
   - `signoffs.md`, if it exists;
   - the other `pack-v*.md` names in the Epic's folder, and the `Version` row of any higher one.

   Done when: you hold the handed-off pack, the records bearing on the Epic now, and any newer pack's version and date.

2. **Compare.** Take each kind in turn. A record that bears on another Feature's Epic is no drift here.
   - **Decisions**: active `Kind: decision` Answers bearing on the Epic that are not in the pack's section 3; and section 3 Decisions now withdrawn, with what replaced them. A Decision whose owner has the People role `engineer` is a **build Decision**: say "decided during build".
   - **Facts**: active `Kind: fact` Answers bearing on the Epic that the pack does not cite.
   - **Questions**: `open` or `chasing` Questions bearing on the Epic that are not in the pack's section 5, building on a guess first; and section 5 Questions now `answered` or `withdrawn` (one line each, pointing at its Answer above).
   - **Requirements**: active Requirements under **Covers** or **Applies here too** that the pack does not carry, and ones it carries that are now withdrawn, with what replaced them. For a Technical Enabler, the Requirements it enables too, in two passes:
     1. **Withdrawn**: each Requirement section 4 lists that is now withdrawn, saying "replaced by <ID>" from its `Replaced by:`, or "withdrawn, nothing replaces it". Note each replacement ID.
     2. **Newly enabled**: the IDs in `Enables:`, less those section 4 lists, less the replacement IDs noted in pass 1. Each one left says "newly enabled". A replacement already has its line in pass 1, and that is its only line.
   - **N/A marks**: lines under `## Not applicable` in `epic.md` that are not N/A rows in the pack's Appendix A, and marks since struck through.
   - **Sign-offs**: `signoffs.md` entries dated on or after the `Handed off:` date, with the Decisions each agreed, less any agreement the pack already shows as an Agreed by line.
   - **Newer pack**: each `pack-v*.md` above the handed-off version, by version and written date only.

   Done when: every kind has its list, or none.

3. **Report**, writing nothing:
   1. One headline: "Engineers have v<N> (<tech face key>, handed off <date>); since then: <counts>", counting each kind that changed (for example "2 Decisions, 1 of them a build Decision"). With no changes, "nothing has changed since".
   2. Each kind that changed, under its shown name, one line per changed record: its ID in a code span and a few plain words. The report is the delta alone: a record the handed-off pack already carries as it stands now is named nowhere in it, and a kind with no change has no heading. With no changes, the headline is the whole report, before the next step.
   3. The next step:
      - a newer pack exists: say it is written but not handed over, and offer "hand off <shown name for Epic> <ID> v<M>, tech face <key>";
      - otherwise, with changes: when the changes are worth a new version is the Operator's call; "write the pack for <shown name for Epic> <ID>" writes v<N+1>, and writing it moves the `Tech face:` line to that version in the same commit;
      - with no changes: nothing to do.

   Cite only Requirement, Question, Answer, Sign-off and pack IDs and file names, each written in full: no Source ID, no range.

   Done when: the reply has the headline, every changed record and no unchanged one, the next step, and `git status --porcelain` is empty.
