# Canonical finding research checkpoint — Ominous Portent

Claim: `canonical-findings-maintenance-gpt56sol-automation-20260906T2305Z`

Finding: `cf-f9d07187211a1675`

## Recovered identity

The blocked retrospective item is UID `zhcn:ddac2a6be25e2e39494d4fbc`, source `怪云行天`, in `text_data_dict.json` category `142`, item id `21`. Category 142 is the Condition-name table. The historical Vietnamese value `Mây Lạ Lướt Trời` is only a semantic rendering and is not identity authority.

Fresh cross-source research now recovers the Japanese Condition identity as `怪しい雲行き`:

- UmaAssistant's Uma condition vocabulary includes `怪しい雲行き` among actual training Conditions.
- Current Uma Musume reference data identifies Copano Rickey's special debuff Condition as JP `怪しい雲行き` and English `Ominous Portent`, with the disrupted-qi description matching the character's feng-shui mechanic.
- An independent current status-effect dataset likewise records `nameJP: 怪しい雲行き` and `name: Ominous Portent`.
- An older community translation uses `Dubious Signs`; because stronger/current cross-source evidence agrees on `Ominous Portent`, use `Ominous Portent` as the player-facing canonical target.

## Scope decision

Lock `怪云行天` to `Ominous Portent` only in `text_data_dict.json` category `142`, exact match. Do not promote the zh-CN token as a global identity alias: the same Chinese wording can occur as ordinary lyrical/prose language, so a broad contains/source-path rule would be unsafe.

## Implementation direction

Follow the existing category-142 Condition hardener pattern (`Hero's Radiance`, `Positive Thinking`, etc.): add a scoped community condition term plus an explicit terminology-review lock and a regression proving both positive resolution in category 142 and negative non-resolution outside that category. Then run the repository validation/context-sync acceptance path before incrementing maintenance completion.
