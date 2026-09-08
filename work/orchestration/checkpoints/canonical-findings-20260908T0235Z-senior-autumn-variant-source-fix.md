# Canonical finding checkpoint — Senior Autumn Triple Crown zh-CN variant

Finding: `cf-80ddcbc78531435e` (`古马级秋三冠`) in `text_data_dict.json` category `111`.

The live repository already has the canonical achievement `achievement.senior_autumn_triple_crown` with player-facing target `Senior Autumn Triple Crown`, but it previously recognized only the zh-CN surface `秋古马三冠`. The open finding is the equivalent standalone source variant `古马级秋三冠`; its current mixed Vietnamese calque is `Tam quán mùa thu Hạng Senior`.

Durable source fix:
- `9c82c88ba205302b66d0ee07cbca9a50f5e2c22b` adds `古马级秋三冠` as a source alias of the existing scoped `achievement.senior_autumn_triple_crown` community rule, keeps scope at `text_data_dict.json`, and marks the mixed Vietnamese form forbidden.
- `26dc97fdbf93eafc97f30f81aa026c253e3feed7` adds regression coverage proving `refresh_canonical_resolutions` resolves the exact variant to `Senior Autumn Triple Crown` while retaining the existing source-file scope guard.

Maintenance accounting remains `208`. Do not count `cf-80ddcbc78531435e` complete until production Validate/Context Sync succeeds, an unchanged/no-op Context Sync succeeds, a fresh translation-review plan rebuild succeeds, and the live finding is no longer returned by `scripts/canonical_findings.py::active_findings`.

The earlier deferred `cf-55f0e8a1d70264a2` (`等级奖牌`) remains unresolved; do not guess its identity without new authoritative evidence.
