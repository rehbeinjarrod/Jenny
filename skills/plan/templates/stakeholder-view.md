# <CODE> · Plan v<N>: <Project name>

Start: <start> · Dates are Fridays. Likely: half the trials finished by then. Very likely: 85 in 100 did.
<Only when history.status is early, otherwise leave this line out:> Early: these dates rest on <history.weeks> weeks of history, so they can move a lot.

## At risk

<One line per item, most at risk first, e.g. "- `HAL-MIL-002` First online bookings: a 34% chance of meeting its 2027-03-01 target.":>
- <Each Milestone whose target_met_share is under 0.5: its ID, name, chance and target.>
- <Each undated Milestone: its ID, name and its no_date reason in plain words.>
<Or, when there are none:> Nothing at risk.

## Milestones

| Milestone | Target | Likely | Very likely | Chance of meeting the target |
| --- | --- | --- | --- | --- |
| `<MIL ID>` <name> | <target, or "none"> | <likely_finish, or "no date"> | <very_likely_finish, or "no date"> | <target_met_share as a whole percent, or "no target", or "no date"> |

## Chart

One row per <shown name for Epic>: dark to its likely finish, a light tail to its very likely finish, red when it is on the critical path. <shown name for Epic>s are grouped by Milestone, groundwork first, and each group ends with its Milestone's row: a ◆ at its very likely date and a red ◆ at its target. Bars are worked out from Stories finished each week, not estimates.

<With one Gantt file, `gantt.mmd`, its whole text in one block:>
```mermaid
<gantt.mmd, as the Forecast script wrote it>
```
<With a chapter per Milestone, one `###` heading per Gantt file in file name order, `### `<MIL ID>` <name>` (or `### Not in a Milestone` for `gantt-other.mmd`), then that Milestone's row of the table above repeated as one line, then its file's whole text in one `mermaid` block.>

## <shown name for Epic>s with no date yet

<One line per undated Epic, e.g. "- `HAL-EPC-002` Cancel a booking: no Story count yet; the engineers are asked for a range in `HAL-Q-017`.":>
- `<EPC ID>` <title>: <its no_date reason in plain words>; <for a no-count Epic: the Question asking for a range>.
<Or, when there are none:> Every <shown name for Epic> has a date.
