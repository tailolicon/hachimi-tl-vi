# Canonical finding complete — Trainee localize compound

Finding: `cf-d4d7f252ccfed57f`

Source/scope: full compound `育成赛马娘`, `contains`, `localize_dict.json`.

Accepted canonical resolution:
- layer: `community`
- term: `career.ui.trainee.localize`
- target: `Trainee`

Permanent hardening:
- `9fa8ecf45d5b8d5765cde520d5acf6038925442a` extended `scripts/harden_trainee_text_data_finding.py` with a localize-only full-compound rule. Bare `育成` and bare `赛马娘` remain outside this lock.
- `0e69ee41ac4c4a7200a2c002203d42a56e35c315` added regression coverage proving the localize finding resolves to `Trainee` while the bare terms remain unresolved.

Acceptance evidence:
- Validate run `34098570963` completed successfully.
- Production Sync run `34098549608` completed successfully from hardener commit `9fa8ecf45d5b8d5765cde520d5acf6038925442a`.
- In that Sync, `harden_trainee_text_data_finding.py` reported `changed=true` on the pre-apply pass and `changed=false` on the second pass, proving hardener idempotence inside one production pipeline execution.
- Canonical refresh reported `findings=528 active=180`.
- Test context pipeline passed `814` tests.
- The generated context commit was rebased safely and pushed to `main` as `183db58333...` (`Sync translation context from pinned source`).
- Live `glossary/ui_community_terms.json` now contains `career.ui.trainee.localize` with source alias `育成赛马娘` and preferred target `Trainee`.
- Live `glossary/canonical_findings.json` resolves `cf-d4d7f252ccfed57f` through that community rule to `Trainee`.
- A later unchanged production Sync run `34098570944` also completed successfully with `814` tests and ended with `Context is already current.`, establishing semantic no-op after persistence.

This finding is accepted complete. Maintenance completed_count advances from 187 to 188. Continue with the next active blocker selected by `scripts/canonical_findings.py::active_findings` semantics.
