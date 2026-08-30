# Canonical findings maintenance checkpoint — wave 3

Confirmed baseline carried into this wave: **30 live-resolved findings**.

Additional durable work after that baseline:

## Verified proper-title hardeners

All are exact-match, item-scoped song/title rules with explicit review locks and positive/negative regression coverage; the production Sync auto-discovers them through `scripts/harden_*_finding.py`.

- `光の後ろ姿` → `Hikari no Ushiro Sugata`
- `楽園` → `Rakuen`
- `彼方へ…` → `Beyond the Horizon`
- `帝笑歌劇〜讃えよ永久に〜` → `Teishou Kageki ~Tataeyo Towa ni~`
- `ぱか☆アゲ↑ミックス` → `Paka Age Mix`
- `シャドーロールの誓い（The Solid Revision）` → `Shadow Roll no Chikai (The Solid Revision)`
- `ささやかな祈り` → `Sasayaka na Inori`

## Explicit blocking defers

When identity evidence remained insufficient, no guessed project-wide target was introduced. Durable empty-target `action=defer` decisions now preserve that state for:

- `等级奖牌`
- `スタホTV`
- `热血誓言`
- `英雄的光辉`
- `待春之蕾`

These defers intentionally remain unresolved/blocking and must not increment the resolved-finding counter.

## Systemic pipeline guards

- hardener-generated `glossary/terminology_reviews.json` is persisted by production Sync;
- production Sync auto-runs every `scripts/harden_*_finding.py`;
- full `pytest -q` remains mandatory;
- permanent workflow tests guard both persistence and auto-discovery.

Do not count the pending title rules as resolved until a green production Sync and live generated `glossary/canonical_findings.json` confirm each canonical resolution.
