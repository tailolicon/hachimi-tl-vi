# Canonical finding implementation — Peep Peep Pow!

Finding: `cf-d3f7dc3b11c9e480`

- live zh-CN title: `看我不把你整得头冒金星！`
- JP title: `ピヨっピヨにしてやんよッ！`
- live item: `text_data_dict.json` category `16`, entry `1160`
- canonical target: `Peep Peep Pow!`

## Evidence basis

The live zh-CN title maps to Espoir City's `WINNING LIVE 23` solo song `ピヨっピヨにしてやんよッ！`. Lantis-distributed English catalog/storefront metadata (including CDJapan, Amazon Music, and Apple Music) publishes the track as `Peep Peep Pow!`. Preserve that stable English-facing proper-name identity instead of the semantic Vietnamese rendering `Xem tôi có đánh cho bạn hoa mắt không nào!`.

## Implementation

- regression: `tests/test_peep_peep_pow_finding_hardening.py`
- hardener: `scripts/harden_peep_peep_pow_finding.py`
- community rule: `song.peep_peep_pow`
- terminology decision: `audit.finding.song-peep-peep-pow`
- source scope: exact match in `text_data_dict.json`

Implementation commits on live `main`:

- regression commit `ef892ff80b4b47d64c0df76de644744cd33d24c4`
- hardener commit `e78e5c0d8ed6f9b7129080b40da11ac8cc222a7d`

## Acceptance status

Pending production acceptance. Do not advance the maintenance completed count until required Validate, Sync translation context, and Sync translation review plan workflows succeed and the then-live generated review item `text_data_dict.json` `16/1160` embeds `song.peep_peep_pow` / `Peep Peep Pow!` with `canonical_findings: []`.
