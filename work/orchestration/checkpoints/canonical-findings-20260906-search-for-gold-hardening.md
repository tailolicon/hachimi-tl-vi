# Canonical finding hardening — Search for Gold

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T202257Z`

Finding: `cf-cb0e0393aa8c140c`

## Repository evidence

Pinned curation result `work/curation/results/term-0033/claim-3f6c8a10.json` records a reviewed `lock` decision for this exact Skill identity:

- locator: `101351`
- Japanese: `黄金を訪ねて`
- Vietnamese target: `Tìm kiếm hoàng kim`
- kind: `skill_name`

Older curation attempts deferred the title before the Japanese identity was verified; the later reviewed lock carries the verified locator and JP title and is the stronger repository evidence.

## Hardening implemented

- `scripts/harden_search_for_gold_finding.py`
  - exact source alias `寻访黄金`
  - source-path coverage `text_data_dict.json`
  - canonical target `Tìm kiếm hoàng kim`
  - historical alternate `Đi tìm hoàng kim` forbidden
  - supported `invalidation_scope: item`
  - terminology review decision locks JP `黄金を訪ねて`
- `tests/test_search_for_gold_finding_hardening.py`
  - proves hardener idempotence
  - pins the supported `item` invalidation scope
  - proves the live source-path-scoped finding resolves
  - proves the exact rule does not overmatch another source path or longer prose.

Implementation commits:

- initial hardener: `73811049e9243bd41f3ad84fa72f11347b213cad`
- initial regression test: `d29e2ff0f5656264b5581bf7a3876889c443a96a`
- integration fix: `7dab4bcfdbda8cdad15f393dcd5457f9dfaba4ce`
- regression assertion: `b00d6d56cc87cd096859223c0f6986a21d81e51f`

## Validation / integration

- Initial Validate run `34057890523` succeeded.
- First production Sync run `34057890507` exposed unsupported `invalidation_scope: source_path`; the fix switched to supported `item` while retaining independent `source_paths` coverage.
- Fresh production Sync run `34058111237` completed successfully through terminology apply, all finding hardeners, context tests, and generated-context commit.
- Generated context commit: `884c03455bb6b1a76eb0ce3ec6cb097d8fafe5c7`.
- Live `glossary/canonical_findings.json` now records for `cf-cb0e0393aa8c140c`:
  - `suggested_targets_vi: ["Tìm kiếm hoàng kim"]`
  - `canonical_resolution.layer: locked`
  - `canonical_resolution.target_vi: "Tìm kiếm hoàng kim"`
  - review decision `audit.finding.skill-ougane-wo-tazunete-search-for-gold`, action `lock`.
- The generated context summary reduced `open_canonical_findings` from 157 to 156.
- Current active review-plan search contains no reference to `cf-cb0e0393aa8c140c`.

## Status

Complete. This maintenance unit may increment the shared maintenance completed count from 151 to 152. Re-route from live `WORKER_START.md`; do not treat the repository as terminal because other canonical findings and retrospective review work remain.
