# CRT-FEA-001 · Book and cancel a court

Code: CRT
Feature: CRT-FEA-001

A customer books a court online, pays in full, and can cancel for a refund that depends on notice.

## Requirements

- **CRT-REQ-001** A court booking is paid in full when it is made; there is no deposit. · Source: CRT-SRC-001 · Status: active
- **CRT-REQ-002** A customer who cancels at least 24 hours before the booking starts gets a full refund. · Source: CRT-SRC-001 · Status: active
- **CRT-REQ-003** A customer who cancels less than 24 hours before the booking starts gets no refund. · Source: CRT-SRC-001 · Status: active
- **CRT-REQ-004** If the centre cancels a booking, the customer gets a full refund and a $20 credit towards their next booking. · Source: CRT-SRC-001 · Status: active
