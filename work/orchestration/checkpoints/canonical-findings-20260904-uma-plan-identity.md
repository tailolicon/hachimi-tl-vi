# Canonical finding checkpoint — Uma Plan identity

Claim: `canonical-findings-maintenance-gpt56sol-20260904T115724Z`
Finding: `cf-17893bf4fbdc7e87`
Source alias: `马娘计划`
Observed item: `localize_dict.json` key `Character608001`, source text `购买马娘计划后解锁`, current Vietnamese previously observed as `Mở khóa sau khi mua Gói Umamusume` / conceptually `Gói Umamusume`.

## Verified identity

Cygames' official Uma Musume JP portal explicitly names the subscription service `ウマプラン` in the 2026-02-24 announcement `新月額サービス「ウマプラン」販売開始！`. The same official portal states it is a monthly service and repeats the exact branded name throughout the purchase/help instructions. A separate official 5th-anniversary announcement also introduces the same service as `ウマプラン`.

Authoritative references:
- https://umamusume.jp/news/detail?id=3078
- https://umamusume.jp/steam-news/detail?id=3097

This establishes that zh-CN `马娘计划` is a bridge rendering of the branded JP service name, not a generic phrase meaning an arbitrary "Umamusume package/plan".

## Canonical direction

Recommended player-facing target: `Uma Plan`.

Rationale:
- preserve the official JP brand identity (`ウマ` → `Uma`, `プラン` → `Plan`) rather than translating it as a generic Vietnamese package label;
- repository policy prefers official JP identity when no released Global terminology is available;
- scope should remain narrow/item-scoped to the proven subscription UI occurrence(s), initially `localize_dict.json` key `Character608001`, with `match_mode=contains` because `马娘计划` occurs inside the longer source string `购买马娘计划后解锁`;
- do not use `match_mode=exact` for this finding because the alias is only a substring of the reviewed item.

## Next implementation step

Add a permanent idempotent hardener + regression test that locks `马娘计划` to `Uma Plan` only in the proven subscription UI scope, then run repository validation and production context/review-plan Sync. Confirm live `glossary/canonical_findings.json` receives a non-null `canonical_resolution` for `cf-17893bf4fbdc7e87` and the regenerated review item no longer carries the blocking finding.
