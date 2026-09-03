# Canonical finding implementation — 中盤巧者

Finding: `cf-b1ad218e98fca601`
Source zh-CN: `中盘巧者`
Verified JP identity: `中盤巧者`
Canonical target: `Bậc thầy giữa chặng`

## Evidence

- Pinned Skill 202792 is Japanese `中盤巧者`.
- Existing repository curation locks `下り坂巧者` → `Bậc thầy xuống dốc`, establishing the Skill-title convention `巧者` → `Bậc thầy`.
- The current Vietnamese title `Bậc thầy giữa chặng` is therefore consistent with both the verified JP identity and the existing Skill-name family.

## Implementation

- Hardener commit `5db344ff40237f0aaa12c29e86d72013d6b73f4e` adds `scripts/harden_chukoban_kosha_finding.py`.
- Regression-test commit `a2ae2ef9c81bd31db38db62d7427b4649552d3e1` adds `tests/test_chukoban_kosha_finding_hardening.py`.
- Rule scope is exact `中盘巧者`, `text_data_dict.json`, JSON-path prefix `147`, item invalidation only. This avoids normal mid-race prose overmatch.

## Acceptance status — 2026-09-03T20:16:12Z

- Validate run `33800614067` for regression-test commit `a2ae2ef9c81bd31db38db62d7427b4649552d3e1` completed successfully.
- Production Sync translation context run `33800614065` completed successfully.
- Live `glossary/ui_community_terms.json` now contains rule `skill.chukoban_kosha.mid_race_expert` with exact zh-CN alias `中盘巧者` and preferred target `Bậc thầy giữa chặng`, confirming the hardener executed in production.
- Sync translation review plan run `33800614096` remains `pending` as of `2026-09-03T20:16:12Z`.
- Live `work/parallel_state.json` still reports active plan `tr-p3-67f8551f7780-7c7282227fdf-b5c0bcb3bd-0461707f55`, updated at `2026-09-03T20:08:13.172655Z`, which predates the hardening commits. Therefore it cannot yet be used to prove that `cf-b1ad218e98fca601` stopped blocking the refreshed review plan.

## Remaining acceptance

Wait for a production translation-review-plan refresh that includes the hardening state, then verify the refreshed plan no longer carries `cf-b1ad218e98fca601` as an active blocking finding. Only after that verification increment the maintenance completion count from 44 to 45 and route to the next canonical finding. Do not count this finding complete before that final check.
