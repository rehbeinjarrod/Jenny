# Spec pack: HAL-EPC-002 Online payment account (v1)

| | |
| --- | --- |
| Initiative | HAL Community hall bookings |
| Feature | HAL-FEA-001 Book and pay |
| Spec | HAL-EPC-002 Online payment account |
| Version | v1, written 2026-11-16 by the Operator |
| Sign-off | none yet |

## For the agent reading this

This Spec pack is the business half of the spec for HAL-EPC-002. Use it as settled input to your spec step.

- **Settled Decisions are final.** Build on them as written, and keep them closed in grilling and brainstorming. If one looks wrong, post a `Business question` about it.
- **An item marked `DO NOT DECIDE` is a business decision still open.** Build around it if you can, or stop. Either way, post a `Business question` quoting its ID.
- **A business decision this Spec pack does not cover** is `DO NOT DECIDE` too: post a `Business question` for it.
- **A business call made anyway**, by you or your engineer: post a `Business call made in build`.
- People are named here by role. Post either shape as a comment on the work item this Spec pack was handed over with, or give it to your engineer to post.
- Stack, commands, repo layout and test seams are not in this Spec pack: the repo's `AGENTS.md` and your harness own those.

```text
Business question
IDs touched: <Requirement, Open item and Answer IDs>, HAL-EPC-002
Question: <the question, in one sentence>
Options seen: <each option, in a few words>
Default if forced: <the option you would take, and why>
Status: blocked | building around it (on a guess: <what>)
```

```text
Business call made in build
IDs touched: <Requirement, Open item and Answer IDs>, HAL-EPC-002
Decided: <what was decided>
Why: <one line>
Made by: agent | engineer
```

## 1. Problem and outcome

The hall takes deposits by bank transfer today, so a booking waits days to be confirmed. The book-and-pay Spec needs somewhere for an online deposit to go before a hirer can pay one.

**Outcome:** the hall has a card payment account the booking service can take a deposit into.

**Who:** the delivery team sets it up; hirers never see it directly.

## 2. Words used here

| Word | Meaning here |
| --- | --- |
| Deposit | The part of the hire fee paid up front to confirm a booking. |

## 3. Settled Decisions

None yet.

## 4. Rules and examples

### HAL-REQ-001 Confirmed once the deposit is paid

> A booking is confirmed only once its deposit has been paid.

- From: Stakeholder, hall committee chair, 2026-10-28

## 5. Still open: DO NOT DECIDE

None.

Parked (build nothing for these yet): None.

## 6. Constraints

- **HAL-REQ-002** (applies here too): The deposit is 20% of the hire fee, with a minimum of $50.

## 7. Depends on

None.

## 8. Scope

- **Goal:** the hall can take a deposit online.
- **Non-goals:** Not stated yet.
- **Left out of this Spec:** None.

## 9. Acceptance criteria (business terms)

- [ ] A test deposit of $50 paid by card reaches the hall's account (HAL-REQ-001, HAL-REQ-002).

---

## Appendix A: Decision coverage

For the Operator and the Sign-off view. Engineers can skip this.

| # | Category | State | Cites |
| --- | --- | --- | --- |
| 1 | Rules | settled | HAL-REQ-001, HAL-REQ-002 |
| 2 | Boundaries | settled | HAL-REQ-002 |
| 3 | Unwanted behaviour | settled | HAL-REQ-001 |
| 4 | States | settled | HAL-REQ-001 |
| 5 | Variants | settled | HAL-REQ-002 |
| 6 | Data | settled | HAL-REQ-001 |
| 7 | Permissions | settled | HAL-REQ-001 |
| 8 | Downstream | N/A | The Operator: the payment provider tells nothing else; the booking Spec reads its result. |
| 9 | Quality | settled | HAL-REQ-001 |
| 10 | Rollout | N/A | The Operator: there is no payment account today, so nothing moves over. |
| 11 | Examples | settled | worked from the rules in section 4 |

Quality: security settled (the payment provider holds the card details, HAL-REQ-001); performance, reliability, interaction capability, compatibility, maintainability, flexibility and safety settled as for the booking service.

## Appendix B: Pain points

None.
