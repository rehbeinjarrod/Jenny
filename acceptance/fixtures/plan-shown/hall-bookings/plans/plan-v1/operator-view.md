# HAL · Plan v1: Community hall bookings (Operator)

Start: 2026-11-23 · Dates are Fridays. Likely: half the trials finished by then. Very likely: 85 in 100 did.

## At risk

Nothing at risk.

## Milestones

| Milestone | Target | Likely | Very likely | Chance of meeting the target |
| --- | --- | --- | --- | --- |
| `HAL-MIL-001` Walking skeleton (hirers) | none | 2026-12-11 | 2026-12-18 | no target |
| `HAL-MIL-002` First online bookings | 2027-03-01 | 2027-01-01 | 2027-01-15 | 100% |

## Chart

One row per Spec: dark to its likely finish, a light tail to its very likely finish, red when it is on the critical path. Specs are grouped by Milestone, groundwork first, and each group ends with its Milestone's row: a ◆ at its very likely date and a red ◆ at its target. Bars are worked out from Stories finished each week, not estimates.

```mermaid
---
displayMode: compact
config:
  gantt:
    leftPadding: 230
    barHeight: 22
    fontSize: 12
    sectionFontSize: 12
---
gantt
    dateFormat YYYY-MM-DD
    axisFormat %d %b
    tickInterval 2week
    todayMarker off
    section Book and pay
    likely 11 Dec :crit, HAL_EPC_001, 2026-11-27, 2026-12-11
    by 18 Dec :active, crit, HAL_EPC_001_tail, 2026-12-11, 2026-12-18
    section ◆ Walking skeleton (hirers)
    by 18 Dec :milestone, HAL_MIL_001_by, 2026-12-18, 0d
    section Cancel a booking
    likely 1 Jan :crit, HAL_EPC_002, 2026-12-18, 2027-01-01
    by 15 Jan :active, crit, HAL_EPC_002_tail, 2027-01-01, 2027-01-15
    section ◆ First online bookings
    target 1 Mar :crit, milestone, HAL_MIL_002_target, 2027-03-01, 0d
    by 15 Jan :milestone, HAL_MIL_002_by, 2027-01-15, 0d
```

## Specs with no date yet

Every Spec has a date.

## Specs

In the order the Forecast gives. Critical: on the critical path in half the trials or more.

| Spec | Likely start | Likely | Very likely | Depends on | Critical path | Count from | Enables |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `HAL-EPC-001` Book and pay | 2026-11-27 | 2026-12-11 | 2026-12-18 | none | 100%, critical | Story counts read 2026-11-18 | |
| `HAL-EPC-002` Cancel a booking | 2026-12-18 | 2027-01-01 | 2027-01-15 | HAL-EPC-001 | 100%, critical | engineers' range | |

## Open items and pain points

None.

## Lucid

1. Open the Lucid document for this view, and paste the whole text of `plans/plan-v1/gantt.mmd` into a Mermaid diagram.
2. Re-render it, and check there is one row per Spec and per ◆.
3. Embed it in the Confluence page with the Lucid macro.

## Seed and history

- Seed: 1 · Trials: 10000 · In flight: 2
- Throughput: 12 weeks of the last 26, normal; from typed by Dana Wells, 2026-11-18
- Finished Specs counted: 0
