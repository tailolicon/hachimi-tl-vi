# Training / Support canonical hardening checkpoint — 2026-08-29T12:22Z

Task: `canonical-training-support`
Stage: `domain_work`
Branch: `canonical-training-support-hardening`

## Preserved prior work

- Continued from `work/orchestration/checkpoints/canonical-training-support-20260829T1212Z.md`; did not restart the completed Friendship Training inventory.
- Existing hardener/test work for `Friendship Training` remains intact.

## New verified corpus findings

1. **Support Points resource**
   - `localize_dict.json` key `Common0160`
   - zh-CN: `支援点数`
   - historical VI: `Điểm Hỗ trợ`
   - Player-facing references consistently use `Support Points`; compact project convention is `Support Pt` for the UI label and `Support Points`/`Support Pts` may be accepted in prose.

2. **Career Energy gauge**
   - `localize_dict.json` key `SingleMode0006`: zh-CN `体力`, historical VI `Thể lực`
   - `SingleMode0074` / `SingleMode0075` are the corresponding Energy loss/recovery messages.
   - This is the training Energy resource, distinct from the `Stamina` race stat. Scope must stay on proven SingleMode keys so generic physical-strength prose is not rewritten.

3. **Friendship Gauge / historical `progress.bond` defect**
   - `text_data_dict.json` category `155`, e.g. ids `30287`–`30293`, uses `羁绊值` in Support Effect descriptions.
   - Existing canonical `progress.bond` globally locked bare `羁绊` to `Gắn kết`; this is overbroad and produces locked mismatches in gauge/value text.
   - Player-facing references use `Friendship Gauge`. Bare friendship/bond prose must remain unforced.

4. **Failure-rate UI located but not yet changed**
   - `localize_dict.json` key `SingleMode0036`: zh-CN `失败率`, historical VI `Tỷ lệ thất bại`.
   - Needs exact display-form decision before canonicalization; do not infer from guide prose alone.

## Branch changes in this session

- `e88b85ab513d30ee024bd93689b9db875af44758` — expanded `scripts/harden_training_support_canon.py` with scoped rules for Support Pt, Energy, Friendship Gauge and removal of the globally locked bare bond calque.
- `4d845e982a89e8487861a88b37d21b676b2ef78f` — expanded `tests/test_training_support_hardening.py` with positive/negative scope coverage and idempotence coverage.

No `localized_data/**` files were edited.

## Validation status

**Not yet validated. Do not treat the new canonical rules as complete.**

- Shiro/local execution backend failed first with HTTP 429, then MCP tunnel 404.
- Direct local Git clone also failed DNS resolution for `github.com`.
- Therefore focused pytest/full pytest/`tlvi validate` have not yet produced green evidence in this session.
- The glossary files have not yet been materialized by running the hardener; the script/test commits are durable preparation only.

## Next exact action

1. Obtain an execution path (preferred: temporary GitHub Actions bridge or restored local backend).
2. Run `python scripts/harden_training_support_canon.py`.
3. Run `pytest -q tests/test_training_support_hardening.py --tb=short`.
4. If green, run full `pytest -q --tb=short`, then `tlvi --db /tmp/tlvi.db validate` and `tlvi --db /tmp/tlvi.db index --out /tmp/index.json`.
5. Commit the generated `glossary/term_registry.json` and `glossary/ui_community_terms.json` only after validation.
6. Continue inventory for Training Level/facility level, training success/failure display forms, generic Support Effects, stat gain/bonus/cap wording.
