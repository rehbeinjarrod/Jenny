# Capture: Confluence pages

Part of Capture, read when [SKILL.md](SKILL.md) sends you here. A section named in bold (**1. Find the Project**, **2. Read the material into candidates**) is in SKILL.md.

The material is the page as the Atlassian MCP returns it: read it with the MCP's Confluence page tool, the page ID taken from the URL and the body as Markdown. When your instructions name a file standing in for the MCP for that URL, read that file instead: it is what the MCP returned. When the read fails, say so in one line and propose nothing; the Operator can paste the page instead.

A page is own-organisation material unless it quotes a third party, and its Owner is the page's last author. Its Source is `Kind: Confluence page` and keeps the parts used word for word, with `URL:`, `Page version:` and `Read:` (the date of this read) in place of `Captured:`, and `Date:` the page's last-updated date.

**Re-read.** A URL already in a Source's `URL:` line is a re-read, whether or not the Operator says "re-read": `grep -rlxF 'URL: <url>' projects/*/sources/`. In each Project that holds the URL, the earlier reading is the latest of its Sources, the one no other names in `Previous reading:`; a page in several Projects is re-read in each, as **1. Find the Project** says for material bearing on several Projects. When its `Page version:` matches the page's, say the page is unchanged since that reading and propose nothing. Otherwise the batch proposes only what changed:

- **Item 1** is a new Source with `Previous reading: <earlier Source ID>`, holding every part this reading uses, unchanged parts included, so each reading stands alone. The earlier Source stays as it is.
- Each part of the earlier reading is **unchanged**, **changed** or **gone**. A Requirement is built on a part when it cites this page's earlier reading or an older one, and its statement comes from that part. One built on a changed part and a gone part is treated as changed.
  - **unchanged**: nothing proposed; name these parts in one line after the items.
  - **changed**: each Requirement built on the old text is withdrawn and replaced ("withdraw `<ID>` and replace it with `<new ID>`: …"), the replacement citing the new Source. The page has changed its own text, so its newer wording stands; a change that bears on a Requirement from another Source is labelled against it as in **2. Read the material into candidates**.
  - **gone**: each Requirement built only on it is a "withdraw? `<ID>`" item: say what has gone, and that `<ID>` stays active unless the Operator says to withdraw it. Accept all leaves it active. When the Operator says to withdraw it, the item becomes a withdrawal with no replacement, its `Reason:` naming the new Source.
- A part new to the page becomes candidates as in **2. Read the material into candidates**.

Done when: the page is read (or the failed read is reported), and on a re-read every part of the earlier reading is unchanged, changed or gone, with an item for each Requirement built on a changed or gone part.
