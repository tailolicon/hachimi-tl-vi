# Canonical findings maintenance checkpoint — Toru NPC item ignore accepted

Finding `cf-4f751c4f35d7c237` covers source `彻(NPC)` / JP identity `徹` at `text_data_dict.json` path `152/179`. The current translation `Toru (NPC)` is plausible, but repository evidence does not prove that reading authoritatively.

## Resolution implemented

- Added `scripts/harden_toru_npc_finding.py` at commit `0c26d77c2461320b98291f1a7b8d61c443a02f1e`.
- Added `tests/test_toru_npc_finding_hardening.py` at commit `d337b50773bbda9c858ebf359df0abad0ec39206`.
- The hardener creates an explicit `ignore` decision with `invalidation_scope: item`, `source_paths: [text_data_dict.json]`, `json_path_prefixes: [[152, 179]]`, and `match_mode: exact`.
- The regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()`.

This deliberately does **not** promote `Toru` (or another possible reading) to reusable canonical terminology. It removes only the systemic blocker for this exact one-off NPC item and leaves ordinary translation review responsible for its displayed text.

## Production acceptance

For head `d337b50773bbda9c858ebf359df0abad0ec39206`:

- Validate run `33888533476`: completed successfully.
- Sync translation context run `33888533455`: completed successfully.
- Sync translation review plan run `33888533508`: completed successfully.
- Live active review plan `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0`, batch `b0137`, now contains the `152/179` item with `source_text: 彻(NPC)` and `canonical_findings: []`.

Acceptance complete. Maintenance completion count advances from 105 to 106. Do not canonize `Toru` from this evidence and do not broaden the ignore beyond exact item `152/179`.
