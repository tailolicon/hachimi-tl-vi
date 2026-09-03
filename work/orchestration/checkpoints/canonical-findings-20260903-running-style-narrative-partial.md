# Canonical finding checkpoint — narrative 跑法 context

Claim: `canonical-findings-maintenance-gpt56sol-20260903T110239Z`

Target finding: `cf-b17becec58edec45` (`跑法`).

## Live finding state

The live canonical findings ledger reports this finding as `status: open`, `match_mode: contains`, scoped to `text_data_dict.json`, with no canonical resolution. All three evidence rows are character-introduction/narrative strings under text-data category `163` where `跑法` means a natural-language manner/style of running, not the player-facing running-style category label.

Current reviewed targets already render these occurrences naturally as forms such as `cách chạy` / `cách tôi chạy`.

## Existing canonical rule causing the block

`glossary/ui_community_terms.json` has canonical term `common.style` with zh-CN source alias `跑法`, preferred target `Style`, and no narrative exclusion. The alias is correct for player-facing running-style UI, but its unrestricted contains matching overmatches the category-163 narrative evidence.

## Proposed hardening

Do **not** change the canonical player-facing `Style` vocabulary. Instead, neutralize the generic `common.style` matcher only for the proven narrative evidence/context. A safe implementation should either:

1. add narrowly scoped exclusions for the three durable narrative source strings to `common.style`, then resolve `cf-b17becec58edec45` as a context guard only after every evidence row no longer matches `common.style`; or
2. introduce an equivalently narrow category-163 context guard if the matcher supports json-path-scoped negative rules.

The first option matches the existing `common.stat.power` context-hardening pattern and is preferred unless a narrower json-path negative mechanism already exists.

## Acceptance requirements

- preserve `跑法 → Style` for actual running-style UI/category labels;
- all three current category-163 narrative evidence rows must stop matching `common.style`;
- `cf-b17becec58edec45` may resolve only through a context guard after the matcher is neutralized, never by globally locking `跑法` to a Vietnamese narrative phrase;
- hardener must be idempotent;
- full repository validation and production Sync translation context must pass before counting the finding complete.
