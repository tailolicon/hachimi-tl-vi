# Canonical finding checkpoint — 固有加成 conflicting implementation removed

Finding: `cf-5cc239af1c9d7710` (`固有加成`).

A concurrent same-lane integration briefly added `scripts/harden_unique_effect_finding.py` / `tests/test_unique_effect_finding_hardening.py` with target `Unique Effect` and `match_mode=exact`.

That implementation was rejected before production acceptance because:

1. `target_vi` must be Vietnamese; fresh identity evidence uses English `Unique Effect` only as the cross-locale identity and recommends canonical VI `Hiệu ứng riêng`.
2. Live worker policy requires a reusable source alias to remain `contains`-matched with scope guards. `固有加成` occurs inside `固有加成详情`, so exact matching is not protocol-valid for the shared alias.
3. Keeping both implementations would create duplicate canonical terms/review decisions for the same zh-CN source and risk split-brain resolution.

The conflicting hardener was removed at `fbadb8c901d99870329d5cc9b46d5afd65e7b310`; its regression was removed at `103915623a3cdeb0ead953d37229eb8f533bda7f`.

The surviving live-main implementation is `scripts/harden_support_unique_effect_label_finding.py` + `tests/test_support_unique_effect_label_finding_hardening.py`, target `Hiệu ứng riêng`, `contains`, scoped to `localize_dict.json` keys Character0050 / Character0196.

Validate and Context Sync triggered from the cleaned head must be used for final acceptance. Do not increment `completed_count` until production Sync + second unchanged no-op Sync prove the ledger is stable.
