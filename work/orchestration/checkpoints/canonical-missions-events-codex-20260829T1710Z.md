# Canonical Missions / Events checkpoint — 2026-08-29T17:10Z

## Ownership and branch

- Domain: `canonical-missions-events`
- Claim: `canonical-missions-events-codex-20260829T1653Z`
- Branch: `canonical-missions-events-hardening`
- Durable branch head: `4b82e55ceddb840383b69d24491ef2119ec2ec55`
- Domain remains `pending` / `domain_work`; do not publish these changes directly to `main`.

## Permanent hardening added

Added exact-key, item-scoped canonical/community rules and permanent regression coverage for:

- `获得报酬` -> `Nhận thưởng` at `Champions0024`, `Champions0030`, `Champions0076`, and `Common0164`.
- `报酬一览` -> `Danh sách phần thưởng` at `Race0260` and `TrainingChallenge4080016`.
- `活动个人奖励` -> `Thưởng cá nhân` at `FanRaid424003` and `CollectEvent508002`.
- `活动奖励` -> `Thưởng sự kiện` at `FanRaid400102`.
- `活动全体奖励` -> `Thưởng chung` at `FanRaid424002` and `CollectEvent508001`, resolving the prior split between `Thưởng chung` and the unnecessarily verbose `Thưởng chung sự kiện`.

Long event-reward sentences and fabricated/wrong keys are explicit negative cases so the short-label rules do not overmatch prose.

## Validation

At the final materialized state:

- focused Missions/Events suite: **31 passed**;
- full suite: **227 passed**;
- `tlvi validate`: `ok: true`, zero errors/warnings;
- `tlvi index`: succeeded for 8 files;
- hardener reran idempotently through the permanent idempotence test.

## Remaining evidence work

Do not invent Daily/Weekly/Main Mission mappings: the active corpus scan still contains no verified standalone hits.

Continue the bounded objective/progress/clear/completion review. A verified standalone candidate is `达成条件` at `SingleMode0498`, currently `Điều kiện đạt được`, but its compact Vietnamese standard still needs a deliberate UI/terminology decision before locking. Keep generic `已完成` prose and long reward sentences negative.

Resume this branch and checkpoint; do not restart broad inventory.
