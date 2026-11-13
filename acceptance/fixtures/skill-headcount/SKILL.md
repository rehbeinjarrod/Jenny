---
name: headcount
description: Count the People on one Project. Use for `/headcount`, or when the Operator asks how many people are on a Project.
---

# Headcount

A test skill, added after install to prove the Jenny mode routes to skills it was never told about. It writes nothing.

Read the Project's `project.md`, count the rows of its People table, and reply in exactly this shape, with Veneer names in any words around it:

```markdown
**Headcount**
`<CODE>`: <n> people
- <Name> (<role>)
```

One `- ` line per person, in table order. Done when: the reply has the label, the count line and one line per person.
