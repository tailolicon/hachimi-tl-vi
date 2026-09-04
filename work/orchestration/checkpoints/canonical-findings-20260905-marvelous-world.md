# Canonical finding checkpoint — Marvelous Sunday unique Skill

Finding: `cf-1c047ac10a89e52a`
Source zh-CN alias: `万彩☆美丽★世界`
Verified JP identity: `万彩☆マーベラス★世界` (Skill 100551, Marvelous Sunday unique Skill)
Canonical target: `Vạn Sắc☆Marvelous★World`

## Live diagnosis

The generated retrospective finding was a source-bridge blocker with historical review action `defer`, backed by category-147 Skill-name keys `10550101`, `10550102`, and `10550103`.

Repository curation evidence explicitly warns that zh-CN `万彩☆美丽★世界` semantically replaces the JP character keyword `マーベラス` with generic `美丽`, so a literal bridge-derived Vietnamese title is unsafe. Independent JP Skill references identify Skill 100551 as `万彩☆マーベラス★世界`, the unique Skill of Marvelous Sunday.

The canonical target `Vạn Sắc☆Marvelous★World` keeps the title's `万彩` imagery, preserves `Marvelous` as the character-specific stylized keyword, and retains the `☆` / `★` punctuation. The historical calque `Vạn sắc☆Thế giới★Tươi đẹp` is forbidden because it loses that identity.

## Durable repair

- `scripts/harden_marvelous_world_finding.py` adds an exact, category-147 source-path-scoped community Skill identity and reviewed lock.
- Implementation commit: `d08377e011d92d5de36e5aa9eb84babdccedcc1d`.
- `tests/test_marvelous_world_finding_hardening.py` covers idempotence, replacement of the historical defer, resolution of the live finding shape, and negative category-prefix coverage.
- Regression commit: `dd3febfe15663475145a0fcc62342ff64af9c178`.
- Both regression functions also passed in the local repository environment (`manual_regressions=2 passed`).

## Production acceptance status

- Validate run `33912686400`: success on regression head `dd3febfe15663475145a0fcc62342ff64af9c178`.
- Context Sync run `33912686323`: success.
- Context regeneration commit `8a2f0ffc434f80a0724edef26be89b7188d01d17` persists the canonical artifacts.
- Live `glossary/canonical_findings.json` now resolves `cf-1c047ac10a89e52a` to `Vạn Sắc☆Marvelous★World` with reviewed lock `audit.finding.skill-marvelous-sunday-myriad-world`; it is no longer an active canonical finding.
- Review-plan run `33912686378` remains queued/pending. The latest durable active-plan generation visible at this checkpoint is `3511f5d5ad12b687bdf6c1c671d4b390a121dacb`, generated `2026-09-04T19:43:44.800076Z`, which predates the Marvelous context regeneration and therefore cannot be used as its final acceptance gate.

Do not increment maintenance `completed_count` from 122 to 123 yet. Require a production review-plan regeneration newer than context commit `8a2f0ffc434f80a0724edef26be89b7188d01d17`, then verify the regenerated plan no longer exposes this blocker. Dream Journey `cf-1900e9e9aa8bd7ec` is already fully accepted and counted as 122.
