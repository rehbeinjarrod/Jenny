# Lucid paste steps

Confluence shows a Plan's Gantt through Lucid, which renders Mermaid. Each Gantt file has its own Lucid document. These steps go into the Operator view under `## Lucid`, once per Gantt file, as a numbered list headed by the file's path, `plans/plan-v<N>/<gantt file>`:

1. Open the Lucid document for this chart, or make one named after the Plan version and the file the first time.
2. Paste the file's whole text into the document's Mermaid diagram, in place of what is there.
3. Re-render the diagram.
4. Check one row per item: each `section` line in the file is one row, in the file's order, with its bars and diamonds on the dates the file gives, and no row missing or doubled.
5. Embed the document in the Confluence page with the Lucid macro.
