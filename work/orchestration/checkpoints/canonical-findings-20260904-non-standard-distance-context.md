# Canonical finding checkpoint: non-standard distance context

- Finding: `cf-8faece2c0770dea4` (`非根干距离○`)
- Resolution: standard-distance Skill locks now exclude the explicit `非根干距离×/○/◎` compounds; the finding is resolved by the context guard and does not invent a competing non-standard-distance base term.
- Durable changes: `scripts/harden_non_standard_distance_context_finding.py`, `scripts/resolve_context_guard_findings.py`, `glossary/term_registry.json`, `glossary/canonical_findings.json`, and `tests/test_non_standard_distance_context_finding_hardening.py`.
- Validation: hardener idempotence and resolver behavior passed through direct Python invocation; `python -m compileall` passed. The environment has no `pytest` module.
- Continuation: re-read live routing, verify the finding remains resolved after the production context refresh, then release this maintenance lane and resume the highest-priority eligible mass-work unit.

## Follow-up maintenance

- Finding: `cf-d1bcaa0ab582cbdf` (`宝石`)
- Guard extension: the canonical `currency.jewel` matcher now excludes the evidenced character and gemstone compounds `第一红宝石`, `绿宝石`, and `蓝宝石`, while preserving bare currency matches.
- Validation: the Jewel hardener remains idempotent; direct matcher checks cover currency, character-name, emerald, and sapphire contexts.
