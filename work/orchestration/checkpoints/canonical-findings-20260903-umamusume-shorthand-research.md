# Canonical findings maintenance research — 马娘 shorthand in character profile text

Claim: `canonical-findings-maintenance-auto11-20260903T082829Z`
Finding: `cf-cd337bc7f688a0d4`

The rebuilt live review plan `tr-p3-67f8551f7780-a680c10c6dd2-b5c0bcb3bd-fb07a29806` places this finding at the head of priority work. It is a `contains` finding for zh-CN `马娘` under `text_data_dict.json` category `144`, with suggested Vietnamese target `Mã Nương` and concept `Generic horse-girl species shorthand`.

Live category-144 evidence includes multiple character-profile taglines ending in `赛马娘`, for example:

- `涡轮全开！\n不受极限束缚的暴走赛马娘！`
- `追求着所憧憬的！\n坦率的努力家赛马娘`
- `成为世上最闪耀的星！\n充满魅力的野心家赛马娘`
- `以武代礼，全力奔跑。\n武痴赛马娘`

The authoritative community registry already locks generic `赛马娘` to `Mã Nương` via `common.world.umamusume`, and these profile strings are exactly generic species references, not the full product title. The open finding exists because worker evidence used the shorter contained zh-CN token `马娘`, which is not itself an alias covered by a canonical rule broad enough to resolve that finding.

Hardening direction:

- add a category-144, text-data-scoped supplemental community rule for contained `马娘` -> `Mã Nương`;
- keep it scoped to character-profile category 144 rather than adding `马娘` as a global alias, because the shorter token is more collision-prone than full `赛马娘`;
- preserve existing `common.world.umamusume` as the general species canonical and use the supplemental rule only to close the worker-reported shorthand finding safely;
- regression must prove category-144 profile text matches the shorthand rule, while the same substring outside category 144 does not gain this supplemental match;
- canonical-finding refresh must resolve `cf-cd337bc7f688a0d4` through the scoped community rule.
