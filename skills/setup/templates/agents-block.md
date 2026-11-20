<!-- jenny:begin -->
# Jenny

This folder is a Jenny Workspace: one Operator's Projects kept as small Markdown files. The text between the `jenny:begin` and `jenny:end` markers belongs to the Tool and is replaced on upgrade; write your own notes outside the markers.

The Jenny skills live in the runtime's skills folder named in `workspace.md`. They are a Tool-owned copy: read them, never edit them.

## Read first

1. `workspace.md`: Tool version, runtime, settings and the list of Projects. Before anything else on every turn, run the version check, step 1 of the `jenny` skill's `SKILL.md`. Until it passes, its warning is the whole reply, and the rules below wait, Lookup included, except the Veneer scan, which the warning goes through like every reply. The one exception is a request the `setup` skill owns, such as an upgrade: it runs as `setup` says, so the Operator can bring the versions back in line through it. In the Jenny mode, the mode's own step 1 still comes first.
2. `veneer.md`, if it exists: the Veneer.
3. The Project's `projects/<slug>/index.md`, then only the files it points to. Work in one Project at a time.

## Veneer

When `veneer.md` exists, every word the Operator reads uses its shown names: chat replies, proposals, asks and summaries. That holds for every Delivery term spoken in passing too, such as the kind of file being written or the heading of a batch. Records, folder and file names, IDs, log entries and commit messages always use the canonical terms. That covers every line Jenny writes in a record, prose included: a `Score reason:` and each line of a log entry name an Epic as "Epic" and a Question as "Question", never by their shown names, even when the batch said them in shown names. The Guard rejects a shown name in a `Score reason:`. Show every file path, ID, and piece of text quoted from a record (a heading such as `## Projects`, a header line) in a code span, exactly as stored.

A renamed term's canonical word (either case, singular or plural) belongs to its records alone: in a reply it appears only inside code spans, in every sense, ordinary English included. Reword instead:

- The Operator's own message: "what you asked".
- An ask of the Operator: the ask itself ("Item 3: who owns this Decision?"), "can you confirm …", or "one more thing I need from you".
- Something the Operator left unanswered: "you didn't say".
- A record, even in passing or in a possessive: its shown name ("the <shown name for Project>'s People").
- A record named by its topic: its shown name, its ID, or both ("the <shown name for Question> on deposits", "<shown name for Question> `HAL-Q-014`"). An engineer's ask can also be their `Business question`, in a code span.
- A shown name stands alone, with no canonical word beside it to explain it. A record's exact stored text, such as a heading or a file path, goes in a code span.

Words taken from a skill, a template or a record (a section name, a sentence a file will hold) are either put in a backtick code span, exactly as written, or said again in shown names. Quotation marks are not a code span.

**Veneer scan.** When `veneer.md` exists, run every draft reply through the Veneer scan before sending it, the version-mismatch warning included. From the Workspace, with `<skills>` the runtime's skills folder (`.claude/skills` or `.cursor/skills`) and the whole reply between the markers:

```bash
python3 <skills>/jenny/scripts/veneer_scan.py <<'JENNY_REPLY'
<the reply>
JENNY_REPLY
```

- Exit 0: the reply is clean. Send it.
- Exit 1: each output line, `<line>: <word>`, is a canonical word outside a code span. Reword each one as the bullets above say, then scan the new draft. Send it once the scan exits 0.
- Exit 2, or the scan cannot run (no `python3`, no script): send the reply, with one line first saying `veneer.md` could not be read and why, from the scan's message, so the Operator can fix it.

Read what the Operator types in any of the three forms (canonical term, shown name, or alias) and store the canonical term. When a shown name is also another term's canonical name, read the Operator's word in the Veneer's sense. Ask when the reading changes which record something lands in.

Operator, Stakeholder, Tool, Workspace and Veneer are never renamed. With no `veneer.md`, the canonical terms show.

## Every write: confirm, then write

Every change to the Workspace is one operation:

1. **Propose** a numbered batch in chat under a heading that names the operation in shown names (for example "New <shown name for Project>: <Name>"): each file to be written or changed and what goes in it, then the words "Nothing is written yet."
2. **Amend** by number as the Operator asks, and show the batch again in full, under the same heading. The items are numbered 1, 2, 3… afresh each time. A proposed ID, shown in the batch but not yet written, follows these rules on each amend:
   - It stays fixed: each proposed record keeps the ID it was first shown with, moving only to close up a gap below it.
   - Drops first: when the amend drops records, the later proposed IDs of each dropped record's kind move down to fill every gap, so the IDs written run on with no hole. Every line in the batch that cites a moved ID changes with it.
   - Adds next: each record the amend adds takes the next ID of its kind after the highest proposed one in the batch, or the Project's next free ID of that kind when the batch has none.
3. **Confirm**: write only after the Operator says yes. Until then, write no file, not even a draft, and run no command that changes the folder.
4. **Log**: add one entry to the log, with the heading `## [YYYY-MM-DD] <op> | <title>` and one line per file written, naming each record by its canonical term and ID (`- Question HAL-Q-014 in questions/HAL-Q-014-….md`). A Project operation logs to `projects/<slug>/log/YYYY-MM.md`; a Workspace-wide one to `log/YYYY-MM.md`. Start a new month's file with `# <CODE> log · YYYY-MM` (or `# Workspace log · YYYY-MM`).
5. **Commit** everything in the operation as one commit. The message is the log heading with only its leading `## ` taken off, so it starts with the bracketed date: `git add -A && git commit -m "[YYYY-MM-DD] <op> | <title>"`. The commit runs the Guard, the Workspace's git pre-commit hook. When it rejects the commit, it names each file and problem: fix each one in the files of this operation, and commit again. Never pass `--no-verify`.
6. **Report**: one reply after the commit, holding what the skill's own steps say to tell the Operator (such as its record lines or its **Hand on**) and the commit message in a code span. Give any file it names as its full path in a code span (`projects/<slug>/questions/index.md`). It is a draft reply like any other: when `veneer.md` exists, it goes through the Veneer scan before it is sent.

When the Operator's own typed words answer a Question during any skill's operation, that skill's batch may capture them as an Answer: follow **Embedded Capture** in the `capture` skill.

Done when: `git status --porcelain` is empty, the last commit message is the log heading, and the report has been sent, through the Veneer scan when `veneer.md` exists.

## Records

- IDs start with the Project code: `<CODE>-SRC-`, `-REQ-`, `-FEA-`, `-EPC-`, `-Q-`, `-ANS-`, `-SO-`, `-MIL-`, then three digits. A written ID is never reused or renumbered, and is written out in full every time. A proposed ID follows **Amend** above.
- Every file starts with its ID (or Project code) and title, then `Key: value` header lines.
- Links are relative Markdown links.
- A file stays under 300 lines and an index under 150. Past that, split it along a natural seam and update its index in the same operation. An Epic pack is the exception: it is never split, and `pack` refuses one that would pass 300 lines.
- Sources, Epic packs (`pack-v<N>.md`), Sign-off views and Plan folders (`plans/plan-v<N>/`) are frozen once written: never edited, but for the `Shown:` line `plan` appends to a Plan's `plan.md`. A change is a new file, or a new Plan version.
- A withdrawn line stays in place, struck through, with `Withdrawn <date>`, `Reason:` and `Replaced by: <ID>` when it has a replacement.

## Lookup

Everything the Operator asks about what a Project's records say is answered this way, in plain words or through `lookup`, and the reply takes the answer shape in the `lookup` skill. A lookup writes nothing. A question a skill's description names, such as where an Epic stands with its Stakeholders (`signoff`), follows that skill instead, reading the records by these same rules.

1. **One Project.** Find the Project from its name, code or the words used, and ask when two could fit. Read only that Project's folder: another Project's rule never answers this one, even when it uses the same words.
2. **Index first.** Read the Project's `index.md`, then the folder indexes and files it links to that bear on what was asked. Read each file whole; they are small. To find every place an ID appears, `grep -rn '<ID>' projects/<slug>/`.
3. **Active records only.** A struck-through line is history. Follow its `Replaced by:` to the active record, answer from that, and say what it replaced and when.
4. **Gaps stay gaps.** What the records do not settle is unknown. Name the open Question in `questions/index.md` that covers it and who it is waiting on (from its `Ask:` and `Asked:` lines, as the `lookup` skill says), or say no Question covers it yet. Fill no gap from general knowledge or another Project, and offer no guess at the answer: no possible answers, options or likely outcomes, not even hedged.
5. **Cite.** Every ID the answer rests on, with the file it is in, as code spans. For a Decision, also its owner and date.

Done when: every fact in the reply cites an ID and its file, and every gap is named as unknown.
<!-- jenny:end -->
