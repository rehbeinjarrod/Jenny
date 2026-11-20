# <CODE>-EPC-<nnn> · <Title>

Code: <CODE>
Epic: <CODE>-EPC-<nnn>
Feature: <CODE>-FEA-<nnn>
<Only for a Technical Enabler, otherwise leave these two lines out:> Technical Enabler: yes
<Only for a Technical Enabler: the active Requirement IDs it enables, comma-separated; left out only beside the pain point line below:> Enables: <CODE>-REQ-<nnn>, <CODE>-REQ-<nnn>
<Only for a pain point kept with the Operator's reason, otherwise leave this line out:> Pain point: <second Epic in <CODE>-FEA-<nnn> | horizontal Feature | Technical Enabler enabling no Requirement>: <the Operator's reason>

## Covers

- <Requirement IDs this Epic delivers, comma-separated, each written in full>

<For a Technical Enabler, the section holds the one line `None.` in place of the list above.>

## Applies here too

<- <Requirement ID> (<a short title in your own words, e.g. "Refunds over $500 need a manager">): covered by <Epic ID>; this Epic must obey it.> or None.

## Depends on

<- <Requirement or Epic ID> (<a short title in your own words, e.g. "Refunds over $500 need a manager">): must be built before this Epic can work.> or None.

<Only once the Epic holds an Enabler Story, otherwise leave this section out:>
## Enabler Stories

- **<CODE>-ENS-<nnn>** <the enabler's name> · Enables: <Requirement IDs | none> · Depends on: <Enabler Story or Epic IDs | none>

## External items

None yet.

<Written by the `handoff` skill in place of "None yet.", and moved to a new version by `pack`; `slice` never writes it:> - Tech face: [<Jira key>](<URL>) · Pack: pack-v<N>.md · Handed off: <YYYY-MM-DD>

## Left out

<- <Requirement ID> (<a short title in your own words, e.g. "Refunds over $500 need a manager">): <why it is not in this Epic and where it is instead>> or None.

<Only once the Operator marks a Decision coverage category N/A, otherwise leave this section out:>
## Not applicable

- **<Category>**: <the Operator's reason, in their words> · Marked: <YYYY-MM-DD>
