# Canonical finding hardening — Imagination × Creation = Infinity

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T203247Z`

Finding: `cf-46f8fab03950e013`

## Repository evidence

Pinned curation result `work/curation/results/term-0041/cur-20260826T114929Z-ecf7e0b1.json` already contains a reviewed `lock` decision:

- zh-CN: `想象×创造＝∞`
- locator: `47:101371`
- Japanese: `想像×創造＝∞`
- Vietnamese: `Tưởng tượng×Sáng tạo＝∞`
- kind: `skill_name`

The curation note explicitly preserves the exact `×` and fullwidth `＝` equation structure while translating the two ordinary concepts.

## Hardening implemented

- `scripts/harden_imagination_creation_infinity_finding.py`
  - exact zh-CN alias
  - exact source-path coverage for `text_data_dict.json`
  - supported `invalidation_scope: item`
  - target `Tưởng tượng×Sáng tạo＝∞`
  - review decision `audit.finding.skill-imagination-creation-infinity`
  - JP identity `想像×創造＝∞`.
- `tests/test_imagination_creation_infinity_finding_hardening.py`
  - idempotence
  - canonical + review resolution
  - exact source-path and exact-source non-overmatch
  - symbol-preservation assertions.

Implementation commits:

- hardener: `a831149ab38ac3fdc839fdcefd7e520beca5b3b8`
- regression test: `e932100c3022c07ca6226dd124c892bde8bede3e`

## Completion gate

Do not increment the maintenance completed count yet. Validate the implementation and require a successful production context Sync that records a non-null canonical resolution for `cf-46f8fab03950e013` on live `main` and removes it from newly generated review context.
