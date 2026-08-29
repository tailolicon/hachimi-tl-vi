# Training / Support canonical hardening — ready for finalize checkpoint

Task: `canonical-training-support`
Stage reached: `ready_for_finalize`
Branch: `canonical-training-support-hardening`
Validated materialized branch head before cleanup: `74c23a4cd20a76dc93648a69b3ead3480401a21d`
Temporary-workflow cleanup commit: `778dce6cf8317a6e1e6562a67def4dfee491c695`

## Substantive canonical work completed

The domain now has scoped permanent canonical coverage/regression tests for the high-frequency player-facing Training / Support concepts established during this hardening task, including:

- Friendship Training;
- Support Pt;
- Energy / Max Energy;
- Friendship Gauge (category-155 support effects) while disabling the ambiguous global bare Bond lock;
- Training Level;
- Failure Rate;
- Support Effects heading;
- Stat Cap;
- Friendship Bonus;
- Training Effectiveness;
- Mood Effect, including both `干劲效果提升` and the conditional-support alias `心情加成`;
- Initial Friendship;
- Specialty Priority;
- Speed / Stamina / Power / Guts / Wit Bonus;
- Skill Pt Bonus.

All newly-added Support Effect rules are limited to `text_data_dict.json` category `155`, with negative regression coverage so ordinary story prose is not treated as a system label. No `localized_data/**` examples were patched.

## Evidence from this run

- Live Audit Round 1 context was shown to be stale for Friendship Gauge (`羁绊值` still inherited legacy `progress.bond -> Gắn kết`), confirming the need for final production review-plan rebuild/Sync after integration.
- Current corpus examples directly confirmed repeated category-155 labels such as `友情加成`, `训练效果提升`, `干劲效果提升`, `得意率提升`, `速度加成`, `耐力加成`, `力量加成`, `技能Pt加成`, and conditional `心情加成`.
- GitHub Actions run `33257080780` validated the first expanded effect-label set: 26 focused tests and 193 full tests passed; `tlvi validate` and index were clean; generated glossary was persisted.
- GitHub Actions run `33257177114` passed after adding the conditional Mood Effect alias and persisted the resulting glossary. All materialize/focused/full/CLI steps and the persistence step succeeded.
- Temporary validation workflow was removed after validation, so it is not part of the permanent integration set.

## Deliberate non-locks

- Scenario prose such as `当设施达到 Lv3 时` is not a standalone canonical Training Level/Facility Level label; it was intentionally left as prose to avoid overmatching.
- `提示获得数提升` appears in support-effect prose, but this exact source wording was not promoted to a canonical Hint Level/Frequency term because the repository evidence in this pass does not establish that it is semantically identical to either standard label. Do not guess it during finalization; only reopen domain work if concrete evidence establishes a systemic mapping.

## Finalizer contract

Do not restart Training/Support inventory. Finalization should only:

1. integrate the permanent hardeners, tests, and materialized glossary changes onto live `main` while preserving concurrent main changes;
2. run full validation;
3. rebuild the review plan/context;
4. run production Sync and then a second unchanged no-op Sync proof;
5. spot-check representative positive and negative Training/Support contexts, including Friendship Gauge and category-155 Support Effects;
6. mark this domain complete and activate the next canonical-hardening roadmap task.
