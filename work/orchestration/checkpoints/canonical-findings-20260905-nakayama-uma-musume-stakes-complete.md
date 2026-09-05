# Canonical finding completion — 中山赛马娘锦标

Finding: `cf-2672ecdef6c16856`

## Accepted identity

- zh-CN source: `中山赛马娘锦标`
- pinned JP game identity: `中山ウマ娘S`
- accepted project target: `Nakayama Uma Musume Stakes`

The prior `Nakayama Himba Stakes` identity was stale real-racing carryover. Pinned curation evidence identifies the in-game race as `中山ウマ娘S`, and the project already canonizes the reusable `ウマ娘ステークス` component as `Uma Musume Stakes`.

## Permanent hardening

- `scripts/harden_nakayama_uma_musume_stakes_finding.py`
- `tests/test_nakayama_uma_musume_stakes_finding_hardening.py`
- exact community rule `race.nakayama_uma_musume_stakes`
- terminology review lock `audit.finding.nakayama-uma-musume-stakes`
- legacy registry id `race.nakayama_himba_stakes` retained only for compatibility, with its JP identity/target corrected

## Acceptance evidence

For head `5318cc31a3f9f41fa6d1a53987c15024520d29d6`:

- Validate run `33938793628`: success
- Sync translation context run `33938793629`: success
- Sync translation review plan run `33938793635`: success

Live regenerated read-back on `main` confirms:

- `term_registry.json` has `中山ウマ娘S` → `Nakayama Uma Musume Stakes` for the legacy compatibility record.
- `ui_community_terms.json` contains exact `race.nakayama_uma_musume_stakes` → `Nakayama Uma Musume Stakes`.
- `terminology_reviews.json` has exactly one current decision for `中山赛马娘锦标`, action `lock`, target `Nakayama Uma Musume Stakes`.
- `canonical_findings.json` now carries both canonical and review resolutions for `cf-2672ecdef6c16856`.
- Current active review plan `tr-p3-67f8551f7780-ac19b5d9dc03-b5c0bcb3bd-8d48ae7a7e`, batch `b0072`, still flags the stale translated text for correction but embeds `canonical_findings: []` for this item, proving the canonical blocker itself is cleared.

No `localized_data/**` example was hand-edited as canonical evidence.