# Canonical finding prepared — 堀江晶太 / Shota Horie

Finding: `cf-9912f84bf82c3999` (`堀江晶太`), creator/staff credit in `text_data_dict.json`.

Evidence:

- Sony Music official PENGUIN RESEARCH profile maps `堀江晶太` to `SHOTA HORIE`: https://www.sonymusic.co.jp/artist/penguinresearch/profile/
- Lantis official Umamusume WINNING LIVE 09 credits `堀江晶太` as composer/arranger for `Ms. VICTORIA`: https://umamusume.lantis.jp/discography/winning-live-09/

Prepared locally, not published yet:

- `scripts/harden_shota_horie_finding.py`
- `tests/test_shota_horie_finding_hardening.py`
- focused regression: `2 passed`
- test covers existing `defer` being superseded by verified canonical resolution
- intended mapping: `堀江晶太` -> `Shota Horie`, `text_data_dict.json` only, `match_mode=contains`, item-scoped invalidation.

Publication is intentionally held until Shunryu production Sync + unchanged no-op Sync acceptance completes.

Implementation applied to live-main snapshot locally:
- hardener first run: `changed=true`
- unchanged second pass: `changed=false`
- focused regression, including superseding an existing defer: `2 passed`
- no direct localized-data patching.

Next: publish implementation, run Validate, production Sync, verify live resolution, then second unchanged Sync before maintenance accounting.
