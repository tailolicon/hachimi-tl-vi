# Remaining initial canonical-hardening domains

This file supplies persistent scope for the initial high-frequency canonical hardening tasks after `canonical-race`.

All tasks use the generic completion/safety rules in `AUTOPILOT.md`:

- dedicated repository maintenance, not normal translation/review/UI work;
- claim the serial maintenance lease first;
- `main` + live task branch are source of truth, never chat memory;
- canonical-first systemic fixes;
- no direct `localized_data/**` example patching;
- narrow/item-scoped rules where correctness permits;
- positive + negative tests;
- permanent idempotent enforcement;
- remove temporary staging/inventory artifacts;
- full validation + production Sync + representative regenerated-context checks + second unchanged no-op Sync;
- update `work/orchestration/state.json` only after live completion criteria are verified.

Songs, lyrics, staff names and creator credits are not blocking domains in this initial sequence.

## canonical-training-support

Focus on the high-frequency training/support/progression vocabulary players repeatedly see.

Inventory and harden, where supported by actual JP/game identity:

- Training;
- Friendship Training;
- Support Card;
- Support Pt / Support Points if the game distinguishes display forms;
- Bond / Friendship Gauge and related gauge/bonus wording;
- Energy;
- training success/failure and failure-rate UI;
- training level / facility level where applicable;
- stat gain / bonus / cap / limit terminology;
- support effects that are generic system labels rather than individual effect names;
- repeated training-result/status labels.

Known risk: the historical registry used Vietnamese calques such as `Huấn luyện`, `Huấn luyện Hữu nghị`, `Điểm Hỗ trợ`, `Gắn kết`, etc. Do not assume they are correct just because they are locked somewhere; compare all canonical layers and actual player-facing terminology.

Do not turn ordinary story prose about training, friendship, energy, bonding or support into system labels. Use category/key/json-path guards and negative tests.

When complete, transition to `canonical-character-training-ui`.

## canonical-character-training-ui

Focus on common育成/career/player-facing labels rather than proper-name trivia.

Inventory and harden concepts such as:

- Mã Nương vs franchise brand protection;
- Trainer and role labels;
- Career /育成 run terminology;
- objective / target race labels;
- turn / year / class labels used in career flow;
- aptitude and aptitude grades;
- rating/rank labels where generic;
- Scenario as a system label where verified;
- Track / course-related generic labels not already owned by Race hardening;
- status/condition headings without redoing named Conditions already hardened;
- common selection/result labels in training mode.

Preserve the established rule that generic `Uma Musume` world-reference usage may map to `Mã Nương` while the franchise brand remains `Umamusume: Pretty Derby`.

Do not harden character proper names as part of this domain unless a high-frequency systemic identity defect blocks ordinary UI consistency.

When complete, transition to `canonical-resources-gacha-shop`.

## canonical-resources-gacha-shop

Focus on currencies/resources and repeated acquisition/exchange UI.

Inventory and harden, with exact mechanic identity:

- Jewels and paid/free distinctions where present;
- Monies;
- Cleat / Cleats;
- Support Pt if not fully settled by Training/Support;
- tickets and named generic ticket types only when their identity is stable;
- exchange/shop points and pity/exchange mechanics;
- owned / required / cost / insufficient-resource labels in resource-specific contexts;
- acquisition/spend/exchange generic UI terms;
- shop/exchange headings if project-wide player-facing terminology is inconsistent.

Preserve source-bridge safeguards such as `金币` resource context -> `Monies` and `蹄铁` resource context -> `Cleat/Cleats`; do not match ordinary gold/money/hoof prose.

Do not lock one-off event currency names without strong evidence merely to expand the glossary.

When complete, transition to `canonical-missions-events`.

## canonical-missions-events

Focus on repeated mission/reward/event-system labels.

Inventory and harden concepts such as:

- Daily / Weekly / Main missions;
- Mission / objective / progress / clear/completion labels;
- Rewards / claim/receive labels;
- event points and generic event mission labels;
- Login Bonus;
- campaign/system event labels that recur broadly;
- completion conditions and counters where a fixed player-facing label exists;
- trigger labels such as morning login only when they are actual system labels, not prose.

Do not translate event titles/proper names into a canonical system rule unless they are genuinely repeated game identities.

Category/context separation is mandatory: mission objective prose remains natural Vietnamese and must not be corrupted by generic label rules.

When complete, transition to `canonical-common-ui-system`.

## canonical-common-ui-system

Focus on high-frequency generic controls/system labels that materially affect UI consistency.

Audit recurring labels such as:

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

Do not force English merely for aesthetic consistency. Use established project/game UI terminology and fit constraints. UI-short-form rules may be more appropriate than global term-registry locks for compact controls.

Do not collide with proper names or ordinary sentence text that contains the same words.

When complete, transition to `canonical-final-conflict-sweep`.

## canonical-final-conflict-sweep

This is not a new broad research domain. It is the freeze check before scaling Audit Round 1.

Systematically detect split-brain canonical state across:

- `glossary/term_registry.json`;
- `glossary/ui_community_terms.json`;
- `glossary/source_bridge_terms.json`;
- `glossary/ui_short_forms.json`;
- `glossary/skill_name_style.json`;
- permanent hardener scripts;
- translation guard/review matching logic;
- current merged 19,520-entry corpus as evidence only.

Look specifically for:

- lower-priority bad locked values being hidden by higher-priority overrides;
- one concept with multiple competing targets;
- global substring aliases that should be exact/scoped;
- generic prose accidentally matching named gameplay concepts;
- literal zh-CN carryover for high-frequency player-facing mechanics;
- canonical rules that conflict with earlier Conditions/Mood, Skill/Inheritance or Race hardening;
- rules with missing negative tests;
- temporary hardening/staging artifacts left in production workflows.

Do not delay mass audit for songs, lyrics, staff/creator credits or rare one-off proper-name uncertainty. Those can be handled by ordinary review/canonical findings when encountered.

Completion criteria are strict:

1. full tests pass;
2. canonical enforcement is idempotent;
3. production review-plan Sync succeeds;
4. representative positive/negative contexts are correct;
5. second unchanged Sync is a true no-op;
6. no known high-frequency systemic conflict remains intentionally unfixed without explicit defer rationale.

Then update orchestration:

- mark all initial canonical-hardening tasks complete;
- set `blocking_maintenance = false`;
- set `phase = "retrospective_translation_review"`;
- clear/reset the maintenance claim;
- let future `WORKER_START.md` sessions route to `WORKER_25MIN.md` and the live Audit Round 1 gate.
