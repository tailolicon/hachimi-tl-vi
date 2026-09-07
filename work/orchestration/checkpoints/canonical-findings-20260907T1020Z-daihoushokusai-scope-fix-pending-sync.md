# Canonical finding maintenance checkpoint — Daihoushokusai scope coverage

- Finding: `cf-5310cb8fbcc8798f` (`大丰食祭`).
- Live active-findings enumeration found 116 blockers; this was the first current active row.
- Diagnosis: the existing canonical lock `scenario.daihoushokusai.short` was restricted by `key_prefixes: ["SingleModeScenarioCook"]`, but the generated finding itself is scoped only to `localize_dict.json`. `canonical_findings.py::_rule_covers_finding` therefore correctly refused to mark the broader finding resolved.
- Hardening commit: `a77fc6b2a8364a20b2386001fe3ed23c5ff79ceb` removes the narrower key prefix from the stable proper-name rule/decision while preserving `source_paths: ["localize_dict.json"]` and `match_mode: contains`.
- Regression-test commit: `90bd7b4bbd2471c2e9adb82b972e1114749f7388` adds `tests/test_gourmet_festival_scenario_finding_hardening.py`, covering idempotence and canonical-resolution removal from `active_findings` for the actual source-path-scoped finding shape.
- Local pytest was unavailable (`No module named pytest`), so repository GitHub Actions are the required acceptance backend.
- Production Sync translation context run `34110827740` and Sync translation review plan run `34110827765` were queued from the regression-test commit when this checkpoint was written.
- Do not increment `completed_count` yet. Success requires validation/sync completion, regenerated ledger proof that `cf-5310cb8fbcc8798f` has `canonical_resolution`, then the required second unchanged production Sync/no-op proof.
