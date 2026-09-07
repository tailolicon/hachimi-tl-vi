# Canonical finding checkpoint: cf-735331afc1ace008

Finding: `奔跑到何处` (exact song-title row in `text_data_dict.json`).

## Identity evidence

Repository evidence already mapped the zh-CN title to JP `どこまで走れば` but previously deferred an English lock because the evidence was too weak. Fresh storefront verification now supplies the missing authoritative English-facing identity: Apple Music US and Amazon Music list the WINNING LIVE 22 track for Win Variation (CV: Hika Tsukishiro) as `How Far Must I Run?`; community metadata independently matches the JP title `どこまで走れば` to the same track.

## Implementation on live main

- hardener: `scripts/harden_how_far_must_i_run_finding.py`
- hardener commit: `eb1610975e86d455761a15377c5019e2a0f201ec`
- regression: `tests/test_how_far_must_i_run_finding_hardening.py`
- regression commit: `8a48ea32819d0faa82c54ae0250276db968a0a00`
- community rule: `song.how_far_must_i_run`
- review decision: `audit.finding.song-how-far-must-i-run`
- target: `How Far Must I Run?`
- scope: exact `奔跑到何处` in `text_data_dict.json`, item-level invalidation; longer prose and other files are explicitly regression-protected from overmatch.

## Acceptance pending

Validate run `34155751198` started from the regression commit. Production Sync run `34155737079` started from the hardener commit and queued follow-up Sync `34155751136` from the regression commit. Do not increment maintenance accounting above 200 until Validate succeeds, a production Sync materializes/resolves the finding, and a second unchanged production Sync succeeds with `how_far_must_i_run_hardening_changed=false` and exact final no-op `Context is already current.`.
