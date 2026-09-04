# Persistent tasks after initial canonical hardening

This file defines the repository-owned tasks that carry the project from Audit Round 1 through the full pinned corpus, deferred waves, post-completion audits and final release.

Use `WORKER_START.md` for routing and `AUTOPILOT.md` for lifecycle/claim safety. This file exists so no future worker needs chat history to know what "finish the remaining corpus" means.

## translation-review-round1

Mass-worker phase. Use `WORKER_CONTINUOUS.md` + `TRANSLATION_REVIEW.md` and the live active plan.

Completion is repository state, not a worker assertion:

- current translation-review gate clears;
- active plan/merge state agrees;
- unresolved high-priority systemic canonical findings are resolved/deferred/ignored explicitly;
- no ordinary worker bypasses the gate to translate new content.

If review discovers a systemic terminology/context defect, use `glossary/canonical_findings.json`; do not establish a competing local convention in one batch.

After the translation-review gate clears, allow the universal router to select required UI review.

## ui-review-round1

Mass-worker phase. Use `WORKER_CONTINUOUS.md` + `UI_REVIEW.md` while live state shows assignable required UI review.

Completion requires canonical merge/review state, not merely worker completion markers.

After required UI review clears, normal translation becomes eligible.

## translate-pinned-corpus

Mass-worker phase. Use `PARALLEL_TRANSLATION.md` and current pinned epoch metadata.

Never change the pinned source commit inside an ordinary translation session.

Every wave must preserve:

- task-isolated claims/results;
- durable partial checkpoints;
- Translation Memory/reviewed regression reuse;
- canonical/source-bridge guards;
- aggregation as the only path to canonical `localized_data/**` progress.

Current project snapshot at orchestration bootstrap:

- pinned source total: 1,158,825 entries;
- canonically translated: 19,520;
- initially queued: 131,560;
- deferred: 1,027,265.

These numbers are historical bootstrap context only. Always read live `work/translation_progress.json` instead of assuming they remain current.

The project is NOT complete when the current 131,560-entry wave finishes. If deferred pinned entries remain, route to `deferred-wave-expansion`.

## deferred-wave-expansion

Serial maintenance. Acquire `work/orchestration/maintenance_claim.json`.

Trigger only when:

- higher-priority audit/UI gates are clear;
- current queued wave is fully covered/merged;
- live `deferred_entries > 0`.

Goal: promote the next deterministic tranche of the SAME PINNED CORPUS into an ordinary claimable translation epoch/wave without losing prior work.

Required procedure:

1. inspect the live source-batch/epoch-generation tooling and current pinned source identity;
2. determine why the remaining entries are deferred and how the current queue was selected;
3. do not invent a second incompatible queue format;
4. deterministically select a bounded next tranche from deferred UIDs;
5. preserve prior translated UID/fingerprint coverage and Translation Memory;
6. create/update source-batch/epoch metadata needed by `PARALLEL_TRANSLATION.md`;
7. keep the pinned upstream source commit unchanged unless there is a separate explicit source-promotion maintenance task;
8. update progress fields consistently (`queued_entries`, `deferred_entries`, batch totals/epoch metadata);
9. validate source counts/UID uniqueness/fingerprints and run repository tests;
10. publish the new wave so fresh universal workers automatically return to normal translation.

Prefer bounded repeatable waves if putting all remaining ~million entries into one Git commit/plan would be operationally unsafe.

After publishing a wave:

- release/complete the maintenance claim;
- leave orchestration in the mass-translation lifecycle;
- README progress must show the new queued/deferred counts;
- repeat translation -> expansion until live deferred entries reach zero and pinned source coverage reaches source total.

If the existing repository tooling cannot safely promote deferred content, persist the exact blocker and implement the missing deterministic queue-expansion tooling as repository maintenance. Do not silently declare the deferred corpus out of scope.

## post-completion-audit-round2

Once the entire pinned source is translated/covered and `deferred_entries == 0`, perform an explicit full-corpus Audit Round 2.

Serial transition step:

- verify source coverage from live progress;
- deliberately increment `glossary/translation_audit_policy.json.audit_round` by exactly one;
- regenerate the full retrospective review plan under current canonical context;
- validate production Sync;
- update orchestration phase/task state.

Then mass workers complete the generated full review plan through `TRANSLATION_REVIEW.md`.

Systemic findings remain canonical-first and may reopen affected entries.

## post-completion-audit-round3

After Round 2 fully resolves and its systemic fixes settle, deliberately start another full-corpus clean Audit Round 3 using the same controlled audit-round transition.

This round exists to catch inconsistencies introduced/exposed by the full project rather than only the initial 19,520 translated subset.

If Round 3 reveals a material systemic canonical correction that invalidates a substantial part of the pass, start another full pass rather than pretending the stale pass is clean.

## final-release-verification

Serial maintenance after required audits/UI checks are clean.

Verify at minimum:

- `translated_entries == source_total_entries` for the pinned corpus, or equivalent canonical coverage accounting with no unexplained gap;
- `deferred_entries == 0`;
- no required translation-review gate remains active;
- required UI review is complete;
- no unresolved high-priority canonical finding lacks explicit disposition;
- full test suite passes;
- compile/index/release workflow succeeds;
- `release/index.json` is produced from current canonical output;
- README/status progress agrees with repository state.

Then update `work/orchestration/state.json`:

- `phase = "complete"`;
- `blocking_maintenance = false`;
- `terminal = true`;
- mark final roadmap item complete;
- record final main SHA and release verification evidence.

Only then may a universal worker report the pinned-corpus project complete.
