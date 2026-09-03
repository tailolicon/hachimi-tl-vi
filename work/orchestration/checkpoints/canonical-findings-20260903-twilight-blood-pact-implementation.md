# Canonical finding implementation: 黄昏の血盟

- Findings: `cf-0fd7f3b4c864c3ff`, `cf-de21b30194640181`
- zh-CN source: `黄昏的血盟`
- Verified JP unique Skill title: `黄昏の血盟`
- Character identity: Jungle Pocket [ヴァーミリオン・ヘッド] (game character 109402)
- Canonical Vietnamese target: `Huyết Minh Hoàng Hôn`
- Historical target rejected: `Huyết minh hoàng hôn`

## Evidence and reasoning

Current JP gameplay references identify `黄昏の血盟` as Jungle Pocket [ヴァーミリオン・ヘッド]'s unique Skill. The zh-CN bridge `黄昏的血盟` preserves the same two motifs: twilight (`黄昏`) and blood pact/alliance (`血盟`). The existing Vietnamese phrase is semantically close, but it does not follow the repository's game-title capitalization policy. `Huyết Minh Hoàng Hôn` keeps the concise Han-Viet title rhythm and both JP motifs while normalizing title capitalization.

## Implementation

- Hardener: `scripts/harden_twilight_blood_pact_finding.py` at commit `d25aacd54e7a822ed71d06ff12b44caeb2034d55`.
- Permanent regression tests: `tests/test_twilight_blood_pact_finding_hardening.py` at commit `ef11536770326df0751b05a7c0b735540814da93`.
- Community rule ID: `skill.jungle_pocket.twilight_blood_pact`.
- Terminology decision ID: `audit.finding.skill-twilight-blood-pact`.

## Duplicate-finding scope safety

The live context contains one exact finding under category `147` and one broad contains finding for the same source title in `text_data_dict.json`. The canonical rule uses the complete source title as an `exact` alias, is file-scoped, and intentionally has no JSON-path prefix. This covers both finding scopes under `scripts/canonical_findings.py` while preventing longer prose that merely contains the Skill title from resolving. Regression coverage also checks the same phrase in another file remains unmatched.

## Acceptance complete

- Validate run `33808081855` for the regression-test commit: completed successfully.
- Production `Sync translation context` run `33808080546`: completed successfully.
- The first review-plan run was superseded/cancelled by newer pushes; the successful replacement published active plan `tr-p3-67f8551f7780-ddd89987ff0f-b5c0bcb3bd-570540b0f1` at `2026-09-03T21:32:32.626362Z`.
- Live batch `...-b0137` embeds `skill.jungle_pocket.twilight_blood_pact`, preferred `Huyết Minh Hoàng Hôn`, rejects `Huyết minh hoàng hôn`, and has `canonical_findings: []` for the `黄昏的血盟` entries.

Both duplicate findings are therefore unblocked in the live review context and this maintenance unit is complete.
