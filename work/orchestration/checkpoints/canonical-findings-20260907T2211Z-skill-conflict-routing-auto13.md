# Canonical findings routing checkpoint — Skill canonical conflicts

Worker claim: `canonical-findings-maintenance-gpt56sol-auto13-20260907T221120Z`.

## Live routing

The live project is in `retrospective_translation_review`, `blocking_maintenance=false`, with the shared maintenance lane takeover-eligible at claim time. The worker claimed the shared maintenance lane through optimistic concurrency and preserved the prior rank-medal handoff.

## Rank Medal finding

`cf-55f0e8a1d70264a2` (`等级奖牌`) remains evidence-blocked. The existing hardener intentionally keeps it blocking because repository evidence and repeated JP/Global searches do not establish the underlying identity. Do not guess `Rank Medal`, `Grade Medal`, or conflate it with the distinct Trainer Medal.

## Newly actionable canonical conflicts observed in the live review plan

A live partial review result for current plan `tr-p3-67f8551f7780-4980bf9be38a-b5c0bcb3bd-72a03a0a2a`, batch `b0092`, records three project-wide Skill-title conflicts that should be preferred over another rank-medal recheck:

1. `cf-619bf2cec9f217a5` — `弯道回复○` / JP `コーナー回復○`.
   - `glossary/skill_name_style.json` currently defines the canonical Skill target `Hồi Phục Khúc Cua○`.
   - Embedded reviewed lock `reviewed.skill_name.ab9ceceded12` still requires `Khúc cua hồi phục○`.
   - This is an internal canonical-source conflict; resolve the older reviewed lock/hardening source to the current Skill-title canonical convention rather than patching individual translated rows.

2. `cf-d19e3a2086ff6567` — `领放牵制`.
   - Current reviewed Skill lock uses `Kiềm chế Nige`.
   - Live common running-style terminology forbids `Nige` and requires `Front Runner`/`Front` for `领放`.
   - Reconcile the exact Skill title at canonical source, preserving the pinned JP Skill identity.

3. `cf-7da1d5f099be055d` — `领放焦躁`.
   - Current reviewed Skill title uses `Nôn nóng Nige`.
   - This conflicts with both the live `Front Runner` running-style standard and the reviewed system label `焦躁 → Rushed`.
   - Reconcile the exact Skill title at canonical source; the current review result suggests `Front Runner Rushed` but acceptance still requires the normal canonical hardening + validation + production Sync/no-op chain.

## Continuation

Prefer these deterministic internal canonical-source conflicts before performing another evidence-only recheck of `等级奖牌`. For each finding: inspect the exact current reviewed decision and the newer canonical source, add a permanent hardener/regression, run full validation, production Sync, and a second unchanged no-op Sync before incrementing `completed_count` (currently 201). Do not edit `localized_data/**` to hide the conflicts.
