# Canonical finding checkpoint — Tanino Gimlet scoped-resolution gap

- Finding: `cf-46c6157b0331a647` (`神话、哲学、Vu行的发音、业余木工`).
- Production hardener entry point: `scripts/harden_tanino_gimlet_v_row_source_bridge_finding.py` from commit `0b72038ba5a84d0af7b63bc541e61388f90a957a`.
- Validate run `34081865465` succeeded.
- First production Sync run `34081865411` attempt 1 succeeded, ran the hardener, passed 794 tests, and published regenerated context.
- Live regenerated ledger still has `canonical_resolution: null` for this finding while its `review_resolution` is the expected lock to `Thần thoại, triết học, phát âm các âm V, làm đồ gỗ DIY`.
- Root cause identified from live data/code: the finding has no top-level `json_path_prefixes`, although its sole evidence record is at `text_data_dict.json` path `["164", "1084"]`; the source-bridge rule is deliberately scoped to that exact path. `_rule_covers_finding` currently rejects any scoped rule when the finding-level prefix list is empty, so the canonical resolver cannot consume the evidence path and leaves the finding active.
- Permanent test currently seeds the finding with `["164", "1084"]`, so it does not reproduce the live aggregation shape and therefore missed this production-resolution gap.
- Sync run `34081865411` attempt 2 is currently in progress. Do not mark this finding complete merely from the existing review lock or from the first successful Sync. Completion requires a live non-active canonical resolution plus a successful unchanged production Sync.
- Next implementation step: harden canonical-finding scope derivation so a finding with absent aggregate prefixes can safely derive scope from its concrete evidence paths (and require all usable evidence paths to be covered), then add a regression test using the live shape before rerunning Validate/Sync.
