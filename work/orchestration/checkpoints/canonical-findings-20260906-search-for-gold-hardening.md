# Canonical finding hardening — Search for Gold

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T202257Z`

Finding: `cf-cb0e0393aa8c140c`

## Live finding

- zh-CN source: `寻访黄金`
- generated finding status: `open`
- source path: `text_data_dict.json`
- generated finding scope has no json-path prefix, so any resolving canonical rule must cover the source path rather than narrow itself to category 147.

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
  - source-path scope `text_data_dict.json`
  - canonical target `Tìm kiếm hoàng kim`
  - historical alternate `Đi tìm hoàng kim` forbidden
  - terminology review decision locks JP `黄金を訪ねて`
  - appends the canonical target to finding suggestions so `refresh_canonical_resolutions` can resolve the blocker.
- `tests/test_search_for_gold_finding_hardening.py`
  - proves hardener idempotence
  - proves the live source-path-scoped finding resolves through community + review layers
  - proves the exact rule does not overmatch another source path or longer prose containing the source phrase.

Implementation commits:

- hardener: `73811049e9243bd41f3ad84fa72f11347b213cad`
- regression test: `d29e2ff0f5656264b5581bf7a3876889c443a96a`

## Completion gate

Do not increment maintenance `completed_count` yet. Completion requires validation plus production context regeneration/Sync so live `glossary/canonical_findings.json` records a non-null canonical resolution for `cf-cb0e0393aa8c140c` and the blocker disappears from newly generated review context.
