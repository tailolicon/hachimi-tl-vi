# Canonical finding research: 暁の御旗『葛城栄主』！

Finding: `cf-abda2b1124d162ff`

- zh-CN alias: `拂晓御旗『葛城荣主』！`
- Repository locator: `47:101041`
- Verified JP title: `暁の御旗『葛城栄主』！`
- Character: Katsuragi Ace
- Current Vietnamese title in live inheritance text: `Ngự kỳ bình minh 『Katsuragi Ace』!`
- Proposed canonical Vietnamese title: `Ngự Kỳ Bình Minh 『Katsuragi Ace』!`

## Evidence

Repository curation already verifies locator `47:101041` as JP `暁の御旗『葛城栄主』！` and explicitly warns that quoted `葛城栄主` is stylized character/kanji wordplay associated with Katsuragi Ace, so the Chinese proper-name spelling must not be literally calqued.

Fresh JP gameplay references independently identify Katsuragi Ace's unique Skill as exactly `暁の御旗『葛城栄主』！`; GameWith, Game8, and Umamusume Lab all agree on the title and effect. This closes the identity uncertainty that caused the earlier curation defer.

The existing Vietnamese title already makes the important proper-name treatment correctly: preserve `Katsuragi Ace` in Roman letters rather than translate `葛城栄主`/`葛城荣主`. `暁の御旗` is faithfully represented by `Ngự kỳ bình minh`; normalize only game-title capitalization to `Ngự Kỳ Bình Minh`.

## Scope decision

Canonicalize the complete Skill-title alias only, scoped to `text_data_dict.json`. The live finding appears inside category-172 inheritance descriptions, so matching must cover the full title inside longer strings without creating a generic rule for `拂晓`, `御旗`, or the character name independently.

Next: implement a hardener and regression mirroring the accepted Katsuragi Ace `決意一筆` pattern, then require Validate + production context sync + refreshed live review-plan acceptance before incrementing maintenance completion accounting.
