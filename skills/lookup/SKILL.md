---
name: lookup
description: Answer what a Project's records say, citing IDs and files. Use for `/lookup`, or when the Operator asks what the rule is, what was decided, or what we know about something. Not for where an Epic stands or who has agreed its Decisions: that is `signoff`.
---

# Lookup

Follow the Lookup rules in the Tool-owned block of `AGENTS.md`, then reply in this shape, the three labels exactly as written:

```markdown
**In short**
<the answer in one to three sentences, with working shown when it is worked out from rules>

**Based on**
- `<ID>` in `<file path from the Workspace root>`: <what it says, in a few words>
- <one line per cited ID; for a replaced record, the active one first, then "replaced `<old ID>` (<what it said>) on <date>">

**Not known yet**
- <each gap in what you asked, with the {Question} that covers it: "{Question} `<Q ID>` in `<file>` asks <its wording> and is not settled yet; <who it is waiting on>"; or that no {Question} covers it yet>
- <or, when nothing that bears on what you asked is missing, exactly: "Nothing: the records settle what you asked.">
```

Every `{Term}` slot is that term's shown name, in **Based on** as in **Not known yet**.

Who it is waiting on comes from the {Question}'s header lines:

- `Ask:` and `Asked:` both set: "waiting on <the `Ask:` person> since <the `Asked:` date>".
- `Ask:` set, no `Asked:`: "<the `Ask:` person> is to be asked, not asked yet".
- No `Ask:` line: "nobody has been asked yet".

**Not known yet** holds only gaps in what the Operator asked; open Questions on other points stay out of the reply.

A gap line says what is open in the {Question}'s own wording and stops there. It offers no possible answers, options or likely outcomes, not even hedged ("whether a full refund, a credit or …", "probably …"): the open {Question} is the whole answer.

Done when: the reply has all three parts and passes the Lookup rules' done-check.
