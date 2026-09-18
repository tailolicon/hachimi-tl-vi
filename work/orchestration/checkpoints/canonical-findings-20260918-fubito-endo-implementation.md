# Canonical finding implementation — Fubito Endo credit (2026-09-18)

Finding: `cf-6ff2aa5d2b9f58ce`
Source name: `遠藤フビト`
Verified Latin spelling: `Fubito Endo`

## Evidence

- Official Uma Musume/Lantis release credits identify `遠藤フビト` as lyricist for Uma Musume songs including WINNING LIVE 07 / `笑顔の宝物 -Beyond The Future!-`.
  - https://umamusume.lantis.jp/discography/winning-live-07/
- Uta-Net's English lyricist index renders the same creator as `FUBITO ENDO`.
  - https://www.uta-net.com/global/en/lyricist/40521/
- Music metadata independently maps `遠藤フビト` to `Fubito Endo`.
  - https://musicbrainz.org/artist/4ac7f6ea-cdb6-4fed-af78-c1b96eacc727/works

## Permanent fix

- Add `scripts/harden_fubito_endo_finding.py`.
- The hardener creates a category-17-only proper-name community rule:
  - `遠藤フビト → Fubito Endo`
  - source path `text_data_dict.json`
  - json path prefix `17`
  - `match_mode=contains`
  - source CJK spelling forbidden in clean Vietnamese credit output.
- The hardener also persists reviewed decision `audit.finding.fubito-endo-credit` so normal Sync can materialize the locked term registry entry.
- Add `tests/test_fubito_endo_finding_hardening.py` proving idempotence, positive category-17 resolution, and negative scope outside category 17 / text_data.

## Validation

- Focused creator-name tests: 4 passed.
- Full repository suite: 872 passed.
- Isolated live finding simulation resolves exactly to:
  `{"layer":"community","term_id":"proper_name.fubito_endo.credit17","target_vi":"Fubito Endo"}`.
- A whole-ledger manual refresh was intentionally not applied because unrelated stale context hashes would reopen other findings; production Sync remains the authority for global refresh.

Production Sync verification is required before incrementing maintenance `completed_count`.

## Production acceptance — complete

- Implementation commit: `02d2196687fb6e0f2bd8c395b22187712fe2aaea`.
- Validate run `35303464140`: success.
- First production Sync `35303464131`: success.
- Live canonical finding `cf-6ff2aa5d2b9f58ce` is non-active under `scripts/canonical_findings.py::active_findings` because it has locked canonical resolution `Fubito Endo`.
- Live review lock: `audit.finding.fubito-endo-credit` → `Fubito Endo`.
- Unchanged production Sync `35317741599`, job `105513018621`: success.
- Fubito Endo hardener reported `fubito_endo_hardening_changed=false` in both hardener passes.
- Full context pipeline: `878 passed`.
- Exact no-op proof: `Context is already current.`

## Accounting

This finding is complete and is eligible to increment maintenance `completed_count` exactly once.
