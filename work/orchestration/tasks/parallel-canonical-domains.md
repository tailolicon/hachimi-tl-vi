# Parallel initial canonical-hardening domains

This file is the task scope for canonical domains that may run concurrently during Phase 0.

Claim/integration semantics are defined by `CANONICAL_PARALLEL.md` and `WORKER_START.md`:

- claim the task-specific `work/orchestration/domain_claims/<task-id>.json`, NOT the primary `maintenance_claim.json`;
- work only on the deterministic domain branch recorded in `work/orchestration/state.json`;
- canonical-first systemic fixes; no direct `localized_data/**` example patching;
- positive and negative tests; permanent idempotent enforcement;
- do not publish canonical changes directly to live `main`;
- when substantive domain work is complete, checkpoint the branch and mark only this roadmap item `ready_for_integration` / `ready_for_finalize` using optimistic concurrency;
- release the task-specific domain claim after that checkpoint;
- another canonical domain does not have to wait for this one;
- final live-main integration, production Sync/no-op proof, and cross-domain conflict resolution are owned by the serial primary integration lane.

Songs, lyrics, staff names and creator credits are not blocking domains in this initial phase.

## canonical-character-training-ui

Focus on common training-career/player-facing labels rather than proper-name trivia. Inventory and harden, with exact context guards where needed:

- Trainer and role labels;
- Career / 育成-run terminology;
- objective / target-race labels;
- turn / year / class labels used in career flow;
- aptitude and aptitude grades;
- rating/rank labels where generic;
- Scenario as a system label where verified;
- track/course-related generic labels not already owned by Race hardening;
- status/condition headings without redoing named Conditions already hardened;
- common selection/result labels in training mode;
- generic `Uma Musume` world-reference usage vs franchise-brand protection.

Do not harden character proper names unless a high-frequency systemic identity defect blocks ordinary UI consistency. Do not let generic prose match a player-facing system label merely because the same words occur.

## canonical-resources-gacha-shop

Focus on currencies/resources and repeated acquisition/exchange UI:

- Jewels and paid/free distinctions where present;
- Monies;
- Cleat / Cleats;
- Support Pt only where not already settled by Training/Support;
- stable generic ticket identities;
- exchange/shop points and pity/exchange mechanics;
- owned / required / cost / insufficient-resource labels in resource-specific contexts;
- acquisition/spend/exchange UI;
- shop/exchange headings.

Preserve source-bridge safeguards such as resource-context `金币` -> `Monies` and `蹄铁` -> `Cleat/Cleats`; ordinary money/gold/hoof prose must remain negative. Do not lock one-off event currencies merely to expand the glossary.

## canonical-missions-events

Focus on repeated mission/reward/event-system labels:

- Daily / Weekly / Main missions;
- Mission / objective / progress / clear/completion labels;
- Rewards / claim/receive labels;
- generic event points and event mission labels;
- Login Bonus;
- recurring campaign/system event labels;
- completion conditions and counters where a fixed UI label exists.

Mission objective prose must remain natural text and must not be corrupted by generic label rules. Event titles/proper names are not system rules unless they are genuinely repeated identities.

## canonical-common-ui-system

Focus on high-frequency generic controls/system labels that materially affect player-facing consistency:

- OK / Cancel / Confirm;
- Select / Change;
- Details;
- Reward;
- Owned;
- Required;
- Max;
- Level / Lv;
- Unlock;
- Upgrade;
- filter / sort;
- date/time/status headings;
- generic result/notice/confirmation labels.

Do not force English for aesthetics. Use established game/project terminology and UI fit constraints. Prefer scoped UI-short-form rules over global canonical locks when a compact-control form is the actual requirement. Add prose negatives for every generic token that could overmatch.

## Ready-for-integration acceptance

A parallel domain may enter `ready_for_integration` only when its branch has, to the extent applicable:

1. deterministic inventory/classification for the intended scope;
2. canonical decisions with evidence sufficient for the project policy;
3. permanent hardener/enforcement or structured canonical data changes;
4. positive and negative regression coverage;
5. no intentional TEMP inventory/staging artifacts among the permanent changes;
6. branch-local validation evidence available through the execution paths of the current worker, or an explicit checkpoint identifying the exact remaining integration-only validation.

Do not run production Sync or mark the domain `complete`; those are integration-lane responsibilities.

## canonical-final-conflict-sweep

This task is deliberately excluded from parallel domain work. It becomes eligible only after Race, Training/Support, Character/Training UI, Resources/Gacha/Shop, Missions/Events and Common UI/System are complete on live `main`. Its scope remains the final split-brain/overmatch sweep described in `work/orchestration/tasks/remaining-canonical-domains.md`.
