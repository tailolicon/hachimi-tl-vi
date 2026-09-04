# Canonical finding acceptance: 進 / 进(NPC)

Finding: `cf-0ed1b3254699aa40`

## Resolution

The source item `进(NPC)` at `text_data_dict.json` path `152/141` represents the one-off NPC display name `進`. The existing Vietnamese text uses `Susumu (NPC)`, but the repository evidence and public-source research available in this maintenance pass did not establish the NPC's specific Japanese reading strongly enough to promote `Susumu` (or another reading) into reusable canonical terminology.

The finding is therefore resolved with an exact, item-scoped `ignore` review disposition:

- decision: `audit.finding.npc-susumu-unverified-reading`
- action: `ignore`
- invalidation scope: `item`
- source path: `text_data_dict.json`
- JSON path prefix: `152/141`
- match mode: `exact`
- no canonical Romanization is created

Implementation:

- `scripts/harden_susumu_npc_finding.py`
- `tests/test_susumu_npc_finding_hardening.py`
- implementation head: `0d0730f75046d4946144a8bfd953bcb3ce360012`

## Acceptance evidence

- Validate run `33882727994`: success.
- Sync translation context run `33882728021`: success.
- Sync translation review plan run `33882728107`: success.
- Regenerated `glossary/terminology_reviews.json` contains `audit.finding.npc-susumu-unverified-reading`.
- Regenerated `glossary/canonical_findings.json` keeps `canonical_resolution: null` and records `review_resolution.action: ignore`, so this one-off ambiguity no longer remains an active systemic blocker.

## Maintenance progress

This acceptance raises the durable canonical-findings maintenance count from **98 to 99** accepted findings.
