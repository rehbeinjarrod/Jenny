# Jenny

Jenny is a requirements-management workspace for a product manager or business analyst running several delivery projects at once. It keeps each project's requirements, open questions, decisions and sign-offs as plain files in a git repository on your own machine, and gives your AI assistant (Claude Code or Cursor) a set of skills for reading and writing them.

You talk to Jenny in plain words. Every change is shown to you as a numbered proposal first, and nothing is written until you say yes. Jenny holds no project data: your data lives in a separate folder, your **Workspace**, which Jenny installs into and you own.

## Skills

Each skill is a folder in [skills/](skills/). You rarely name one: say what you want and Jenny picks the skill.

- **setup**: install Jenny, upgrade it, start a project, add the people on it, and set your organisation's own words for Jenny's terms (say "Initiative" where Jenny says Project, for example).
- **capture**: turn what you bring in (a typed note, an email, meeting notes, a Confluence page) into requirements, open questions and answers, each tied to where it came from. Also brings back a stakeholder's sign-off, and checks a handed-off Jira Epic for business questions the engineers have raised.
- **lookup**: answer what a project's records say, citing the IDs and files.
- **up-next**: what to chase next in a project, and shaping a question before you ask it.
- **slice**: group a project's requirements into features, each with one Epic.
- **pack**: check an Epic for business decisions still unmade, then write the pack the engineers build from.
- **signoff**: write a stakeholder's view of an Epic's pack, publish it to Confluence, and report who has agreed what.
- **handoff**: record that a pack went to the delivery team, and report what has changed since.
- **plan**: forecast when a project's milestones and epics will land, from the stories the team finishes each week, with a Gantt chart to paste into Lucid. Also records when a plan went out, and reports which dates have moved since.
- **jenny**: the Jenny mode, which routes each request to its skill and checks your Workspace is on the installed Tool version.

## What you need

- [Claude Code](https://claude.com/claude-code) or [Cursor](https://cursor.com), with access to a Sonnet model. Jenny is tested on Sonnet only.
- git.
- Python 3.9 or later, as `python3`. Jenny uses it to check her replies use your organisation's words.
- For Jira and Confluence: an Atlassian Cloud site you can sign in to. Jenny reaches it through the Atlassian MCP server, which signs in through your browser, so no token is stored in your Workspace. Without Atlassian, Jenny still works on what you type or paste, and writes anything it would post to an `outbox/` folder instead.

## Install

1. Clone this repository somewhere that will stay put. Your Workspace remembers the path.

   ```bash
   git clone https://github.com/rehbeinjarrod/jenny.git
   ```

2. Make an empty folder for your Workspace and open it in Claude Code or Cursor.
3. Tell the assistant:

   > Follow `<path to your clone>/skills/setup/SKILL.md` to install Jenny in this folder.

   Jenny asks which tool you use and whether it should post to Jira and Confluence or write to `outbox/`, shows what it will write, and installs once you say yes. Your Workspace becomes its own git repository.
4. Start afresh so the skills load:
   - **Claude Code**: start a new session in the Workspace folder.
   - **Cursor**: make the Jenny mode from the settings the install shows you (also in [skills/jenny/mode.md](skills/jenny/mode.md)), then start every Jenny chat in that mode.

Then ask for a new project. Each project gets a short code (such as `HALL`) used in every ID.

## Upgrade

Each Tool version is a commit on `main` tagged `v<version>`. [CHANGELOG.md](CHANGELOG.md) says what each one changes in a Workspace and how older records are read.

Version numbers say what an upgrade does to your Workspace (its records, its settings and the Jenny block of `AGENTS.md`):

- **Major** (2.0.0): something older is no longer read as it was, or you have a step to do by hand. Its CHANGELOG entry says which.
- **Minor** (1.1.0): new or changed behaviour; every older record is still read as it is.
- **Patch** (1.0.1): fixes only, with no new record shapes or settings.

1. Pull the new version into your clone:

   ```bash
   git -C <path to your clone> pull
   ```

2. In your Workspace, ask Jenny to upgrade. It shows what will change (skills, the Jenny block of your `AGENTS.md`, any new settings) and the CHANGELOG entries in between, and upgrades in one commit once you say yes. Your records are never rewritten.
3. Start a new session (Claude Code) or a new chat in the Jenny mode (Cursor).

Going back is reverting that one upgrade commit in your Workspace. To stay on a version, check out its tag in your clone (`git checkout v1.0.0`) instead of pulling.

## Acceptance checks

`acceptance/` holds the checks Jenny is tested against, a sample Workspace and its fixtures. You can run them yourself to see that Jenny behaves on your machine as it does on the maintainer's. Runs go into `acceptance/runs/`, which git ignores, so your clone stays clean and `git pull` keeps working.

- **Claude Code**: open your clone and say

  > Follow `acceptance/runner/claude-code.md` and run acceptance for `<scope>`

  where `<scope>` is a skill name (`lookup`), a check ID (`LK-01`), or `gate` for every check.

- **Cursor**: the Cursor bench runs the few checks that prove a published Tool version works on Cursor, each once, from a clone at that version's tag. It has two sides. A grading chat (a plain Agent chat on Sonnet, opened on your clone) prepares the run and grades it; you type each check's script into a fresh chat in the Jenny mode. Start the grading chat with

  > Follow `acceptance/runner/cursor.md` to prepare a Cursor bench run.

  and it tells you each step.

Every check reads fixtures in place of Jira and Confluence, so a run never touches a real Atlassian site.

A run is made to be cheap: the design target is 0.25% of a 5-hour usage window per check run. A gate run makes only the check runs whose evidence is missing: a check unchanged since the last Tool version needs none.

## Support and contributions

This is a personal project, provided as-is under the [Apache License 2.0](LICENSE), **with no support, warranty or obligation of any kind**. Responses, fixes and new versions happen only at the maintainer's discretion, and may not happen at all. Everyone, including any organisation the maintainer works for or with, uses it under the same public licence, with no separate agreement.

The project is open source but not open to contributions: issues and pull requests are turned off. See [SUPPORT.md](SUPPORT.md) and [CONTRIBUTING.md](CONTRIBUTING.md). Forks are welcome.
