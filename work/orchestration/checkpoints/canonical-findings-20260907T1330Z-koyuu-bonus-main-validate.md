# Canonical finding checkpoint — 固有加成 main integration + Validate

Finding: `cf-5cc239af1c9d7710` (`固有加成`), with companion exact finding `cf-823a42e63df66f92`.

## Live-main integration

The canonical implementation is already durable on live `main`:

- `scripts/harden_support_unique_effect_label_finding.py`
- `tests/test_support_unique_effect_label_finding_hardening.py`

The main implementation is intentionally narrower than the earlier task-branch prototype: it uses `match_mode=contains`, `source_paths=[localize_dict.json]`, and `key_exact=[Character0050, Character0196]`. This still covers the reusable alias inside `固有加成详情` while preventing the label from overmatching other localize UI text or category-150 named Support unique effects.

## Acceptance evidence so far

Push head `c6ef7dce0e93ac20234c21f33d2197519bc816a8` triggered Validate run `34127589683`; it completed with conclusion `success`.

The production Context Sync run `34127589711` and review-plan Sync `34127589797` were also triggered for the same head and have not yet supplied final acceptance evidence at this checkpoint.

Do not increment `completed_count` yet. Continue with production Context Sync result, verify live canonical resolution / inactive finding, then obtain a second unchanged Sync semantic no-op proof.
