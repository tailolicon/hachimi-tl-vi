# Canonical findings maintenance checkpoint — Character0146 Scout

Finding: `cf-3caafd7a2224e00e` (`奖池`, exact `localize_dict.json` / `Character0146`).

## Evidence and decision

Existing durable research at `work/orchestration/checkpoints/canonical-findings-20260903-scout-label-research.md` verifies the stable cross-locale key identity as **Scout**, not a generic prize pool. Canonical Vietnamese target is **`Chiêu mộ`**. Generic `奖池` remains context-dependent elsewhere, so the correction must stay exact-key scoped.

## Durable implementation added

- `scripts/harden_character0146_scout_finding.py`
  - adds `common.scout.character0146` to `ui_community_terms.json`;
  - exact source path `localize_dict.json` + `key_exact: [Character0146]` + exact match;
  - preferred/accepted `Chiêu mộ`;
  - forbids legacy `Kho quà`;
  - adds terminology review decision `audit.finding.character0146-scout`.
- `tests/test_character0146_scout_finding_hardening.py`
  - proves hardener idempotence;
  - proves finding resolves to the scoped community term;
  - proves another key and another source path do not inherit the rule.

Local isolated verification from fresh `origin/main` using `uv run --with pytest pytest -q tests/test_character0146_scout_finding_hardening.py` passed: **2 passed**.

## Continuation

Run the hardener against fresh live `main`, persist its generated glossary changes, run required repository validation / context Sync and unchanged no-op Sync, verify `cf-3caafd7a2224e00e` has a canonical resolution and is no longer active, then record accepted completion before moving to the next live active finding. Do not broaden `奖池` globally.
