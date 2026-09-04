# Canonical findings maintenance checkpoint — Toru NPC item ignore pending acceptance

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260904T150548Z`

## Live evidence

The current retrospective review plan `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0`, batch `b0137`, carries `cf-4f751c4f35d7c237` for source `彻(NPC)` / JP identity `徹` at `text_data_dict.json` path `152/179`. The finding remains a proper-name blocker with no canonical target; its review resolution is defer. The current translation `Toru (NPC)` is plausible but the repository evidence does not prove that reading authoritatively.

## Resolution implemented

- Added `scripts/harden_toru_npc_finding.py` at commit `0c26d77c2461320b98291f1a7b8d61c443a02f1e`.
- Added `tests/test_toru_npc_finding_hardening.py` at commit `d337b50773bbda9c858ebf359df0abad0ec39206`.
- The hardener creates an explicit `ignore` decision with `invalidation_scope: item`, `source_paths: [text_data_dict.json]`, `json_path_prefixes: [[152, 179]]`, and `match_mode: exact`.
- The regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()`.

This deliberately does **not** promote `Toru` (or another possible reading) to reusable canonical terminology. It removes only the systemic blocker for this exact one-off NPC item and leaves ordinary translation review responsible for its displayed text.

## Acceptance gate

For head `d337b50773bbda9c858ebf359df0abad0ec39206`:

- Validate run `33888533476`: in progress when checkpointed.
- Sync translation context run `33888533455`: pending when checkpointed.
- Sync translation review plan run `33888533508`: pending when checkpointed.

Do not increment `completed_count` until the production acceptance workflows succeed and regenerated live state confirms the item-scoped ignore persists.
