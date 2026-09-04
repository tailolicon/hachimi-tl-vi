# Canonical finding diagnosis — Uma Musume Stakes after Air Messiah acceptance

Finding: `cf-0dae34861911a969`
Source alias: `赛马娘锦标`
Target: `Uma Musume Stakes`

Live state after Air Messiah production Sync:
- `glossary/canonical_findings.json` still exposes this finding as `status: open` with `canonical_resolution: null` and `review_resolution: null`.
- Evidence remains the `text_data_dict.json` text containing `取得3次带有「赛马娘锦标」名称的赛事的胜利...`.
- Current hardener `scripts/harden_uma_musume_stakes_component_finding.py` already defines `race.uma_musume_stakes.component131`, source alias `赛马娘锦标`, `match_mode: contains`, source path `text_data_dict.json`, and explicitly empty `json_path_prefixes`.
- The hardener also excludes `赛马娘锦标` from generic `common.world.umamusume` matching.
- Prior checkpoint `canonical-findings-20260903-uma-musume-stakes-live-scope-repair.md` documents the same historical failure mode: stale category-131 scope could not cover the live source-path-scoped finding.

Therefore do not redo identity research. Next step is persistence/production diagnosis: inspect the materialized live `race.uma_musume_stakes.component131` record in `glossary/ui_community_terms.json` and the matching terminology review decision, verify whether stale `json_path_prefixes` survived despite the current hardener, then repair the materialized canonical records or refresh path as required. Acceptance still requires Validate + Sync translation context + Sync translation review plan and a regenerated ledger/batch where this finding has a non-null canonical resolution / is absent from active findings.
