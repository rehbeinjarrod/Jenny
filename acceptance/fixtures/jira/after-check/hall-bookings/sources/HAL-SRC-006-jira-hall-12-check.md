# HAL-SRC-006 · Jira check of HALL-12: Book and pay

Kind: Jira item
Owner: Ravi Kumar, Priya Shah
Date: 2026-11-11
URL: https://example.atlassian.net/browse/HALL-12
Read: 2026-11-12
Kept: word for word, parts used

HALL-13 · comment 10231 · Ravi Kumar · 2026-11-10

> Business question
> IDs touched: HAL-REQ-001, HAL-REQ-002, HAL-EPC-001
> Question: When a hirer books the hall twice on the same day (say a morning and an evening), do they pay one deposit or a deposit for each booking?
> Options seen: one deposit covering both; a deposit for each booking
> Default if forced: a deposit for each booking, so each booking stands on its own
> Status: building around it (on a guess: a deposit for each booking)

HALL-14 · comment 10238 · Priya Shah · 2026-11-11

> Business call made in build
> IDs touched: HAL-REQ-001, HAL-EPC-001
> Decided: an unpaid booking holds its slot for 30 minutes; if the deposit is not paid by then, the slot is released for others to book.
> Why: an abandoned checkout would otherwise block the hall for everyone.
> Made by: engineer
