# Plan: Throughput and Story counts from Jira

Part of Plan, read when [SKILL.md](SKILL.md) sends you here. **Make a plan** and its numbered steps are in SKILL.md. This flow reads the Throughput and each handed-off Epic's Story counts through the Atlassian MCP's Jira tools instead of having them typed. Ranges, start and in flight are held as SKILL.md says, and so is everything after the Forecast.

1. **The team's Jira project.** The one `project.md` links, or else the prefix of the `Tech face:` keys in the handed-off Epics (`HALL-12` → `HALL`), on the site of their URL; the project's URL is `<site>/jira/software/projects/<key>`. When these differ, ask which project is the team's, and stop until the Operator says.

   Done when: you hold one site and one project key.

2. **Read the done items.** Make the scratch folder now, as step 2 of SKILL.md says. When your instructions name a file standing in for the MCP for the project's URL, it is what both searches below returned: `cp` it to `<scratch>/jira.json` and go to 3. Otherwise make two searches with `searchJiraIssuesUsingJql`, each paged with `nextPageToken` until none comes back:
   - **Done**, with fields `issuetype`, `parent`, `status`, `resolution`, `resolutiondate`, `statuscategorychangedate`, `created` and `labels`: `project = <key> AND issuetype in standardIssueTypes() AND statusCategory = Done AND (resolution in (Done, Fixed) OR resolution is EMPTY) AND updated >= -52w ORDER BY key ASC`.
   - **Never in progress**, keys only: the same JQL without its `ORDER BY`, then `AND status WAS NOT IN (<every status in the In Progress category>)`, those statuses read with `listJiraStatuses` (`mode: "project"`) through `executeRead`.

   Write `<scratch>/jira.json` as `{"done": [<every issue of every page, as returned>], "never_in_progress": ["<key>", …]}`. When a read fails, say so in one line and ask for typed Throughput as step 1 of SKILL.md says.

   Done when: `<scratch>/jira.json` holds both searches, or you have asked for typed Throughput.

3. **Story counts.** For each handed-off Epic, read its tech face (the `Tech face:` URL), or the file your instructions name standing in for that URL: every child work item whose parent it is, at standard level (a Sub-task is not one). **Open** is every child not in the Done status category; **done** is every child in it except the won't-do ones (a Won't Do or Cancelled status, or a won't-do label or resolution), which are in neither count; **read** is today. Only these three numbers are kept: the tech face's own status stays in Jira, and `epic.md` is left as it is. When a read fails, say so and use the counts the Operator typed, asking for them if there are none.

   Done when: each handed-off Epic has open, done and read, from its tech face or typed.

4. **Count the weeks.** Write `inputs.json` as step 2 of SKILL.md says, with `"weeks": []`, `"finished_epics": []` and `throughput.from` naming the source:

   `Jira <site> project <key>, done: <Done JQL>; never in progress: <Never in progress JQL>; run <today>`

   adding `; left out by <Operator's name>: <keys>` once the Operator leaves any out. Then run the Throughput script, which sets the weeks and finished Epics in that file:

   `python3 <skills>/plan/scripts/throughput.py <scratch>/jira.json --today <today> --into <scratch>/plan-v<N>/inputs.json`

   with `--leave-out <key>,<key>` naming every item the Operator has left out so far. Exit 1: fix what stderr names and run it again. Exit 2: say what could not be read, and stop. Hold its stdout: `window`, `counted`, `never_in_progress` and `left_out`. Then run the Forecast script as step 2 of SKILL.md says.

   Done when: `inputs.json` holds the script's weeks and finished Epics and the source, and the Forecast has run.

5. **In the batch**, item 1 (`inputs.json`) also shows, from the Throughput script's stdout:
   - The source: the project, the run date, and the weeks counted (`window`, and `counted` items).
   - **Left out**: one line per item, its key and reason as the script gave them (won't do, closed without work, done this week, left out by the Operator).
   - **Never in progress**: each key with its done date, counted in the Throughput. Ask the Operator, for each one, whether it was real work to keep or one to leave out.

   An Operator who leaves an item out amends the batch: run step 4 again with it in `--leave-out`, then the rest as an amend in SKILL.md says.

   Done when: the batch names the source, every left-out item and every never-in-progress item, with the ask.

`<scratch>/jira.json` stays outside `plan-v<N>/`, so it is never copied into the Workspace, and goes when the scratch folder is deleted.
