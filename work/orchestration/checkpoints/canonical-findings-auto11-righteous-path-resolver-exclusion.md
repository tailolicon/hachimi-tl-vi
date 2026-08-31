# Canonical findings maintenance checkpoint

- task: `canonical-findings-maintenance`
- finding: `cf-1bd479584e40d767`
- source: `永井正道`
- completed_count: `116`
- previous_completed_count: `115`
- status: resolved

## Durable work

- Existing runtime hardener: `fcc963978694bd2a266e9e855e99a95df1c86e94`
- Existing overlap regression: `9bf246e7f13924cf38aba0ae4a73c65e73840ab3`
- Resolver exclusion fix: `ecb2282094286c413199bd20b080a52900d792c5`
- Resolver regression: `8d82d66fcbf58c40471b098d6dda26bca9933065`

## Verification

The canonical-finding resolver now applies `exclude_source_exact` and `exclude_source_contains` before accepting a canonical rule as coverage. This prevents the valid Skill rule `正道 -> Chính đạo` from resolving the creator name `永井正道`, while preserving the valid positive Skill match.

GitHub Actions verification:

- Validate for resolver commit `ecb2282094286c413199bd20b080a52900d792c5`: success.
- Sync translation context run `33452210274` for the same commit: success.
- Validate for regression commit `8d82d66fcbf58c40471b098d6dda26bca9933065`, run `33452219446`: success.

The regenerated live `glossary/canonical_findings.json` still contains `cf-1bd479584e40d767` as an open evidence record, but it no longer contains the false `skill.righteous_path` canonical resolution. This is intentional: the creator-name finding remains non-canonically resolved rather than being incorrectly covered by the Skill rule.

No `localized_data/**` files were edited.
