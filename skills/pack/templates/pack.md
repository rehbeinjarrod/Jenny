# {Epic pack}: <CODE>-EPC-<nnn> <Title> (v<N>)

| | |
| --- | --- |
| {Project} | <CODE> <Project name> |
| {Feature} | <CODE>-FEA-<nnn> <Feature title> |
| {Epic} | <CODE>-EPC-<nnn> <Title> |
| Version | v<N>, written <YYYY-MM-DD> by the Operator<, replacing `pack-v<N-1>.md`; leave out for v1> |
| {Sign-off} | <a> of <d> {Decision}s agreed by a Stakeholder, or none yet |

## For the agent reading this

This {Epic pack} is the business half of the spec for <CODE>-EPC-<nnn>. Use it as settled input to your spec step.

- **Settled {Decision}s are final.** Build on them as written, and keep them closed in grilling and brainstorming. If one looks wrong, post a `Business question` about it.
- **An item marked `DO NOT DECIDE` is a business decision still open.** Build around it if you can, or stop. Either way, post a `Business question` quoting its ID.
- **A business decision this {Epic pack} does not cover** is `DO NOT DECIDE` too: post a `Business question` for each one.
- **A business call made anyway**, by you or your engineer: post a `Business call made in build`.
- People are named here by role. Post either shape as a comment on the work item this {Epic pack} was handed over with, or give it to your engineer to post.
- Stack, commands, repo layout and test seams are not in this {Epic pack}: the repo's `AGENTS.md` and your harness own those.

```text
Business question
IDs touched: <{Requirement}, {Question} and {Answer} IDs>, <CODE>-EPC-<nnn>
Question: <the question, in one sentence>
Options seen: <each option, as a short phrase, e.g. "a manager approves; any staff member can">
Default if forced: <the option you would take, and why>
Status: blocked | building around it (on a guess: <what>)
```

```text
Business call made in build
IDs touched: <{Requirement}, {Question} and {Answer} IDs>, <CODE>-EPC-<nnn>
Decided: <what was decided>
Why: <one line>
Made by: agent | engineer
```

## 1. Problem and outcome

<The problem, in two or three plain sentences from the {Project}'s description and the {Feature}'s.>

**Outcome:** <what changes, for whom, from the {Feature}'s description.>

**Who:** <who uses it, as the records say.>

## 2. Words used here

| Word | Meaning here |
| --- | --- |
| <a business word in this {Epic pack} an engineer could read two ways> | <its meaning, as the records use it> |

## 3. Settled {Decision}s

- **<CODE>-ANS-<nnn>** <the {Decision}, as stored> · Owner: <role> · <YYYY-MM-DD>
  Agreed by: <role>, <YYYY-MM-DD>

<or> None yet.

## 4. Rules and examples

### <CODE>-REQ-<nnn> <a short title in your own words, e.g. "Refunds over $500 need a manager">

> <the {Requirement}, word for word>

- From: <a link to the Confluence page or Jira item | <role>, <YYYY-MM-DD> | <CODE>-ANS-<nnn>>
- <what an active {Answer} adds to this rule, citing its ID>
- Example: <a worked case with real numbers> <(agreed: <role>, <YYYY-MM-DD>) | (worked from the rules, not yet agreed)>
- <CODE>-Q-<nnn> <a short title in your own words, e.g. "Who approves big refunds">: see section 5. `DO NOT DECIDE`.

## 5. Still open: DO NOT DECIDE

- **<CODE>-Q-<nnn>** `DO NOT DECIDE` <the {Question}, as stored> · Needed by: <date, ID or "not set">
  Why it matters to the build: <the score reason, in build terms>. <Only when building on a guess:> **Already being built on a guess: <what>.**

Parked (build nothing for these yet): <CODE>-Q-<nnn> <a short title in your own words, e.g. "Who approves big refunds">; … <or> None.

## 6. Constraints

- **<CODE>-REQ-<nnn>** (applies here too): <the {Requirement}, word for word>

<or> None.

## 7. Depends on

- <each line of `## Depends on` in `epic.md`, in shown names>

<or> None.

## 8. Scope

- **Goal:** <one line, from the {Feature}'s description>
- **Non-goals:** <what the records exclude, or "Not stated yet.">
- **Left out of this {Epic}:** <each line of `## Left out` in `epic.md`, or "None.">

## 9. Acceptance criteria (business terms)

- [ ] <one per covered {Requirement} and per settled {Decision}: a check a Stakeholder could watch happen, in your own words, citing its ID, e.g. "A $600 refund waits for a manager's OK (<CODE>-REQ-<nnn>)">

---

## Appendix A: Decision coverage

For the Operator and the {Sign-off view}. Engineers can skip this.

| # | Category | State | Cites |
| --- | --- | --- | --- |
| 1 | Rules | <settled | open | N/A | gap> | <IDs, or the Operator's N/A reason> |

Quality: <each ISO/IEC 25010:2023 characteristic and its state.>

## Appendix B: Pain points

- <each pain point, in one plain line citing its ID> <or> None.
