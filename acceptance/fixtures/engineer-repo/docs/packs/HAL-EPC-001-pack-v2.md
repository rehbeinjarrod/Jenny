# Spec pack: HAL-EPC-001 Book and pay (v2)

| | |
| --- | --- |
| Initiative | HAL Community hall bookings |
| Feature | HAL-FEA-001 Book and pay |
| Spec | HAL-EPC-001 Book and pay |
| Version | v2, written 2026-11-12 by the Operator, replacing `pack-v1.md` |
| Sign-off | 1 of 1 Decisions agreed by a Stakeholder |

## For the agent reading this

This Spec pack is the business half of the spec for HAL-EPC-001. Use it as settled input to your spec step.

- **Settled Decisions are final.** Build on them as written, and keep them closed in grilling and brainstorming. If one looks wrong, post a `Business question` about it.
- **An item marked `DO NOT DECIDE` is a business decision still open.** Build around it if you can, or stop. Either way, post a `Business question` quoting its ID.
- **A business decision this Spec pack does not cover** is `DO NOT DECIDE` too: post a `Business question` for each one.
- **A business call made anyway**, by you or your engineer: post a `Business call made in build`.
- People are named here by role. Post either shape as a comment on the work item this Spec pack was handed over with, or give it to your engineer to post.
- Stack, commands, repo layout and test seams are not in this Spec pack: the repo's `AGENTS.md` and your harness own those.

```text
Business question
IDs touched: <Requirement, Open item and Answer IDs>, HAL-EPC-001
Question: <the question, in one sentence>
Options seen: <each option, in a few words>
Default if forced: <the option you would take, and why>
Status: blocked | building around it (on a guess: <what>)
```

```text
Business call made in build
IDs touched: <Requirement, Open item and Answer IDs>, HAL-EPC-001
Decided: <what was decided>
Why: <one line>
Made by: agent | engineer
```

## 1. Problem and outcome

The Riverbend community hall takes bookings by phone and in person. The hall committee wants hirers to book the main hall online, at the member or non-member rate, and pay a deposit to confirm it.

**Outcome:** a hirer books the main hall online and pays the deposit; the booking is confirmed once the deposit is in.

**Who:** hirers of the main hall, members and non-members.

## 2. Words used here

| Word | Meaning here |
| --- | --- |
| Hirer | The person who books the hall and pays for it. |
| Member | A hirer who is a member of the community hall; pays the member rate. |
| Hire fee | The hourly rate times the hours booked. |
| Deposit | The part of the hire fee paid when booking, which confirms the booking. |

## 3. Settled Decisions

- **HAL-ANS-001** The deposit is 20% of the hire fee, with a minimum of $50. · Owner: Stakeholder, hall committee chair · 2026-11-04
  Agreed by: Stakeholder, hall committee chair, 2026-11-10

## 4. Rules and examples

### HAL-REQ-001 Confirmed once the deposit is paid

> A booking is confirmed only once its deposit has been paid.

- From: Stakeholder, hall committee chair, 2026-10-28
- HAL-Q-004 cash deposits, HAL-Q-008 who sees a booking, HAL-Q-010 responsible adult, HAL-Q-014 failed payment, HAL-Q-015 two hirers at once: see section 5. `DO NOT DECIDE`.

### HAL-REQ-002 The deposit amount

> The deposit is 20% of the hire fee, with a minimum of $50.

- From: HAL-ANS-001
- Example: a non-member books the main hall for 3 hours: the hire fee is $135, 20% is $27, so the deposit is the $50 minimum (worked from the rules, not yet agreed).

### HAL-REQ-003 Member and non-member rates

> The main hall costs $30 an hour for members and $45 an hour for non-members.

- From: Stakeholder, hall committee chair, 2026-10-28
- HAL-Q-007 member booking for a non-member, HAL-Q-009 past 11 pm, HAL-Q-011 cleaning fee: see section 5. `DO NOT DECIDE`.
- Example: a member books the main hall for 4 hours: the hire fee is $120 (worked from the rules, not yet agreed).

### HAL-REQ-004 How far ahead

> Members can book up to six months ahead; non-members up to three months ahead.

- From: Stakeholder, hall committee chair, 2026-10-28
- HAL-Q-016 exactly six months ahead: see section 5. `DO NOT DECIDE`.

## 5. Still open: DO NOT DECIDE

- **HAL-Q-007** `DO NOT DECIDE` Does a member pay the member rate when they book the hall for a non-member's event? · Needed by: HAL-EPC-001
  Why it matters to the build: it decides which rate a member's booking is charged. **Already being built on a guess: the member rate for anything a member books.**
- **HAL-Q-014** `DO NOT DECIDE` If the deposit payment fails, is the booking held for the hirer, and for how long? · Needed by: HAL-EPC-001
  Why it matters to the build: it decides whether a failed payment frees the hours at once. **Already being built on a guess: whatever the build does today.**
- **HAL-Q-015** `DO NOT DECIDE` If two hirers try to book the same hours at the same time, who gets them? · Needed by: HAL-EPC-001
  Why it matters to the build: it decides which payment confirms the booking. **Already being built on a guess: whatever the build does today.**
- **HAL-Q-009** `DO NOT DECIDE` Can a booking run past 11 pm? · Needed by: 2026-12-10
  Why it matters to the build: it sets the last hour a booking can cover.
- **HAL-Q-008** `DO NOT DECIDE` Who can see a booking's details: only the hirer, or the whole committee? · Needed by: 2026-11-20
  Why it matters to the build: booking details hold the hirer's phone number.
- **HAL-Q-004** `DO NOT DECIDE` Can non-members pay the deposit in cash at the hall office? · Needed by: 2026-12-15
  Why it matters to the build: a cash deposit confirms a booking outside the online payment.
- **HAL-Q-010** `DO NOT DECIDE` Does every booking need a named adult who is responsible on the night? · Needed by: 2026-12-20
  Why it matters to the build: it may add a field every booking must fill in.
- **HAL-Q-013** `DO NOT DECIDE` Will the new meeting room be booked through the same service when it opens? · Needed by: 2027-07-31
  Why it matters to the build: adding a second room later could change every price table.
- **HAL-Q-011** `DO NOT DECIDE` Is there a cleaning fee on top of the hire fee? · Needed by: 2027-01-15
  Why it matters to the build: it would change the hire fee and so the deposit.

- **HAL-Q-016** `DO NOT DECIDE` Can a member book a date exactly six months ahead, to the day? · Needed by: HAL-EPC-001
  Why it matters to the build: it decides which side of the limit wins.

Parked (build nothing for these yet): HAL-Q-005 photo gallery; HAL-Q-017 bookings already taken at the hall office.

## 6. Constraints

None.

## 7. Depends on

None.

## 8. Scope

- **Goal:** a hirer books the main hall online and pays a deposit to confirm it.
- **Non-goals:** Not stated yet.
- **Left out of this Spec:** HAL-REQ-008 (the door code in the confirmation email) stays unplaced for now.

## 9. Acceptance criteria (business terms)

- [ ] A booking shows as confirmed only after its deposit is paid (HAL-REQ-001).
- [ ] The deposit asked for is 20% of the hire fee, and never less than $50 (HAL-REQ-002, HAL-ANS-001).
- [ ] A member is charged $30 an hour and a non-member $45 an hour for the main hall (HAL-REQ-003).
- [ ] A member can book up to six months ahead and a non-member up to three (HAL-REQ-004).

---

## Appendix A: Decision coverage

For the Operator and the Sign-off view. Engineers can skip this.

| # | Category | State | Cites |
| --- | --- | --- | --- |
| 1 | Rules | open | HAL-REQ-001, HAL-REQ-002, HAL-REQ-003, HAL-ANS-001 · open HAL-Q-011 |
| 2 | Boundaries | open | HAL-Q-009, HAL-Q-016 |
| 3 | Unwanted behaviour | open | HAL-Q-014, HAL-Q-015 |
| 4 | States | settled | HAL-REQ-001 |
| 5 | Variants | open | HAL-REQ-003, HAL-REQ-004 · open HAL-Q-004, HAL-Q-007, HAL-Q-013 |
| 6 | Data | open | HAL-Q-008 |
| 7 | Permissions | open | HAL-Q-008, HAL-Q-010 |
| 8 | Downstream | N/A | The Operator: nothing else needs to hear of a booking yet; the caretaker's list is its own Feature. |
| 9 | Quality | N/A | The Operator: the phone-screen rule covers what matters for now. |
| 10 | Rollout | open | parked HAL-Q-017 |
| 11 | Examples | N/A | The Operator: the rules are plain sums, and the worked cases in section 4 show them. |

Quality: performance, reliability, security, interaction capability and compatibility are N/A by the Operator's mark; safety: no harm to a person is possible.

## Appendix B: Pain points

- HAL-Q-007 is being built on a guess: the member rate is charged for anything a member books.
- HAL-Q-014 and HAL-Q-015 were raised after the handover of `pack-v1.md`, so the build has already made some choice for each.
