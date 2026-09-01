# Canonical findings maintenance checkpoint — 力量感 narrative Power guard

- Finding: `cf-03be28442492e3b1` (`力量感`), raised from Taiki Shuttle narrative dialogue.
- Root cause: generic `common.stat.power` alias `力量` can overmatch descriptive prose inside `力量感`, incorrectly forcing the gameplay stat label `Power`.
- Durable hardening committed on `main`:
  - `02b385c0a22e7b0b4e332595a863cd1867314241` extends `scripts/harden_narrative_stat_context_finding.py` with `力量感` as an exclusion for `common.stat.power`.
  - `9fadebf477d8a68a52cc5747d31b9e905db662c0` extends `tests/test_narrative_stat_context_finding_hardening.py` with finding `cf-03be28442492e3b1` and expected `context_guard` resolution to `common.stat.power` / `Power`.
  - `f74f51e94be3d0eed1399e9d2fef5c86e15ec2a5` fixes the missing `cf-03be28442492e3b1` registration in `scripts/resolve_context_guard_findings.py`, which was the exact cause of the earlier test failure.
- Verification so far:
  - Live `glossary/ui_community_terms.json` contains `力量感` under `common.stat.power.exclude_source_contains`.
  - Validate run `33473873822` for `f74f51e...` completed successfully.
  - Sync translation context run `33473873834` reached source extraction but failed transiently with `urllib.error.URLError: <urlopen error [Errno 104] Connection reset by peer>`; failed jobs were retried rather than changing canonical logic.
  - Earlier Sync run `33473104280` had demonstrated the original resolver omission with 458 tests passing and one focused failure; it was also retried after the resolver fix.
- Do not patch the Taiki Shuttle localized line directly. Remaining acceptance work is to obtain a successful production Sync, confirm generated `canonical_findings.json` gives `cf-03be28442492e3b1` a `context_guard` resolution to `common.stat.power` / `Power`, verify review-plan synchronization, then establish unchanged/no-op Sync evidence before releasing maintenance back to retrospective review.
