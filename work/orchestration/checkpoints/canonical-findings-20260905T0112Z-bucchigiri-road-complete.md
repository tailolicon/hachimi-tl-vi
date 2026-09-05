# Canonical finding maintenance completion — ぶっちぎりロード / 冠绝之路

Finding: `cf-c54e95a392368cab`

## Resolution

Accepted canonical target: `Keep Pushing Ahead`.

The old Vietnamese `Con đường độc tôn` came from the zh-CN bridge `冠绝之路` and is rejected as a backward calque. Existing curation had already pinned Skill 100641 to JP `ぶっちぎりロード` and marked the Chinese title as an interpretive rewrite. Fresh identity verification confirmed this is Mejiro Palmer's unique Skill, while the English release supplies the stable title `Keep Pushing Ahead` for Mejiro Palmer [Line Breakthrough].

Permanent hardening:

- `scripts/harden_bucchigiri_road_finding.py`
- rule `skill.mejiro_palmer.keep_pushing_ahead`
- exact source `冠绝之路`
- scope `text_data_dict.json` category `147`
- item-scoped invalidation
- terminology decision `audit.finding.skill-mejiro-palmer-keep-pushing-ahead`
- forbidden legacy target `Con đường độc tôn`

Regression:

- `tests/test_bucchigiri_road_finding_hardening.py`
- regression head `5b2340febce1c06e6c524c29fc5db7aca1d33400`
- verifies idempotency, JP metadata, category-147 canonical resolution, and no canonical overmatch outside the intended category.

## Production acceptance evidence

- Validate run `33934908542`: success on regression head.
- Context Sync run `33934884620`: success; generated commit `febed41e97de70a3e0a2189f7e01117519fc191c` resolves the finding to `Keep Pushing Ahead` and reduced open canonical findings `113 -> 112`.
- Review-plan run `33934884589`: success; first regenerated live read-back removed the finding from the affected item.
- Exact regression-head Review-plan run `33934908414`: success; enforce/publish step completed successfully.
- Final live read-back of current `b0127` SHA `80ba6cdf3b62cd544508d99a8418e53e56919e87`: the `冠绝之路` item has `canonical_findings: []`; adjacent `钻石桥` / `cf-8758bee3b2929016` remains open, demonstrating that the hardening did not clear unrelated blockers.

Maintenance completion advances `completed_count` from `130` to `131` exactly once.
