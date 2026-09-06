# Canonical finding research — 大丰食祭

Finding: `cf-5310cb8fbcc8798f`

## Live finding state

The current canonical-findings ledger shows this as an active blocker:

- status: `open`
- source alias: `大丰食祭`
- match mode: `contains`
- source: `localize_dict.json`
- kind: `proper_name`
- concept: Cooking scenario/event title
- current Vietnamese evidence includes `Đại Lễ hội Ẩm thực`
- `canonical_resolution: null`
- `review_resolution: null`

## Verified identity evidence

Official Japanese/Cygames-distributed coverage identifies the scenario title as `収穫ッ！満腹ッ！大豊食祭`, released in JP on 2024-06-26. The zh-CN alias `大丰食祭` is therefore the short component of that named scenario, not a generic food-festival phrase.

Fresh external verification also shows that, as of 2026-09-06, this scenario is still not available in the official Global release. The maintained Umamusume Wiki explicitly marks the content JP-only for Global and records:

- Kanji: `収穫ッ！満腹ッ！大豊食祭`
- Romaji: `Shuukaku! Manpaku! Daihoushokusai`
- community English label: `Hearty! Harvest! Gourmet Festival!`

Because repository policy prefers official Global terminology when available, then official JP identity, then community usage, the community English label should not be locked as if it were an official Global localization. The existing semantic Vietnamese `Đại Lễ hội Ẩm thực` likewise lacks identity authority.

## Safe continuation

Do not resolve this finding by guessing an English or Vietnamese title. Next maintenance step should inspect repository precedent for JP-only scenario proper names and either:

1. lock a narrow JP-identity/Romanized form consistent with existing precedent, or
2. record an explicit defer rationale if the project intentionally waits for future official Global localization.

No canonical count increment is justified by this research checkpoint alone.
