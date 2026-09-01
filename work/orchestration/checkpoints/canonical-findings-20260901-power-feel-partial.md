# Canonical findings maintenance checkpoint — 力量感 narrative Power guard

- Finding: `cf-03be28442492e3b1` (`力量感`), raised from Taiki Shuttle narrative dialogue.
- Root cause: generic `common.stat.power` alias `力量` could overmatch descriptive prose inside `力量感`, incorrectly forcing the gameplay stat label `Power`.
- Durable hardening on `main`:
  - `02b385c0a22e7b0b4e332595a863cd1867314241` extends `scripts/harden_narrative_stat_context_finding.py` with `力量感` as an exclusion for `common.stat.power`.
  - `9fadebf477d8a68a52cc5747d31b9e905db662c0` adds regression coverage expecting finding `cf-03be28442492e3b1` to resolve via `context_guard` to `common.stat.power` / `Power`.
  - `f74f51e94be3d0eed1399e9d2fef5c86e15ec2a5` registers `cf-03be28442492e3b1` in `scripts/resolve_context_guard_findings.py`; the missing registration was the exact cause of the focused test failure.
- Production verification:
  - Validate run `33473873822` completed successfully.
  - Sync translation context run `33473104280`, attempt 2, completed successfully with `459 passed`; `context_guard_resolutions_changed=true` and generated context was published to `main` as `8bdb0ffbe04c0dbf77eb3602ce98746209f39113` after safe rebase.
  - Live `glossary/canonical_findings.json` now gives `cf-03be28442492e3b1` `canonical_resolution.layer=context_guard`, `term_id=common.stat.power`, `target_vi=Power`.
  - Sync translation review plan run `33473873818` completed successfully.
  - Sync translation context run `33473873834`, retry attempt 2, completed successfully; its checkout included this checkpoint lineage and ended with `Context is already current.`, giving the required no-op/stability proof.
  - A later rerun of `33473104280` also passed all `459` tests; it generated unrelated concurrent canonical drift from other hardeners, not a regression of this finding.
- No `localized_data/**` line was patched. `cf-03be28442492e3b1` is canonically resolved and no longer blocks retrospective review through this context rule.
