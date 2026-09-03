# Canonical finding implementation: きせき・おもい・かなで

- Finding: `cf-13a5fddb56f09a28`
- zh-CN source: `心意·奏响·奇迹`
- Verified JP unique Skill title: `きせき・おもい・かなで`
- Character identity: K.S. Miracle (game ID 1093)
- Canonical Vietnamese target: `Kỳ Tích・Tâm Ý・Tấu Vang`
- Historical target rejected: `Tâm ý·Tấu vang·Kỳ tích`

## Evidence and reasoning

Current JP gameplay references identify `きせき・おもい・かなで` as K.S. Miracle's unique Skill. The JP title orders the motifs as miracle → feeling/thought → musical playing, while the zh-CN bridge `心意·奏响·奇迹` reorders them. The old Vietnamese text follows the bridge order. The canonical target restores the JP identity/order while retaining a compact Vietnamese game-title rhythm and the JP middle-dot styling.

Repository `glossary/skill_name_style.json` requires compact Vietnamese Skill titles while using JP wording to protect meaning, motif, and identity.

## Implementation

- Hardener: `scripts/harden_kiseki_omoi_kanade_finding.py` at commit `13cd6122b8a3f71f1a680d80bd0700cf2c8bfe1a`.
- Permanent regression tests: `tests/test_kiseki_omoi_kanade_finding_hardening.py` at commit `6d6a317171f0bcdd6eb5eb74f39fda4ba06aca21`.
- Community rule ID: `skill.ks_miracle.kiseki_omoi_kanade`.
- Terminology decision ID: `audit.finding.skill-kiseki-omoi-kanade`.

## Scope safety

The live finding is `match_mode: contains` with `source_paths: ["text_data_dict.json"]` and no JSON-path prefix. Following the repository's accepted no-prefix finding precedent, the canonical rule uses the complete Skill title as an `exact` alias restricted to `text_data_dict.json`, without adding a category prefix that would fail to cover the live finding's recorded scope. Regression coverage verifies that a longer source containing the phrase and the same phrase in another file do not resolve.

## Remaining acceptance

Do not increment maintenance completion yet. Required next evidence is successful Validate, production Sync translation context, refreshed translation-review plan, and live review context showing the finding unblocked with the canonical rule embedded.
