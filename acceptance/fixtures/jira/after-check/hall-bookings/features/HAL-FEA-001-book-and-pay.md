# HAL-FEA-001 · Book and pay

Code: HAL
Feature: HAL-FEA-001

A hirer books the main hall online at the member or non-member rate and pays a deposit to confirm the booking.

## Requirements

- **HAL-REQ-001** A booking is confirmed only once its deposit has been paid. · Source: HAL-SRC-001 · Status: active
- **HAL-REQ-002** The deposit is 20% of the hire fee, with a minimum of $50. · Source: HAL-ANS-001 · Status: active
- **HAL-REQ-003** The main hall costs $30 an hour for members and $45 an hour for non-members. · Source: HAL-SRC-001 · Status: active
- **HAL-REQ-004** Members can book up to six months ahead; non-members up to three months ahead. · Source: HAL-SRC-001 · Status: active
- **HAL-REQ-014** An unpaid booking holds its slot for 30 minutes, then the slot is released for others to book. · Source: HAL-ANS-004 · Status: active
- **HAL-REQ-015** Each booking takes its own deposit, even when the same hirer books twice on one day. · Source: HAL-ANS-005 · Status: active
