# Canonical findings maintenance checkpoint — 力量感 narrative Power guard

- Finding: `cf-03be28442492e3b1` (`力量感`), raised from Taiki Shuttle narrative dialogue.
- Root cause: generic `common.stat.power` alias `力量` can overmatch descriptive prose inside `力量感`, incorrectly forcing the gameplay stat label `Power`.
- Durable hardening committed on `main`:
  - `02b385c0a22e7b0b4e332595a863cd1867314241` extends `scripts/harden_narrative_stat_context_finding.py` with `力量感` as an exclusion for `common.stat.power`.
  - `9fadebf477d8a68a52cc5747d31b9e905db662c0` extends `tests/test_narrative_stat_context_finding_hardening.py` with finding `cf-03be28442492e3b1` and expected `context_guard` resolution to `common.stat.power` / `Power`.
- Repository-native Sync translation context run `33473104280` was triggered for `9fadebf...` and was still pending at checkpoint time. Sync translation review plan was also triggered.
- Do not patch the Taiki Shuttle localized line directly. The next maintainer should verify workflow completion, confirm `glossary/ui_community_terms.json` contains `力量感` under `common.stat.power.exclude_source_contains`, confirm the generated finding gains `canonical_resolution.layer=context_guard`, run/verify required validation, then production Sync/no-op proof and release maintenance back to retrospective review.
