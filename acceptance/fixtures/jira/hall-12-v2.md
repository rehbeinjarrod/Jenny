# What the Atlassian MCP returned for HALL-12, its child work items and their comments

Site: https://example.atlassian.net

## HALL-12 · Epic · Book and pay

URL: https://example.atlassian.net/browse/HALL-12
Status: In Progress · Created: 2026-11-07 · Updated: 2026-11-07

Description:

> Build from the Spec pack for HAL-EPC-001, v1 (attached). Business questions and business calls go as comments here or on the Stories.

Comments: none.

## HALL-13 · Story · Book the hall online · parent HALL-12

URL: https://example.atlassian.net/browse/HALL-13
Status: In Progress · Created: 2026-11-07 · Updated: 2026-11-10

Description:

> A hirer picks a date and time, sees the hire fee at their rate, and books the main hall.

### Comment 10231 · Ravi Kumar · created 2026-11-10 · updated 2026-11-10

> Business question
> IDs touched: HAL-REQ-001, HAL-REQ-002, HAL-EPC-001
> Question: When a hirer books the hall twice on the same day (say a morning and an evening), do they pay one deposit or a deposit for each booking?
> Options seen: one deposit covering both; a deposit for each booking
> Default if forced: a deposit for each booking, so each booking stands on its own
> Status: building around it (on a guess: a deposit for each booking)

### Comment 10235 · Ravi Kumar · created 2026-11-10 · updated 2026-11-10

> PR for the booking form is up for review. Moving to testing tomorrow.

## HALL-14 · Story · Take the deposit · parent HALL-12

URL: https://example.atlassian.net/browse/HALL-14
Status: In Progress · Created: 2026-11-07 · Updated: 2026-11-12

Description:

> Take the deposit by card when the hirer books. The booking is confirmed once it is paid.

### Comment 10238 · Priya Shah · created 2026-11-11 · updated 2026-11-11

> Business call made in build
> IDs touched: HAL-REQ-001, HAL-EPC-001
> Decided: an unpaid booking holds its slot for 30 minutes; if the deposit is not paid by then, the slot is released for others to book.
> Why: an abandoned checkout would otherwise block the hall for everyone.
> Made by: engineer

### Comment 10247 · Priya Shah · created 2026-11-12 · updated 2026-11-12

> Business question
> IDs touched: HAL-ANS-001, HAL-REQ-002, HAL-REQ-003, HAL-EPC-001
> Question: HAL-ANS-001 sets a $50 minimum deposit, but a one-hour member booking costs $30, so the deposit would be more than the whole hire fee. Should the deposit be capped at the hire fee?
> Options seen: cap the deposit at the hire fee; keep the $50 minimum and charge more than the fee
> Default if forced: cap the deposit at the hire fee
> Status: building around it (on a guess: the deposit is capped at the hire fee)
