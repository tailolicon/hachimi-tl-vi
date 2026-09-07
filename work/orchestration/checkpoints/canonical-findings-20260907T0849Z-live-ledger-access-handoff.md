# Canonical findings maintenance — live-ledger access handoff

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T084600Z`

Live routing was re-read from `main` before work. The project remains in retrospective translation review; the translation-review gate is enabled, concurrent translation is allowed, and the active plan is `tr-p3-67f8551f7780-dccdca6d3e23-b5c0bcb3bd-51e9797e5a` with 3142 unresolved review entries at the latest live gate snapshot.

The released maintenance lane was atomically taken over at main commit `19003c90f17c60b8c35d75292a06cec1c85d9142`. The latest accepted maintenance completion remains `cf-d4d7f252ccfed57f` (`育成赛马娘` -> `Trainee`) at `completed_count=188`; no new finding is marked complete in this unit.

Active finding selection must follow `scripts/canonical_findings.py::active_findings`: only open/deferred rows without `canonical_resolution` and without an explicit ignore action are blockers. The prior handoff for `cf-3a460c751596bfac` remains authoritative: it is intentionally deferred and must not be locked without materially new authoritative Global evidence.

The generated `glossary/canonical_findings.json` is large enough that the connected file-read surface did not return the complete payload in this bounded unit. The REST content surface returned only a truncated prefix, and a secondary raw-content backend hit a transient DNS failure. Per `work/worker_session_policy.json`, this is a capability-local/transient backend failure, not a repository/task blocker and not grounds to guess a canonical target.

Continuation: use any normal connected repository execution/read path that can evaluate or enumerate the full live ledger (prefer invoking the repository's own `scripts/canonical_findings.py::active_findings` semantics), select the first actionable blocker other than `cf-3a460c751596bfac`, and continue canonical verification/hardening. Do not increment `completed_count` until the finding passes the repository's required validation + production Sync/no-op acceptance proof.
