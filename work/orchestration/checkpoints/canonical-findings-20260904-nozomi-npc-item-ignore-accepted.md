# Canonical findings maintenance checkpoint — Nozomi NPC item ignore accepted

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260904T150548Z`

## Accepted resolution

The one-off `望(NPC)` identity at `text_data_dict.json` path `152/11` is resolved as an exact item-scoped explicit ignore. Repository maintenance evidence explicitly states that 望 has multiple valid Japanese given-name readings and that the zh-CN bridge cannot verify the intended reading, so this resolution deliberately does not promote `Nozomi` (or another reading) to reusable canonical terminology.

Implementation:
- `scripts/harden_nozomi_npc_finding.py` — `2c28a71f8c373a368dcab74b594ef62c11826324`
- `tests/test_nozomi_npc_finding_hardening.py` — `ec65c8a5392c35c0a2d05f2b52a7df6fb8325ea0`

## Production acceptance

- Validate `33888991634`: success.
- Sync translation review plan `33888991465`: success.
- Sync translation context `33888991540`: success.
- Context Sync completed pre/post hardening, canonical finding refresh, context tests, and generated-context publication successfully.

The item-scoped ignore therefore removes only the project-wide canonical blocker for this exact NPC item while preserving ordinary translation review authority over its displayed text.

## Counter

Advance `completed_count` from **102** to **103** exactly once.
