# Canonical finding implementation: 念い、信ずればこそ

- Finding: `cf-33179a9c092b7da2`
- zh-CN source: `正因念想，确信所在`
- Verified JP unique Skill title: `念い、信ずればこそ`
- Character identity: Believe / ビリーヴ (game ID 1095)
- Canonical Vietnamese target: `Tâm Niệm, Chính Vì Tin`
- Historical target rejected: `Chính bởi tâm niệm, niềm tin hiện hữu`

## Evidence and reasoning

Current JP gameplay references identify `念い、信ずればこそ` as Believe's unique Skill. `念い` carries the thought/feeling/wish motif, while `信ずればこそ` is an emphatic belief clause: precisely because one believes. The zh-CN bridge expands this into `正因念想，确信所在`; the historical Vietnamese target follows that expansion closely and reads as an explanatory sentence. `Tâm Niệm, Chính Vì Tin` restores the JP motif/order and compresses it into the repository's commercial-game title rhythm.

## Implementation

- Hardener: `scripts/harden_believe_omoi_shinzureba_koso_finding.py` at commit `deee00072091323a49e81624f3c367c641eb4ff1`.
- Permanent regression tests: `tests/test_believe_omoi_shinzureba_koso_finding_hardening.py` at commit `017ac21ed466b9fa1a346391820fd096c607affe`.
- Community rule ID: `skill.believe.omoi_shinzureba_koso`.
- Terminology decision ID: `audit.finding.skill-believe-omoi-shinzureba-koso`.

## Scope safety

The live finding is exact, scoped to `text_data_dict.json` and category `147`. The canonical rule mirrors that exact scope rather than broadening it. Regression coverage verifies the same phrase outside category `147`, in another file, or embedded inside a longer source does not resolve.

## Remaining acceptance

Do not mark this maintenance unit complete yet. Required evidence is successful Validate, production Sync translation context, refreshed translation-review plan, and live review context showing `cf-33179a9c092b7da2` absent with the canonical rule/lock embedded.
