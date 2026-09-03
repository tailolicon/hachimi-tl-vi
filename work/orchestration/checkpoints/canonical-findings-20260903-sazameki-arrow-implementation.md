# Canonical finding implementation: 击退,喧鸣之箭 / 翳り退く、さざめきの矢

Claim: `canonical-findings-maintenance-gpt56sol-20260903T183533Z`
Finding: `cf-3a4b945b9d461490`

## Evidence

- Live repository source entries are exact Skill ids `10170201`-`10170203` with zh-CN text `击退,喧鸣之箭`.
- The Uma Musume CN/JP comparison table maps those exact ids to JP `翳り退く、さざめきの矢` and identifies them as the same unique-Skill family.
- Current JP references identify `翳り退く、さざめきの矢` as the unique Skill of autumn/kimono Symboli Rudolf and report the same late-race speed-up effect.
- The title imagery is the recession of cloud/shadow (`翳り退く`) and a sounding/murmuring arrow (`さざめきの矢`).

## Decision

Lock target: `Mây Tan, Tiễn Ngân`.

This keeps a compact Vietnamese game-title cadence while preserving both halves of the JP title imagery. It replaces the literal, awkward current output `Đánh lui, mũi tên vang dội`.

## Durable implementation

- `scripts/harden_sazameki_arrow_finding.py` at commit `45a6a3200c09182a330e735c34fd410bf61f42cc` adds an exact source-path-scoped Skill-name rule, a JP-backed review lock, and accepted-target evidence for the finding.
- `tests/test_sazameki_arrow_finding_hardening.py` at commit `4fc872ad14f27545d0846a253041a0802943ab01` protects idempotence, canonical-resolution clearing of the active finding, and exact-match/source-path non-overmatch.

## Production acceptance

Accepted.

- Validate run `33793107054` completed successfully on final implementation head `4fc872ad14f27545d0846a253041a0802943ab01`.
- Sync translation context run `33793107093` completed successfully on the same implementation head.
- Sync translation review plan run `33793106936` completed successfully; its production pass ran 576 tests successfully and refreshed the live review plan.
- Live active plan is now `tr-p3-67f8551f7780-15b42115d87b-b5c0bcb3bd-6c5fb85f24`.
- In live batch `b0133`, the three exact `击退,喧鸣之箭` entries now carry `skill.sazameki_arrow → Mây Tan, Tiễn Ngân` as community canonical evidence, mark the old literal translation forbidden, and have an empty `canonical_findings` array. Therefore `cf-3a4b945b9d461490` is no longer a worker-facing canonical blocker.

Maintenance completion count may advance from 41 to 42.
