# Canonical finding maintenance checkpoint — ぶっちぎりロード / 冠绝之路

Finding: `cf-c54e95a392368cab`

## Live evidence

The current production retrospective plan `tr-p3-67f8551f7780-116121e718ef-b5c0bcb3bd-6fad1b114f` still embeds this finding as an active blocker for `text_data_dict.json` category `147`.

- zh-CN source: `冠绝之路`
- current Vietnamese: `Con đường độc tôn`
- JP-backed curation identity: Skill `100641`, `ぶっちぎりロード`
- existing source-bridge policy explicitly says the zh-CN title is an interpretive rewrite of the JP colloquial/loanword title and must not be calqued.

Fresh external verification in this worker run confirms `ぶっちぎりロード` is Mejiro Palmer's unique Skill and the JP effect text matches the known Skill identity. GameWith (updated 2026-07-20) and Game8 (updated 2026-05-18) both identify the title and owner consistently.

## Decision status

Do **not** accept `Con đường độc tôn` and do not lock a replacement merely by translating `冠绝之路`; that would violate the existing source-bridge risk.

The JP identity is now independently corroborated, but this checkpoint intentionally does not invent a Vietnamese canonical title without repository-backed style/equivalence evidence or an authoritative Global title. The next maintainer should resolve from JP/official Global naming, then add the permanent hardener + regression and run production Validate + Context Sync + Review-plan Sync.

Maintenance `completed_count` remains `130`.
