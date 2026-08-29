# Active maintenance task: canonical-race

## Mode

Dedicated CANONICAL HARDENING maintenance.

This is NOT a translation worker, translation-review worker, UI-review worker, Song worker, or staff/creator-name worker.

Do not claim translation/review/UI batches while this task remains the blocking active maintenance task.
Do not edit `localized_data/**` to patch examples.
Do not restart inventory from scratch.

## Live handoff snapshot

These SHAs are historical handoff evidence only. A fresh worker must fetch live refs before writing.

- last observed `main`: `9e17356ed0702c2574646f9d563b51ec99318e55` before orchestration bootstrap commits;
- Race branch: `canonical-race-hardening-20260828`;
- last observed Race branch head: `7cea5662ad155fdfe598622155dcfdf2e2c7c5e9`;
- at that snapshot the Race branch was ahead of main and not behind it.

Preserve all valid work already on that branch. Do not create another Race branch.

## Work already established

### Pre-flight gate-reason maintenance

The Race branch already introduced a stable `INCOMPLETE_GATE_REASON` and no-op gate-state normalization work in `scripts/build_translation_review_plan.py`, with regression coverage for fresh-plan -> unchanged rebuild behavior.

However, the file currently contains duplicated imports of `canonical_finding_matches` and `load_canonical_findings`. Clean the import block before integration while preserving package/script execution and the no-op semantics.

### Correct Race taxonomy

Confirmed:

- category `16` is Song, NOT racecourse;
- category `32` is `race_name`;
- category `33` is `race_display_name`.

Never add Race matching to category 16. Do not broaden this task into Song hardening.

### Inventory/evidence already found

Branch-side deterministic inventory found roughly 979 unique race-related source strings in the then-current active 19,520-entry corpus context. Existing Race canonical rules were heavily global; many unlocked strings were not proper race names because category 147 contains objective/requirement prose.

Do not interpret "unlocked" as "proper-name candidate" without identity/context classification.

Common player-facing system forms observed include:

- `新马级`;
- `GⅠ`, `GⅡ`, `GⅢ`;
- `OP`, `Pre-OP`;
- Turf/Dirt;
- Sprint/Mile/Medium/Long;
- running-style vocabulary.

Legacy/current Vietnamese output contains mixed forms such as `Cấp Junior`, `Hạng Junior`, and Unicode `GⅠ` where established player-facing terminology should be verified against `Junior Class`, `G1`, etc.

### Known named-race conflicts

Known conflicts requiring canonical/context repair include:

- `日本德比`: current output/canonical history contains both `Japan Derby` and `Japanese Derby`. JRA identity evidence supports Japanese Derby / Tokyo Yushun identity; do not keep a competing legacy `Japan Derby` canonical form without stronger game-specific evidence.
- Tenno Sho: distinguish Spring vs Autumn correctly.
- `Kikka Sho` vs `Kikuka Sho`.
- `Radio NIKKEI Sho` capitalization.
- game-facing names that intentionally differ from literal real-world naming, including Uma Musume/Junior/Nisai variants. Do not replace game-native identity mechanically with real-racing terminology.

### Critical zh-CN identity collapse

`京城锦标` is proven unsafe as a global source-string identity.

Evidence from the pinned corpus/curation shows different contexts can represent different JP race identities, including:

- Miyako Stakes;
- Keio Hai Nisai Stakes.

Therefore any global `京城锦标 -> Miyako Stakes`-style lock must be removed/narrowed. Use item/category/key/json-path identity so identical zh-CN source strings may resolve to different Race canonicals when the JP identity differs.

Search the existing inventory for more collisions of this type.

### Evidence already collected

Prior investigation used established/official sources consistent with forms such as:

- Junior Class / Classic Class / Senior Class;
- G1 / G2 / G3;
- Turf / Dirt / distance terminology;
- JRA racecourse forms Tokyo, Nakayama, Kyoto, Hanshin, Chukyo, Hakodate, Fukushima, Kokura, Niigata;
- JRA forms including NIKKEI SHINSHUN HAI, NIKKEI SHO, RADIO NIKKEI SHO, Spring Stakes;
- NAR English records confirming names such as Japan Dirt Derby, Cluster Cup, Sparking Lady Cup.

A fresh worker should reuse repository evidence/branch inventory first and only browse/research exact unresolved identities, not redo the whole evidence survey.

## Required finish work

### 1. Clean pre-flight maintenance

Normalize imports in `scripts/build_translation_review_plan.py` so `canonical_finding_matches` and `load_canonical_findings` each appear once in the package import path and once in the script fallback path as appropriate.

Preserve:

- `INCOMPLETE_GATE_REASON`;
- unchanged-gate timestamp normalization;
- plan ID/scope/audit-round stability;
- fresh-plan -> unchanged-rebuild true no-op behavior.

Add/fix regression coverage if needed.

### 2. Complete identity classification

Continue from the existing deterministic inventory.

Classify relevant strings into at least:

- exact named race identity;
- race display-name variant;
- class/grade label;
- racecourse label;
- race objective/requirement prose;
- ordinary prose / not canonicalizable;
- ambiguous source-bridge identity.

Only exact gameplay identities should become proper-name canonical rules.

### 3. Harden common Race system labels

Verify and lock, only where evidence/context supports them:

- Junior Class;
- Classic Class;
- Senior Class;
- G1;
- G2;
- G3;
- OP;
- Pre-OP;
- Turf;
- Dirt;
- Sprint;
- Mile;
- Medium;
- Long.

Do not globally rewrite ordinary prose containing junior/class/open/etc.

### 4. Harden named races

Resolve the known conflicts and the high-frequency/clearly identified names in the pinned corpus.

For each locked identity:

1. resolve JP identity when possible;
2. prefer official Global game terminology where verified;
3. otherwise use official JP/JRA/NAR/organizer English identity;
4. use strong established international community terminology only when official English is unavailable;
5. never semantic-calque the zh-CN bridge merely because its characters are transparent.

Do not create duplicate competing canonical aliases for one identity.

### 5. Racecourses

Find the actual source categories/keys carrying racecourse labels; do not infer category 16.

Verify common racecourse labels such as:

- Tokyo;
- Nakayama;
- Kyoto;
- Hanshin;
- Chukyo;
- Sapporo;
- Hakodate;
- Niigata;
- Fukushima;
- Kokura.

Only lock verified player-facing labels.

### 6. Item-scoped proper-race registry

Proper race names are expandable identities and should not globally invalidate unrelated corpus entries when a single name changes.

Where correctness permits, move narrow Race proper-name rules to item-scoped/context-scoped matching.

Tests must prove:

- correcting one race changes matching item context;
- unrelated entries keep stable item context/review identity;
- identical zh-CN source can resolve to two distinct Race identities by context;
- removal/change of a rule cannot leave stale accepted review decisions;
- category 16 Song entries do not receive Race context;
- category 147 ordinary objective prose is not misclassified as a proper name.

Keep genuinely global system terminology global when that is correct.

### 7. Permanent hardener/enforcement

Create or finish a permanent Race hardener/enforcer using stable IDs and structured context guards.

It must:

- preserve correct existing mappings;
- remove/narrow known unsafe global Race mappings;
- reject legacy conflicting targets where appropriate;
- remain idempotent;
- survive normal production context regeneration;
- never act as blind text replacement.

### 8. Regression suite

Permanent regression coverage must include at minimum:

- Junior / Classic / Senior Class;
- G1/G2/G3;
- OP/Pre-OP where applicable;
- Turf/Dirt;
- distance labels;
- Japanese Derby;
- Tenno Sho Spring/Autumn distinction;
- Kikuka Sho identity;
- Radio NIKKEI Sho capitalization;
- identical zh-CN source -> two Race identities;
- at least one racecourse label;
- category 16 Song negative;
- category 147 prose/objective negative;
- proper-name substring isolation;
- item-scoped invalidation;
- previous Conditions/Mood hardening;
- previous Skill/Inheritance hardening;
- canonical-finding pipeline;
- review-plan no-op behavior.

### 9. Remove temporary branch artifacts

Before integration, remove every Race-only temporary inventory/debug/staging artifact that should not persist in production, including temporary workflows/scripts/generated inventories.

Permanent tests and permanent hardener stay.

No `TEMP` Race workflow/script should land on `main`.

### 10. Final branch validation

Run/verify:

- full `pytest -q`;
- translation review plan rebuild;
- `git diff --check`;
- hardener twice for idempotence;
- fresh-plan / unchanged-plan no-op regression;
- representative positive and negative corpus checks.

Do not stop at "tests passed" if canonical Race data has not actually been generated and validated.

### 11. Integrate safely

Before integration:

1. fetch live `main` again;
2. compare the Race branch against it;
3. preserve unrelated concurrent main changes;
4. integrate only clean permanent Race changes;
5. do not import temporary inventory artifacts.

Fast-forward if still valid; otherwise rebase/cherry-pick/construct a clean integration without overwriting concurrent work.

### 12. Production Sync and no-op proof

After Race changes land on main:

1. run/wait for normal production Sync;
2. read new `work/translation_review/active_plan.json`;
3. read `work/parallel_state.json`;
4. confirm both point to the same plan;
5. inspect representative regenerated Race contexts;
6. run a SECOND unchanged production Sync;
7. prove the second Sync is a true no-op / does not create semantic churn.

Representative final checks must include:

- Japanese Derby;
- both ambiguous `京城锦标` identities;
- Junior Class;
- G1;
- at least one racecourse;
- ordinary category-147 objective prose;
- category-16 Song entry.

Expected:

- Race identities receive exact/intended scoped context;
- prose negatives do not receive false proper-name context;
- Song entries receive no Race canonical rule.

## Completion and orchestration transition

Do not claim this task complete until all completion criteria above are verified from live repository state.

Then, while still owning the maintenance claim:

1. update `work/orchestration/state.json` using current blob SHA;
2. mark roadmap item `canonical-race` complete with final main SHA/summary;
3. activate `canonical-training-support` as the next task;
4. create a concise persistent task file for that domain if none exists, using the generic canonical-hardening rules in `AUTOPILOT.md` and the scope below;
5. set/create its maintenance branch deterministically;
6. mark/release/reset the maintenance claim for the next task;
7. ensure README progress sync reflects the new active task.

Next domain scope is high-frequency Training / Support / progression terminology, including Training, Friendship Training, Support Card, Support Pt, Bond/Friendship Gauge, Energy, training success/failure and stat/progression labels. Do not start it before Race completion.

## End report

Persist first, report second. A concise chat report may include:

- final main SHA;
- Race hardener commit(s);
- mappings/classes/racecourses hardened;
- global mappings narrowed/removed;
- ambiguous identities resolved/deferred;
- tests status;
- final active review plan ID/unresolved count;
- first production Sync result;
- second Sync no-op confirmation;
- proof temporary Race tooling is absent;
- orchestration transition to the next task.

The next worker must be able to continue using only `WORKER_START.md` and repository state.

## Finalizer checkpoint — 2026-08-29T09:25Z

- Maintainer claim: `canonical-race-finalizer-20260829T0916Z-gpt56sol`.
- Race branch validation at `7d68edfda2383764ff5cd1a45a1387a461e1d6b8` reached full `pytest -q` and failed with exactly two test failures; Ruff and prior staging gates were already clean.
- Existing Actions log decoding did not expose the traceback text through the connector, so no speculative permanent code change was made.
- Added TEMP-only diagnostic instrumentation to `.github/workflows/validate-race-hardening.yml` on Race branch commit `9be6a421989f5cfb5ffca105a77124f13ea071ea`: pytest now runs with `--tb=short`, tees to `race-pytest.log`, and uploads `race-pytest-diagnostics` with `if: always()`.
- This workflow is branch-only diagnostic tooling and MUST NOT be integrated to `main`.
- Next bounded action: inspect the push-triggered validator run for `9be6a421989f5cfb5ffca105a77124f13ea071ea`, download `race-pytest-diagnostics`, identify the exact two failures, then apply only the concrete permanent fix(es) before rerunning validation.
