# canonical-resources-gacha-shop W2 checkpoint — 2026-08-29T15:41Z

## Scope

Parallel Resources/Gacha/Shop domain work only. No canonical integration or production Sync was performed on `main`.

## Durable branch state

- Branch: `canonical-resources-gacha-shop-hardening`
- Branch head: `2f35efb6e8bea59b57a90187b1f181cf6e179a0a`
- Permanent hardener: `scripts/harden_resources_gacha_shop_canon.py`
- Permanent regression coverage: `tests/test_resources_gacha_shop_hardening.py`

## New canonical unit

The shop corpus contains fixed paid-Jewel wording, including `Shop626028` source `付费宝石详情`, currently translated as `Chi tiết Jewel trả phí`. Existing `currency.jewel` only locks the base `宝石 -> Jewel` identity, so paid/free qualification was not represented as a distinct canonical concept.

The hardener now upserts two UI-scoped bridge records:

- `currency.jewel.paid`: JA `有償ジュエル`, zh-CN `付费宝石` / `有偿宝石`, preferred `paid Jewels`, accepts existing Vietnamese `Jewel trả phí`;
- `currency.jewel.free`: JA `無償ジュエル`, zh-CN `免费宝石` / `无偿宝石`, preferred `free Jewels`, accepts `Jewel miễn phí`.

Both are limited to `localize_dict.json` so ordinary story prose involving free/paid gifts or gemstone language does not become a Jewel canonical match. Opposite paid/free labels are explicitly forbidden for each rule.

## Regression coverage

Added a focused regression proving:

- paid-Jewel shop UI matches only `currency.jewel.paid` and recognizes `Jewel trả phí`;
- free-Jewel shop UI matches only `currency.jewel.free` and recognizes `Jewel miễn phí`;
- generic text-data prose does not match either rule;
- the hardener remains idempotent by construction alongside the existing test.

The code/tests are durably committed but this unit has not yet been executed through a fresh CI validation bridge in this run. Do not treat it as green until focused tests/materialization are run.

## Next safe work

Run focused validation/materialization for the new Jewel unit, then continue Exchange Points/pity and stable shop-currency identity audit. Domain remains `domain_work` and is not ready for integration.
