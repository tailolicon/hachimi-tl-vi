# Canonical findings completion — Uma Plan

Claim: `canonical-findings-maintenance-gpt56sol-20260904T115724Z`

## Resolved findings

Two active canonical findings were proven to be the same official Cygames subscription brand and are now covered by one narrowly-scoped canonical rule:

- `cf-17893bf4fbdc7e87` — `localize_dict.json` / `Character608001` — source contains `马娘计划` in `购买马娘计划后解锁`.
- `cf-3d858d453b1065a8` — `localize_dict.json` / `Character701022` — source contains `马娘计划` in the daily-use-count subscription notice.

Official JP identity: `ウマプラン`.
Player-facing Vietnamese canonical target: `Uma Plan`.

Authoritative Cygames references:
- https://umamusume.jp/news/detail?id=3078 — 2026-02-24 announcement `新月額サービス「ウマプラン」販売開始！`.
- https://umamusume.jp/steam-news/detail?id=3097 — official portal usage of the same branded service name.

## Canonical implementation

Permanent hardener: `scripts/harden_uma_plan_finding.py`.
Regression: `tests/test_uma_plan_finding_hardening.py`.

The canonical rule is intentionally item-scoped:
- source path: `localize_dict.json`
- exact keys: `Character608001`, `Character701022`
- alias: `马娘计划`
- match mode: `contains` because the branded alias occurs inside longer UI strings
- preferred/accepted target: `Uma Plan`
- unrelated occurrences of the same generic source characters outside these proven keys remain unmatched by regression test.

The hardener also removes the initial one-key legacy term id and replaces it with the consolidated `system.uma_plan.subscription` rule.

## Acceptance evidence

- Validate workflow `33871375792`: success.
- Production context Sync `33871375789`: success; full suite `676 passed`; generated worker-facing context refreshed.
- Translation review-plan Sync `33871375791`: success; full suite `676 passed`; plan builder reported active plan `tr-p3-67f8551f7780-dd1bd54ee1ef-b5c0bcb3bd-a046bd2daf`, candidate count `3932`, and canonical terminology/review plan already current.
- Generated context persistence resolved the original `cf-17893bf4fbdc7e87` to `Uma Plan` and reduced the open canonical queue 148 → 147.
- After widening to the second proven UI key, generated context persistence resolved `cf-3d858d453b1065a8` to `Uma Plan` and reduced the open canonical queue 147 → 146.

Both finding IDs therefore satisfy canonical acceptance rather than merely having a source hardener committed.
