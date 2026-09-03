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

## Remaining acceptance

Verify Validate succeeds, production Sync executes the hardener, and the subsequent translation-review plan refresh no longer carries `cf-b1ad218e98fca601` as an active blocking finding. Do not increment the maintenance completion count before those checks pass.
