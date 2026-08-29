# canonical-resources-gacha-shop W2 checkpoint — 2026-08-29T15:38Z

## Scope

Parallel domain work only. No canonical Resources/Gacha/Shop changes were published directly to `main`; serial integration remains owned by the primary maintenance lane.

## Durable branch state

- Branch: `canonical-resources-gacha-shop-hardening`
- Branch head after removing temporary validation workflow: `12c3c6b8b48849bdd48922335d7cd1ca018e5ccd`
- Permanent hardener: `scripts/harden_resources_gacha_shop_canon.py`
- Permanent regression coverage: `tests/test_resources_gacha_shop_hardening.py`
- Materialized canonical data: `glossary/source_bridge_terms.json`

## Canonical finding resolved in this checkpoint

The existing source-bridge records `currency.monies` (`金币` -> `Monies`) and `resource.cleat` (`蹄铁` -> `Cleat/Cleats`) were globally context-free. This contradicted the domain contract that ordinary gold/money/hoof prose must remain negative.

Both bridge rules are now scoped to `localize_dict.json`, retaining player-facing UI/resource enforcement while excluding story/text-data prose until narrower text-data contexts are individually proven.

Representative live review evidence before the fix included Shop137003/Shop137006 using `金币` in exchange UI and currently translated as `Coin`; the source bridge correctly identifies those as `Monies` mismatches.

## Validation evidence

A temporary GitHub Actions validation bridge was used because the local/container backend could not resolve github.com. The workflow order was: materialize hardener -> focused pytest -> second-run idempotence comparison -> persist materialized glossary. It successfully produced bot commit `d64ffe462c8addb75424f31c0cff336916fa6256` (`Materialize scoped resource bridge canon`), which is only reachable after the focused tests and idempotence step succeeded. The temporary workflow was then removed in branch commit `12c3c6b8b48849bdd48922335d7cd1ca018e5ccd`.

Focused regression coverage verifies:

- `金币` matches Monies in localize/shop UI;
- the same semantic token does not match story `text_data_dict.json` prose;
- `蹄铁` matches Cleat/Cleats in localize/UI;
- ordinary hoof prose in text data does not match;
- the hardener is idempotent.

## Additional evidence gathered

Current corpus already has locked `currency.jewel` -> `Jewel`. Shop0091/Shop0092 contain paid-Jewel wording (`付费宝石` / `有偿宝石`) and are currently rendered as `Jewel trả phí`; current global terminology references consistently use `paid Jewels` / `free jewels`. This remains a candidate for the next domain unit, but no paid/free Jewel rule was added in this checkpoint because exact UI wording/scope still needs to be locked deliberately.

## Next safe work

Continue this same domain rather than redoing the Monies/Cleat inventory. Audit and harden, with narrow evidence-based scope:

1. paid/free Jewel distinctions;
2. exchange points / banner pity terminology;
3. stable shop currencies (Friend Points, Club Points, Cleats, Clovers) only where source identity is proven;
4. acquisition/spend/exchange and insufficient-resource labels where a fixed player-facing label is warranted;
5. keep one-off event currencies out of canonical locks.

Domain is **not** ready for integration yet.
