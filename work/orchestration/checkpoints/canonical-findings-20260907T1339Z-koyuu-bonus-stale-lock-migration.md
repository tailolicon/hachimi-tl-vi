# Canonical finding checkpoint — 固有加成 stale reviewed-lock migration

Finding: `cf-5cc239af1c9d7710` (`固有加成`) and companion `cf-823a42e63df66f92`.

Corrected Context Sync `34128281380` reached terminology-review application and failed safely before downstream canonical generation. The diagnostic was exact:

`decision audit.finding.support-unique-effect-label: term_id 'reviewed.source_bridge.826d2de05670' already maps to 'Hiệu ứng riêng', not 'Unique Effect'`

This proved an earlier generated reviewed lock remained in `term_registry.json`. The fix is implemented at the canonical hardener, not by patching generated/localized output:

- commit `87c431452688030c3c0e950e43b661b9dd0876a9` makes `scripts/harden_support_unique_effect_label_finding.py` explicitly own stable reviewed term id `reviewed.source_bridge.826d2de05670`, preserve the verified target `Unique Effect`, copy the narrow `contains` scope into the review decision, and idempotently migrate the stale reviewed registry term when present;
- commit `e5ac933eaaec3e18768d353fbb42d76032986238` adds regression coverage proving migration from historical `Hiệu ứng riêng`, idempotence, Character0050/Character0196 coverage, and negative scope outside the guarded localize keys.

Do not count complete until Validate + production Context Sync for a head including `e5ac933e...` succeeds, both findings are no longer active with `Unique Effect` resolution, and a subsequent unchanged Sync proves semantic no-op.
