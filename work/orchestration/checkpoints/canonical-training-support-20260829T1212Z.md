# canonical-training-support checkpoint — 2026-08-29T12:12Z

Task: `canonical-training-support`
Stage: `domain_work`
Branch: `canonical-training-support-hardening`

## Durable progress

- Live orchestration selected Training / Support / progression after Race completion.
- Confirmed the maintenance branch had no task-specific commits before this session and was only behind `main`.
- Found a concrete systemic canonical defect in the current retrospective review context: `system.friendship_training` matched zh-CN `友情训练` but still required the historical Vietnamese target `Huấn luyện Hữu nghị`; representative current corpus items instead contain natural calques such as `huấn luyện tình bạn`, so the lock is both player-facing-inconsistent and already generating mismatches.
- External terminology verification supports `Friendship Training` as the established English player-facing name; generic bare friendship/training prose must remain natural language.
- Added permanent `scripts/harden_training_support_canon.py` on the task branch. It updates only the full `友情トレーニング` / `友情训练` mechanic compound to `Friendship Training`, sets item-scoped invalidation, and adds a community guard forbidding the historical Vietnamese calques.
- Added `tests/test_training_support_hardening.py` covering: positive full-compound match, historical-calque rejection, negative ordinary prose, and hardener idempotence.

## Branch evidence

- Hardener commit: `ec320abe0382029832fb9731e2855689f7fd6e85`
- Regression commit: `81848fc941d543d335e2b6d96f31c2e59ed2eac5`

## Next work

Continue the same domain; do not finalize yet. Inventory the remaining high-frequency Training/Support concepts from live corpus/canonical layers, especially Support Pt, Bond/Friendship Gauge, Energy, Training Level/facility level, failure-rate UI, and repeated support-effect labels. Only add rules with verified player-facing identity and source/context guards. Then run the full test/validation contract before transitioning to `ready_for_finalize`.

Local shell execution was unavailable because the environment could not resolve github.com, so these new tests have not yet been executed in this session. Do not claim completion until repository execution evidence is green.
