---
name: lookup
description: Answer what a Project's records say, citing IDs and files. Use for `/lookup`, or when the Operator asks what the rule is, what was decided, or what we know about something.
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
- <each gap in what you asked, with the open Question that covers it: `<Q ID>` in `<file>`; or that no Question covers it yet>
- <or, when nothing that bears on what you asked is missing, exactly: "Nothing: the records settle what you asked.">
```

**Not known yet** holds only gaps in what the Operator asked; open Questions on other points stay out of the reply.

Done when: the reply has all three parts and passes the Lookup rules' done-check.
