# Matikanefukukitaru zero-width guard conflict — fixed

A live translation shard exposed a deterministic canonical conflict for `待兼福来`: `glossary/term_registry.json` deliberately locks the clean player-facing spelling `Matikanefukukitaru`, while the verified `characters.json` record currently contains an embedded U+200B separator (`Matikane\u200bfukukitaru`). The previous `TranslationQualityGuard` enforced both strings independently, so no single clean player-facing target could pass.

Implemented on `main` in commit `d72846247`:

- character canonical validation now strips only ignorable generated separators U+200B/U+200C/U+200D/U+FEFF before matching;
- visible character-name spelling and verified game-ID enforcement remain unchanged;
- regression coverage adds the real conflict shape and proves clean `Matikanefukukitaru` passes while an unrelated name is still rejected.

Validation after rebase/push:

- `UV_CACHE_DIR=.uv-cache uv run --with pytest pytest tests/test_translation_guard.py -q` → `10 passed`;
- the previously blocked `batch-01631-s01` entry `zhcn:633d837f6ad34a7e80494cb0` validates cleanly with `Số fan của Matikanefukukitaru\\nđạt tổng cộng 5000 vạn`.

Resume mass routing and reclaim `batch-01631-s01` from its 19/20 released checkpoint to finalize it.