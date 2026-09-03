# Canonical finding implementation: Faith in the Feral

- Findings: `cf-218ec5e342978091`, `cf-ee7eb4b1cd8aca0a`
- zh-CN source: `狂野信仰`
- Verified JP unique Skill title: `Faith in the Feral`
- Character identity: Jungle Pocket (game ID 1094)
- Canonical target: `Faith in the Feral`
- Historical target rejected: `Tín ngưỡng hoang dã`

## Evidence and reasoning

Current JP gameplay references identify Jungle Pocket's unique Skill as the verbatim English title `Faith in the Feral`. The zh-CN bridge localizes that title as `狂野信仰`; the historical Vietnamese target translates the bridge rather than preserving the in-game Skill identity. The canonical target therefore keeps `Faith in the Feral` verbatim.

## Implementation

- Hardener: `scripts/harden_faith_in_the_feral_finding.py` at commit `ee5af172a2163a47e0e3341a4cc5909486848eb6`.
- Permanent regression tests: `tests/test_faith_in_the_feral_finding_hardening.py` at commit `d2f5219e2013146ee142b2454c549efb8cd27343`.
- Community rule ID: `skill.jungle_pocket.faith_in_the_feral`.
- Terminology decision ID: `audit.finding.skill-faith-in-the-feral`.

## Duplicate-finding scope safety

The live review context contains two findings for the same Skill title: a broad `contains` finding scoped to `text_data_dict.json` with no JSON-path prefix, and an `exact` finding scoped to category `147`. A single community rule uses the complete source title as an `exact` alias, is restricted to `text_data_dict.json`, and intentionally has no JSON-path prefix. Under `scripts/canonical_findings.py` coverage semantics this rule encompasses both live finding scopes, while the exact alias prevents longer source strings that merely contain `狂野信仰` from resolving. Regression coverage also verifies that the same source in another file does not resolve.

## Remaining acceptance

Do not mark this maintenance unit complete yet. Required next evidence is successful Validate, production Sync translation context, refreshed translation-review plan, and live review context showing both findings unblocked with `skill.jungle_pocket.faith_in_the_feral` embedded.
