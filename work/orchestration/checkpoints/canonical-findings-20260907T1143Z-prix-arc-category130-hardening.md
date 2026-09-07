# Canonical findings maintenance checkpoint — Prix de l'Arc de Triomphe category-130 hardening

Finding: `cf-766f1b21e2a91de1` (`凯旋门赏`)
Canonical target: `Prix de l'Arc de Triomphe`

## Live diagnosis

The existing locked race identity `race.prix_arc_de_triomphe` already establishes zh-CN `凯旋门赏` / JP `凱旋門賞` as `Prix de l'Arc de Triomphe`, but the base structured-race rule is intentionally scoped to text-data categories 32/33/111. The active finding was emitted from `text_data_dict.json` category 130, entry 291, source `凯旋门赏赛马娘`, where the current text `Uma Musume Khải Hoàn Môn` loses the verified race identity.

The finding itself has source-path scope but no json-path prefix, so merely adding category 130 to the structured race registry would not satisfy canonical-finding coverage semantics. A supplemental proper-name reference rule is therefore used: exact alias `凯旋门赏`, `match_mode=contains`, source-scoped to `text_data_dict.json`, item-scoped invalidation. This covers race-name references in text data, including category 130, without exposing the rule to `localize_dict.json`. The unrelated Skill alias `凯旋` remains exact-only and cannot consume `凯旋门赏`.

## Durable implementation

- `7d74dae648a64ce898091e3394be3c0017671517` adds `scripts/harden_prix_arc_category130_finding.py` with the supplemental reference rule and reviewed lock.
- `4d74917f27a9c63fd2c2ecc957e8eb1341c7dda9` adds `tests/test_prix_arc_category130_finding_hardening.py`.
- Targeted local regression run from live `main` archive: `18 passed` across the new finding test plus `tests/test_race_hardening.py`.

## Acceptance status

Production Context Sync and repository Validate/review-plan gates triggered by the new source/test commits are still pending. Do **not** increment maintenance `completed_count` yet. Completion requires live canonical resolution, green production gates, then a second unchanged Context Sync proving `Context is already current.`
