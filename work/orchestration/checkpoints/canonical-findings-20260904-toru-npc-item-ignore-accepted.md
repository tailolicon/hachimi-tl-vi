# Canonical findings maintenance checkpoint — Toru NPC item ignore accepted

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260904T150548Z`

## Accepted resolution

Finding `cf-4f751c4f35d7c237` for `彻(NPC)` / JP identity `徹` at `text_data_dict.json` path `152/179` is resolved as an exact item-scoped explicit ignore. This deliberately does not promote `Toru` or another possible reading to reusable canonical terminology.

Implementation:
- `scripts/harden_toru_npc_finding.py` — `0c26d77c2461320b98291f1a7b8d61c443a02f1e`
- `tests/test_toru_npc_finding_hardening.py` — `d337b50773bbda9c858ebf359df0abad0ec39206`

## Production acceptance

- Validate `33888533476`: success.
- Sync translation review plan `33888514856`: success.
- Sync translation context `33888514852`: success.
- Context Sync ran the Toru hardener before terminology apply with `changed=true`, ran it again after apply with `changed=false`, refreshed canonical findings, passed the full context pipeline (`683 passed`), and published generated context back to `main`.
- The regenerated live review batch `b0137` keeps the same Toru item but its `canonical_findings` array is now empty. Therefore the systemic canonical blocker has been removed while ordinary translation review remains responsible for the displayed text.

## Counter

This is one newly production-accepted maintenance unit. Advance `completed_count` from **101** to **102** exactly once.
