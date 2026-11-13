# Making the Jenny mode in Cursor

On Cursor, the Operator works in a Custom Mode named Jenny. A `/skill` alone fades after a message or two; the mode makes Jenny re-read [SKILL.md](SKILL.md) every turn, and that file re-reads the skill in hand. The mode's own text never changes between Tool versions, so an upgrade replaces only the skill files.

Make the mode once per Cursor install, from the mode picker in the chat box (add a custom mode):

- **Name**: `Jenny`
- **Model**: Sonnet
- **Tools**: all on: search and read files, edit files, run terminal commands
- **Instructions**, exactly:

  > You are Jenny. At the start of every turn, before anything else, read `.cursor/skills/jenny/SKILL.md` whole and follow it.

Start every Jenny chat in the Jenny mode, in a window opened on the Workspace folder. After an upgrade, start a new chat.
