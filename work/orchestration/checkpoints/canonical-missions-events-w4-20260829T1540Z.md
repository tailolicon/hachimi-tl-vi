# canonical-missions-events W4 checkpoint — 2026-08-29T15:40Z

## Routing

- Domain: `canonical-missions-events`
- Branch: `canonical-missions-events-hardening`
- Branch head at checkpoint: `afe954006669a52fd9d5282e4f0576f751c6ad8c`
- This is parallel domain work only. No canonical publication, production Sync, or global phase transition was performed.

## Durable work completed

1. Added `scripts/harden_missions_events_canon.py` on the domain branch.
2. Added `tests/test_missions_events_hardening.py` with positive, historical-calque rejection, wrong-path/prose negative, and idempotency coverage.
3. First hardened concept is the verified `登录奖励` player-facing label at `text_data_dict.json` path `171/13`, mapped narrowly to `Login Bonus` with item-scoped invalidation.
4. The hardener deliberately does **not** globally lock generic login/reward words or generic `任务` prose.

## Evidence

- Existing retrospective review item: `zhcn:a16dc2bbf220f3fee526789f`, source `登录奖励`, `text_data_dict.json` path `[171,13]`, current target `Phần thưởng đăng nhập`; no locked/community terms were present in that item before this branch work.
- Existing matcher implementation in `scripts/translation_review_common.py` checks `source_paths`, `json_path_prefixes`, and exact-vs-contains matching before emitting locked/community matches.
- Static execution of the same matcher predicates confirmed: exact `[171,13]` + `登录奖励` matches; `[171,99]` does not; prose `登录后可以领取奖励` does not; historical target `Phần thưởng đăng nhập` is detected as forbidden.

## Execution status

- GitHub Actions has no workflow run for this branch yet.
- Shiro execution backend returned MCP tunnel 404/429.
- Local container fallback could not clone GitHub because DNS resolution for `github.com` failed.
- Therefore **do not claim pytest/full validation passed yet**. The regression test file is durable but execution evidence remains pending.

## Next safe work

Continue this same branch; do not restart broad inventory. Run `pytest -q tests/test_missions_events_hardening.py` as soon as an execution path is available, then continue evidence-backed inventory for Daily/Weekly/Main mission labels, claim/receive/reward labels, event mission/event points, and recurring campaign/system labels. Keep objective prose and event proper names negative. Only set `ready_for_integration` after substantive domain coverage, permanent materialized glossary changes, and regression evidence are complete enough for serial finalization.
