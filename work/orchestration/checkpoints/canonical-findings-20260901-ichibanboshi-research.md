# Canonical findings maintenance checkpoint — Ichibanboshi ga Kakeru Sora

Claim: `canonical-findings-maintenance-gpt56sol-hourly-20260901T090150Z`

Blocking finding: `cf-027a0f62d9583a5f` (`イチバン星が駆ける空`), exact match in `text_data_dict.json` category 16 (Song title).

## Verified identity

The source string is the official Japanese title of the ROAD TO THE TOP insert song released on 2023-05-10. Independent catalog/community references consistently identify it in Latin script as `Ichibanboshi ga Kakeru Sora`; the current Vietnamese semantic rendering `Bầu trời nơi ngôi sao số một lao đi` should not be treated as canonical proper-name identity.

Evidence checked:

- Umamusume Wiki: Japanese `イチバン星が駆ける空`, Latin title `Ichibanboshi ga Kakeru Sora`, ROAD TO THE TOP insert song.
- AWA commercial catalog: exact Japanese track `イチバン星が駆ける空`, release date 2023-05-10, performed by Narita Top Road / Admire Vega / T.M. Opera O.
- UtaTen gives the reading `いちばんぼしがかけるそら`.

## Intended hardening

Add a narrow category-16 song canonical/community lock:

- source alias: `イチバン星が駆ける空`
- preferred/accepted target: `Ichibanboshi ga Kakeru Sora`
- source path: `text_data_dict.json`
- JSON prefix: `16`
- match mode: `exact`
- invalidation scope: `item`

Also add an explicit terminology review lock to the same target and a regression test proving the finding resolves inside category 16 but not outside it. The production Sync translation context workflow already auto-runs `scripts/harden_*_finding.py` and `tests/test_*_finding_hardening.py`, so a new conforming hardener/test pair requires no workflow wiring change.

This is a partial checkpoint only; the finding is not complete until implementation, validation, production Sync persistence, and live-ledger canonical resolution are observed.
