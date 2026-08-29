# Canonical Missions / Events W4 checkpoint — 2026-08-29T16:12Z

## Ownership and branch

- Domain: `canonical-missions-events`
- Claim: `canonical-missions-events-w4b-20260829T1553Z`
- Worker: `worker-w4`
- Branch: `canonical-missions-events-hardening`
- Clean branch head after TEMP workflow cleanup: `55672125a463bbc88201ede1ce54d87daf75e658`
- Domain remains `pending` / `domain_work`; **do not mark ready_for_integration yet**.
- `main` is ahead because other canonical lanes continued integrating. Treat branch divergence as an integration concern; do not restart this domain inventory.

## Permanent hardening completed in this session

### Login Bonus

The prior checkpoint covered only `text_data_dict.json [171,13]`. Active retrospective-corpus inventory found the same exact player-facing label at `[171,12]` as well. W4 now materializes separate item-scoped records for both paths:

- `登录奖励` at `[171,12]` -> `Login Bonus`
- `登录奖励` at `[171,13]` -> `Login Bonus`

Both canonical/community rules are exact-path guarded; the old calque `Phần thưởng đăng nhập` is forbidden only in those verified UI items. Generic login/reward prose remains outside the rule.

Materialization checkpoint commit: `3528a3d647a28c3321f277f349b2428e2d25d4ff`.

### Missions / event navigation labels

Inventory of short mission/reward labels in the active retrospective plan found verified standalone UI labels and explicit prose/skill hazards. W4 added exact-key rules only for:

- `任务` -> `Nhiệm vụ` at `localize_dict.json [Home0011]`
- `活动任务` -> `Nhiệm vụ sự kiện` at `[StoryEvent0044]`
- `活动\n任务` -> `Nhiệm vụ\nsự kiện` at `[StoryEvent0024]` and `[CollectEvent508007]`
- `活动点数` -> `Điểm sự kiện` at `[StoryEvent0022]`

Explicit negative coverage protects at least:

- skill-like `任务：凯旋`
- prose `海外诞生，沉默寡言的任务执行者`
- sentence `活动期间外，不能挑战活动任务`

Materialization checkpoint commit: `65f0f29666ab4245e93612a49746ca1dbc1f0ced`.

### Reward claim / receive-state labels

W4 added exact-key rules for verified compact UI actions/statuses:

- `领取` -> `Nhận` at `[Present0003]`
- `领取奖励` -> `Nhận phần thưởng` at `[StoryEvent0054]`
- `已领取` -> `Đã nhận` at `[Present0016]`
- `未领取` -> `Chưa nhận` at `[Present0009]`
- `领取期限` -> `Hạn nhận` at `[TransferEvent0003]` and `[Present0040]`

Explicit negatives protect full sentences such as browser/reward instructions, `领取期限已结束`, and event prose containing `未领取`.

Reward materialization commit: `b1748f8a238c95988735b70753de36064cbc6fe8`.

## Validation evidence

GitHub Actions was used because the Shiro execution backend returned transient 429s. Backend failure was treated as local per repository policy, not as a task-level blocker.

Validation progressed with each substantive batch:

1. Existing Login Bonus branch state: 5 focused tests passed; 201 full pytest passed; `tlvi validate` clean; index succeeded for 8 files.
2. Scoped Missions/Event labels: 13 focused tests passed; 209 full pytest passed; `tlvi validate` clean; index succeeded for 8 files.
3. Final materialized reward-claim state: **20 focused tests passed; 216 full pytest passed; `tlvi validate` returned `ok: true` with zero errors/warnings; index succeeded for 8 files**. The final validated product state is represented by test commit `c0e4c75a728f65550cd3c9b8f3022cb4242ab7dd`, whose history includes reward materialization `b1748f8a238c95988735b70753de36064cbc6fe8`.

TEMP validation/materialization/inventory workflows were removed before handoff. Comparing the clean branch to live main now shows only these permanent domain files:

- `glossary/term_registry.json`
- `glossary/ui_community_terms.json`
- `scripts/harden_missions_events_canon.py`
- `tests/test_missions_events_hardening.py`

## Follow-up inventory / remaining work

A targeted active-corpus scan for `每日任务|每周任务|日常任务|周常任务|主线任务|任务进度|任务完成|完成任务|任务达成|获得报酬|领取报酬|活动奖励|个人奖励|全体奖励|奖励一览|报酬一览` found **25 distinct / 34 items** but no Daily/Weekly/Main Mission label hits. Do not invent those canonical mappings from the task name alone; they still need repository evidence from another source/corpus path if they exist.

High-value remaining evidence-backed candidates for the next W4 takeover include:

- `获得报酬` -> current `Nhận thưởng`, 4 standalone occurrences: `Champions0024`, `Champions0030`, `Champions0076`, `Common0164`.
- `报酬一览` -> current `Danh sách phần thưởng`, 2 occurrences: `Race0260`, `TrainingChallenge4080016`.
- `活动个人奖励` -> current `Thưởng cá nhân`, 2 occurrences: `FanRaid424003`, `CollectEvent508002`.
- `活动全体奖励` has 2 occurrences with **conflicting current targets** (`Thưởng chung` vs `Thưởng chung sự kiện`), so resolve meaning/standard before locking.
- `活动奖励` -> current `Thưởng sự kiện` at `FanRaid400102`.
- Long event-reward sentences and `活动奖励领取时间已结束` must remain prose/context candidates, not be captured by short-label canonical rules without specific evidence.

Also continue objective/progress/clear/completion-label evidence search. The active review scan did not justify Daily/Weekly/Main Mission mappings this session.

## Handoff rule

Resume this branch/checkpoint; do not restart broad inventory. Continue only evidence-backed, scoped labels with wrong-path/prose negatives. Do not integrate to live main from the parallel domain lane. When substantive Missions/Events coverage is genuinely complete, follow the live `ready_for_integration` protocol and let the serialized primary lane perform integration/Sync/no-op proof.
