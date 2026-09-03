# Canonical finding checkpoint — Senior Autumn Triple Crown

Claim: `canonical-findings-maintenance-gpt56sol-20260903T110239Z`

Target finding: `cf-97dd9d6e5657d6f9` (`秋古马三冠` → **Senior Autumn Triple Crown**).

## Live finding state

The live `main` canonical-findings blob shows this finding as `status: open`, `match_mode: contains`, scoped to `text_data_dict.json`, with `canonical_resolution: null` and `review_resolution: null`. The reported evidence is the compound title `秋古马三冠赛马娘`, while retrospective batches also contain the standalone `秋古马三冠` label.

## Hardening decision

Add community term `achievement.senior_autumn_triple_crown` with source alias `秋古马三冠`, preferred/accepted target `Senior Autumn Triple Crown`, `source_paths: [text_data_dict.json]`, and `match_mode: contains`. This preserves the existing English Triple Crown naming pattern and resolves the embedded compound title without leaking the alias into unrelated source files.

Add explicit terminology review decision `audit.finding.senior-autumn-triple-crown` locking `秋古马三冠` to `Senior Autumn Triple Crown`.

## Regression coverage

`tests/test_senior_autumn_triple_crown_finding_hardening.py` verifies:

- hardener idempotence;
- the exact live finding shape resolves through the new community term;
- the reviewed lock is present;
- the same alias does not obtain a canonical resolution outside `text_data_dict.json`.

## Acceptance state

Implementation and regression test are published. Full repository/Sync validation remains required before counting the finding complete.
