# Remaining initial canonical-hardening domains

This file supplies persistent scope for the initial high-frequency canonical hardening tasks after Race.

**Claim and integration semantics are governed by `CANONICAL_PARALLEL.md`. Domain work is parallel; live-main integration is serial.** Any older handoff that says one domain must finish before another domain can begin is obsolete.

Shared rules:

- repository maintenance, not normal translation/review/UI work;
- primary/integration owner uses `work/orchestration/maintenance_claim.json`;
- independent domain workers use the task-specific `claim_path` from `work/orchestration/state.json`;
- work on the deterministic domain branch; never create competing branches merely because main advanced;
- canonical-first systemic fixes;
- no direct `localized_data/**` example patching;
- narrow/item-scoped rules where correctness permits;
- positive + negative tests;
- permanent idempotent enforcement;
- temporary staging/inventory artifacts must not land on main;
- parallel domain workers stop at `ready_for_integration`; only the serial integration lane publishes to main and performs production Sync/no-op proof;
- `blocking_maintenance` blocks mass audit/translation/UI work, not another independent canonical domain.

Songs, lyrics, staff names and creator credits are not blocking domains in this initial phase.

## canonical-training-support

Focus on high-frequency Training / Support / progression vocabulary:

- Training;
- Friendship Training;
- Support Card;
- Support Pt / Support Points where display forms differ;
- Bond / Friendship Gauge and related gauge/bonus wording;
- Energy;
- training success/failure and failure-rate UI;
- training/facility level where applicable;
- stat gain / bonus / cap / limit terminology;
- generic Support Effect labels and repeated training-result/status labels.

Historical Vietnamese calques such as `Huấn luyện`, `Huấn luyện Hữu nghị`, `Điểm Hỗ trợ`, `Gắn kết`, etc. are evidence, not authority. Compare canonical layers and verified game terminology. Ordinary prose about training/friendship/energy must remain negative unless it is truly system UI.

When substantive branch work is complete, checkpoint it as ready for serial integration. Do not require Character/UI or later domains to wait.

## canonical-character-training-ui

Focus on common training-career/player-facing labels rather than proper-name trivia:

- Trainer and role labels;
- Career / 育成-run terminology;
- objective / target-race labels;
- turn / year / class labels in career flow;
- aptitude and aptitude grades;
- generic rating/rank labels;
- Scenario as a verified system label;
- track/course generic labels not already owned by Race hardening;
- status/condition headings without redoing named Conditions;
- common selection/result labels in training mode;
- generic Uma Musume world-reference usage vs franchise-brand protection.

Do not harden character proper names unless a high-frequency systemic identity defect blocks UI consistency. Generic prose must not match UI concepts merely because the same word appears.

## canonical-resources-gacha-shop

Focus on currencies/resources and repeated acquisition/exchange UI:

- Jewels and paid/free distinctions;
- Monies;
- Cleat / Cleats;
- Support Pt only where Training/Support has not settled the context;
- stable generic ticket identities;
- exchange/shop points and pity/exchange mechanics;
- owned / required / cost / insufficient-resource labels in resource contexts;
- acquisition/spend/exchange UI;
- shop/exchange headings.

Preserve scoped source-bridge safeguards such as resource-context `金币` -> `Monies` and `蹄铁` -> `Cleat/Cleats`; ordinary money/gold/hoof prose must remain negative. Do not lock one-off event currencies merely to grow the glossary.

## canonical-missions-events

Focus on repeated mission/reward/event-system labels:

- Daily / Weekly / Main missions;
- Mission / objective / progress / clear/completion labels;
- Rewards / claim/receive labels;
- generic event points / event mission labels;
- Login Bonus;
- recurring campaign/system event labels;
- completion conditions/counters where a fixed player-facing label exists.

Mission objective prose stays natural text. Event titles/proper names are not system canonical rules unless they are genuinely repeated identities.

## canonical-common-ui-system

Focus on high-frequency generic controls/system labels:

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

Do not force English for aesthetics. Prefer established game/project terminology and UI fit constraints. UI-short-form rules may be more appropriate than global locks. Add prose negatives for generic tokens with overmatch risk.

## Parallel-domain ready-for-integration criteria

A parallel domain may set its roadmap item to `status = ready_for_integration` and `stage = ready_for_finalize` only after it has checkpointed the substantive canonical decisions, permanent hardener/data changes, regression coverage, branch SHA, and any remaining integration-only acceptance work. It then releases its task-specific domain claim.

It must **not** mark itself complete, publish canonical changes directly to main, or run production Sync as if it owned the primary integration lane.

## canonical-final-conflict-sweep

This task is deliberately not parallel-eligible. It starts only after Race, Training/Support, Character/Training UI, Resources/Gacha/Shop, Missions/Events and Common UI/System are complete on live main.

It is the freeze check before scaling Audit Round 1. Detect split-brain state across canonical registries, source-bridge/UI rules, permanent hardeners, matching logic, and the current merged corpus as evidence. Look for:

- lower-priority bad locked values hidden by overrides;
- one concept with competing targets;
- unsafe global substring aliases that should be exact/scoped;
- prose accidentally matching named gameplay concepts;
- literal zh-CN carryover for high-frequency mechanics;
- conflicts with prior Conditions/Mood, Skill/Inheritance, Race, Training/Support and other completed domains;
- missing negative tests;
- temporary hardening/staging artifacts in production paths.

Completion requires full validation, idempotent canonical enforcement, production review-plan Sync, representative positive/negative checks, second unchanged Sync true no-op, and no known high-frequency systemic conflict left without explicit defer rationale.

Only then may the integration owner set `blocking_maintenance = false`, transition to `retrospective_translation_review`, and allow mass Audit Round 1 workers.
