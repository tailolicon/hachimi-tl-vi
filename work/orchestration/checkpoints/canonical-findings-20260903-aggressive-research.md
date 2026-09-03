# Canonical finding research — Aggressive

Candidate finding: `cf-5f92ce6e499363dd`

- zh-CN source: `以攻为守`.
- historical Vietnamese target in live review: `Lấy công làm thủ`.
- live review evidence is the exact Skill-title rows `147/2032201`, `147/2032202`, and `147/2032203`.
- pinned curation evidence identifies Skill `203222` as Japanese `アグレッシブ` and explicitly marks zh-CN `以攻为守` as an interpretive idiom rather than a title-equivalent identity.
- current Japanese gameplay references independently list normal Skill `203222` as `アグレッシブ`, including the same mid-race stamina-consumption / speed-up effect and its upgrade `影従打破`.

## Research conclusion

The identity-bearing JP title is the direct katakana rendering of English `Aggressive`. Preserve the title as `Aggressive` rather than canonizing the zh-CN idiom or inventing a Vietnamese semantic title from that idiom.

This is analogous to other identity-bearing English/katakana Skill titles already preserved by the repository. Use an exact `text_data_dict.json` rule for source alias `以攻为守`; do not generalize component words or effect prose. The existing curation bridge risk should be superseded only for this exact title once the JP-backed canonical lock exists.

External corroboration checked during this maintenance run: current Game8, GameWith, Kamigame, and U-tools Skill pages all identify the Skill as `アグレッシブ`; U-tools maps it directly to Skill `203222`.

## Next step

Install a permanent idempotent finding hardener plus positive/negative regression coverage, then require successful Validate, production Sync translation context, and Sync translation review plan before advancing maintenance completion.
