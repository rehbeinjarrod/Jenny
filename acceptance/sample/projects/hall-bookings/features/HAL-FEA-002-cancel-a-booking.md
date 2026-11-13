# HAL-FEA-002 · Cancel a booking

Code: HAL
Feature: HAL-FEA-002

A hirer cancels a booking online and gets back all or part of the deposit, depending on how much notice they give.

## Requirements

- **HAL-REQ-005** A hirer who cancels at least 48 hours before the booking starts gets the whole deposit back. · Source: HAL-SRC-001 · Status: active
- ~~**HAL-REQ-006** A hirer who cancels less than 48 hours before the booking starts loses the whole deposit. · Source: HAL-ANS-002 · Status: withdrawn~~ · Withdrawn 2026-11-08 · Reason: the committee changed its Decision (HAL-ANS-002 replaced by HAL-ANS-003) · Replaced by: HAL-REQ-007
- **HAL-REQ-007** A hirer who cancels less than 48 hours before the booking starts gets half the deposit back. · Source: HAL-ANS-003 · Status: active
