# Canonical finding research — Matikanetannhauser `ごろりん！？パワードライブ`

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T0602Z`
Finding: `cf-51acc67fc17560ad` (`车轮滚滚！？动力驱动`)

## Identity

- Live finding evidence is inheritance-factor prose at text-data keys `10620201`–`10620203`.
- Repository character/costume metadata identifies `1062` as Matikanetannhauser and costume `106202` as `[蓝色・湍流]` / `[ブルー・タービュランス]`.
- Current JP references independently identify `[ブルー・タービュランス]マチカネタンホイザ`'s unique Skill as exactly `ごろりん！？パワードライブ`.
- The historical curation defer explicitly said the missing requirement was exact JP wording; that evidence gap is now closed.

## Canonical title

Lock `Lăn Tròn!? Power Drive`.

Rationale: `ごろりん` is the playful rolling/tumbling expression and `パワードライブ` is the stylized mechanical phrase `Power Drive`. This follows `glossary/skill_name_style.json`: use zh-CN for compact title rhythm, JP as semantic guard, preserve the title gimmick, and keep the result short instead of mechanically expanding the Chinese calque. Existing reviewed punctuation practice renders combined fullwidth `！？` naturally as `!?` in Vietnamese-facing titles.

The old current text `Bánh xe lăn bánh!? Truyền động mạnh mẽ` is forbidden because it over-expands both halves and treats `パワードライブ` as ordinary prose rather than title wordplay.

## Durable implementation

- Hardener: `scripts/harden_matikanetannhauser_tumbly_power_drive_finding.py`, commit `bd3d84e27a3170d87f228c53e18aade29e443cde`.
- Regression: `tests/test_matikanetannhauser_tumbly_power_drive_finding_hardening.py`, commit `318d6c7822bd0fae7c11b7e3dc3881e5ce10a246`.
- Rule is source-path scoped to `text_data_dict.json`, `match_mode: contains`, with item invalidation. The regression reconstructs the live finding's broad source-path scope, proves canonical/review resolution and `active_findings()` clearance, and proves an unrelated source file is not covered.

Do not mark complete until Validate and production Sync succeed, generated live state removes the finding from the actionable queue, and a second unchanged production Sync proves semantic no-op.
