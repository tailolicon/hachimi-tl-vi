# Canonical finding acceptance: Masataka Usui

Finding `cf-130ec8abcb039482` (`碓井雅隆`) is accepted as `Masataka Usui`.

Durable canonical hardening is live on `main` at `fc541cba1dfe87f928110c2bf3f4a49ea4be9a4b` via `scripts/harden_masataka_usui_finding.py`, with permanent regression coverage in `tests/test_masataka_usui_finding_hardening.py`. The rule is item-scoped to creator/staff credit text in `text_data_dict.json` and uses `match_mode: contains` for the full creator name.

Evidence basis: cross-language music metadata for the same Umamusume WINNING LIVE 06 tracks identifies the Latin spelling `Masataka Usui`, while Japanese release/lyrics catalogs identify the creator as `碓井雅隆 (Cygames)`.

Production acceptance for commit `fc541cba1dfe87f928110c2bf3f4a49ea4be9a4b`:

- Validate run `33860788002`: success.
- Sync translation context run `33860787918`: success.
- Sync translation review plan run `33860787844`: success.

The unrelated Sync UI review plan run failed and is not a required canonical-finding acceptance gate for this maintenance unit. Do not double-count this finding on future regenerated-state refreshes.
