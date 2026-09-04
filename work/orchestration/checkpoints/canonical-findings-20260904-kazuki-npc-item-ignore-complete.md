# Canonical findings maintenance checkpoint — Kazuki NPC item ignore accepted

Finding `cf-903f94a51b0e869e` (`和树(NPC)`) is accepted as an item-scoped ignore rather than a reusable romanization lock.

## Durable implementation

- Hardener: `scripts/harden_kazuki_npc_finding.py` at `da17d8d9eef7c353f4db28653e93a6f0c99e0676`.
- Regression: `tests/test_kazuki_npc_finding_hardening.py` at `407841aad6c8e49ae070787b80bdf843732a821c`.
- Scope is limited to exact `text_data_dict.json` category-152 item paths `2`, `36`, `70`, `104`, `138`, `172`.
- The resolution deliberately does not canonize `Kazuki` and does not broaden matching to category `152`.

## Acceptance evidence

All required production workflows on regression head `407841aad6c8e49ae070787b80bdf843732a821c` completed successfully:

- Validate run `33897394422`: success.
- Sync translation context run `33897394450`: success.
- Sync translation review plan run `33897394423`: success.

Live regenerated review artifact `b0135` shows `text_data_dict.json` path `152/104` for `和树(NPC)` with `canonical_findings: []`, while adjacent unrelated category-152 proper-name findings remain review risks. This verifies the resolution stayed item-scoped.

Maintenance sequencing may advance `completed_count` from 113 to 114. Successor routing must re-read live main before selecting the next unresolved finding.
