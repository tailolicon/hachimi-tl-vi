# Canonical finding checkpoint — Marvelous Sunday unique Skill

Finding: `cf-1c047ac10a89e52a`
Source zh-CN alias: `万彩☆美丽★世界`
Verified JP identity: `万彩☆マーベラス★世界` (Skill 100551, Marvelous Sunday unique Skill)
Canonical target: `Vạn Sắc☆Marvelous★World`

## Live diagnosis

The live finding is an active source-bridge blocker under `scripts/canonical_findings.py::active_findings`: status `open`, no canonical resolution, and historical review action `defer`. Its three evidence rows are category-147 Skill-name keys `10550101`, `10550102`, and `10550103`.

Repository curation evidence explicitly warns that zh-CN `万彩☆美丽★世界` semantically replaces the JP character keyword `マーベラス` with generic `美丽`, so a literal bridge-derived Vietnamese title is unsafe. Independent JP Skill references identify Skill 100551 as `万彩☆マーベラス★世界`, the unique Skill of Marvelous Sunday.

The canonical target `Vạn Sắc☆Marvelous★World` keeps the title's `万彩` imagery, preserves `Marvelous` as the character-specific stylized keyword, and retains the `☆` / `★` punctuation. The historical calque `Vạn sắc☆Thế giới★Tươi đẹp` is forbidden because it loses that identity.

## Durable repair

- `scripts/harden_marvelous_world_finding.py` adds an exact, category-147 source-path-scoped community Skill identity and reviewed lock.
- Implementation commit: `d08377e011d92d5de36e5aa9eb84babdccedcc1d`.
- `tests/test_marvelous_world_finding_hardening.py` covers idempotence, replacement of the historical defer, resolution of the live finding shape, and negative category-prefix coverage.
- Regression commit: `dd3febfe15663475145a0fcc62342ff64af9c178`.
- Both regression functions also passed in the local repository environment (`manual_regressions=2 passed`).

## Acceptance status

Do not increment maintenance `completed_count` for this finding yet. Verify production Validate + Context Sync + post-context Review-plan Sync, then confirm the regenerated live canonical finding resolves to the reviewed canonical target and disappears from active-finding ordering.

Dream Journey `cf-1900e9e9aa8bd7ec` has already passed Validate `33911976141` and Context Sync `33911976182`; live regenerated canonical findings resolve it to `Cõi Bạc Trong Mộng`. Its completion count is still waiting for a post-context review-plan success before incrementing from 121 to 122.
