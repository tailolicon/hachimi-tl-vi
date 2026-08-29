# canonical-resources-gacha-shop — W2 ready-for-integration checkpoint

- Task: `canonical-resources-gacha-shop`
- Domain stage at handoff: `ready_for_finalize` / ready for serial integration
- Domain branch: `canonical-resources-gacha-shop-hardening`
- Clean branch head after TEMP workflow removal: `b9a3393b840a786a4118e81eaca5288eca154044`
- Last fully validated/materialized parent: `e2b17b9276a6873f85e8d2101e42efc5cc0bf5da`
- Validation run: GitHub Actions `33262077689`

## Permanent scope completed

Resources/Gacha/Shop canonical hardening now covers the stable, repeated player-facing identities evidenced in the pinned corpus:

- `金币` -> **Monies**, scoped to `localize_dict.json` so ordinary money/gold prose stays negative.
- `蹄铁` -> **Cleat/Cleats**, scoped to localize UI; Rainbow/Gold/Silver Cleat labels are regression-covered.
- paid/free Jewel distinctions (`付费宝石` / `免费宝石` and variants).
- Gacha pity `兑换点数` / `兑换Pt` -> **Exchange Points**, Gacha-key scoped.
- `四叶草` -> **Clovers** in Gacha/Shop resource UI.
- `女神像` -> **Goddess Statues** in Gacha/Shop resource UI.
- `社团点数` -> **Club Points** at the directly evidenced `StoryEvent4080030` key; intentionally not broadened without additional proven contexts.
- `友情点数` -> **Friend Points** in TeamStadium localize UI.
- generic Gacha `抽奖券` -> **Scout Ticket**, while named/event-specific vouchers remain outside the generic lock.
- `结晶片` / `彩虹结晶片` / `金色结晶片` -> **Crystal Shards / Rainbow Crystal Shards / Gold Crystal Shards**, exact-key scoped to `Shop420161`–`Shop420163`.

Permanent files include:

- `scripts/harden_resources_gacha_shop_canon.py`
- `scripts/harden_crystal_shard_canon.py`
- `glossary/source_bridge_terms.json`
- `tests/test_resources_gacha_shop_hardening.py`
- `tests/test_resources_gacha_shop_stable_resources.py`
- `tests/test_crystal_shard_hardening.py`
- `tests/test_translation_review_source_bridge.py`

The source-bridge regression contract was updated so legacy Monies/Cleats tests supply their intended localize/UI context rather than forcing the newly scoped rules to behave globally. This preserves both UI positives and prose negatives.

## Representative corpus evidence

- `Gacha0001` / `Gacha0002`: `兑换点数` currently literalized as Vietnamese exchange points phrasing.
- `Gacha0022` / `Gacha0023`: abbreviated `兑换Pt` usage.
- `Gacha0032`: unused Exchange Points convert to `四叶草`.
- `Gacha0065` / `Gacha0066`: generic single / 10-pull `抽奖券` labels.
- `Gacha0067`: `女神像` resource wording.
- `Shop0130`–`Shop0132`: Rainbow / Gold / Silver Cleat labels.
- `StoryEvent4080030`: `社团点数兑换`.
- `TeamStadium0090`: `友情点数`.
- `Character0212`, `Character0214`, `Character0220`: `金币` in player-facing upgrade/resource contexts.
- `Shop420161`: `结晶片兑换`.
- `Shop420162`: `彩虹结晶片`.
- `Shop420163`: `金色结晶片`.

## Validation evidence

Actions run `33262077689` completed successfully on the permanent content before TEMP-workflow cleanup:

- 30 focused tests passed;
- 211 full tests passed;
- `tlvi validate` returned `ok: true`, no errors or warnings;
- both resource hardeners were idempotent;
- materialization persisted `glossary/source_bridge_terms.json` at commit `e2b17b9276a6873f85e8d2101e42efc5cc0bf5da`.

The only subsequent branch commit, `b9a3393b840a786a4118e81eaca5288eca154044`, deletes the temporary validation workflow. No permanent canonical/test content changed after the green run.

## Intentional non-locks / ownership boundaries

- Broad `兑换券` is heterogeneous across trainee/support-card selection vouchers and event-entry tickets, so it is not globally canonicalized.
- One-off event currencies are not locked merely to grow the glossary.
- Generic owned/required/cost/insufficient/acquisition/exchange wording was audited but remains natural UI text or belongs to Common UI/System; this domain does not force English for those generic controls.
- Support Pt remains owned by the completed Training/Support substantive work rather than duplicated here.
- No `localized_data/**` examples were patched directly.
- No TEMP inventory/staging/validation workflow remains on the domain branch.

## Serial integration handoff

The primary integration lane should selectively integrate the permanent files above onto live `main` while preserving concurrent main changes, then run integrated full validation, rebuild retrospective review context, run production Sync plus a second unchanged no-op Sync, and spot-check representative resource positives/negatives. Do not restart broad Resources/Gacha/Shop research unless integration produces concrete evidence of a substantive unresolved domain defect.
