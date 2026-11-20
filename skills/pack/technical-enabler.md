# Pack: a Technical Enabler

Part of Pack, read when [SKILL.md](SKILL.md) sends you here. A section named in bold (**The 11 categories**, **Coverage**, **Pack**, **Drafting rules**) is in SKILL.md, and each stands, the pack shape scan included, except where this file says otherwise.

The Technical Enabler's **Enabled Requirements** are the Requirement IDs on its `Enables:` line.

## Gather

- Read each Enabled Requirement in its Feature file, and find the Epic delivering it: the one whose `## Covers` holds its ID (`awk 'FNR==1{s=0} /^## /{s=($0=="## Covers")} s{print FILENAME": "$0}' projects/<slug>/epics/*/epic.md | grep '<REQ ID>'`), or "not sliced yet" when none does.
- The Enabled Requirements are **context only**: they settle no category, and Questions or Answers bearing on them bear on the Epics that deliver them.
- A Question bears on the Technical Enabler only when its `Affects:` or `Needed by:` names the Technical Enabler's ID. Its settled Decisions are the active `Kind: decision` Answers to those Questions.

Done when: you hold each Enabled Requirement word for word with its delivering Epic ID or "not sliced yet", and the Questions naming the Technical Enabler, besides what Coverage step 1 names.

## Walk and the shared N/A

Walk all 11 categories, each settled only by the Technical Enabler's own Answers and Applies-here-too Requirements. A gap gets its drafted Question as usual, with `Affects:` naming the Technical Enabler's ID first.

When several gaps look N/A for one reason (for example, "its business rules live in the Epics it enables"), propose that one **shared N/A** reason once, naming each category it covers, under the checklist; each of those categories still shows "gap, looks N/A" and its gap Question stays in the batch until the Operator answers. The Operator takes the reason, or changes its words or its categories, in one reply. On the yes, the shared reason becomes one batch item: a line under `## Not applicable` for each category it covers, each in the template's shape with the same reason and date, written in the one commit, and those categories' gap Questions leave the batch.

Done when: every category has a state settled by the Technical Enabler's own records or none, and each shared N/A the Operator took is one batch item holding a line for each category it covers.

## Sections 4 and 9

Section 4 lists each Enabled Requirement, in `Enables:` order, in this shape and nothing more (no From line, Answers, examples or Questions under it):

```markdown
### <CODE>-REQ-<nnn> <a short title in your own words>

> <the Requirement, word for word>

- Delivered by: <CODE>-EPC-<nnn> | not sliced yet
```

`not sliced yet` is what the records say when no Epic covers the Requirement, so its line reads `- Delivered by: not sliced yet`, word for word.

Section 9 has one criterion per settled Decision, citing its Answer ID, then one per Enabled Requirement saying what becomes possible once the Technical Enabler is built, citing the Requirement ID, for example "A booking can be paid in full by card (CRT-REQ-001)".

Done when: section 4 holds every Enabled Requirement in that shape and no other `###` entry, and section 9 holds a criterion for every settled Decision and every Enabled Requirement.
