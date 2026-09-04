# Canonical finding checkpoint — generic Triple Crown profile label

Finding: `cf-f1601c34df2912ee`
Source alias: `三冠`
Observed live item: `text_data_dict.json` path `144/9046`, source `彰显王者之道的日本首位三冠赛马娘`.
Target: `Triple Crown`.

## Scope decision

The repository already has distinct canonical rules for compound crowns such as `经典三冠` → `Classic Triple Crown`, `春古马三冠` → `Senior Spring Triple Crown`, and `秋古马三冠` → `Senior Autumn Triple Crown`. Therefore the generic short alias must not become a corpus-wide contains rule.

The new rule is deliberately limited to `text_data_dict.json` with `json_path_prefixes: [["144"]]`, `match_mode: contains`, and item-scoped invalidation. This resolves the profile/title use of the achievement label while preserving the existing narrower compound-crown identities elsewhere.

## Durable implementation

- `scripts/harden_generic_triple_crown_finding.py` — commit `23cdd6cff48372d8b36c308d7a810396310a6e02`.
- `tests/test_generic_triple_crown_finding_hardening.py` — commit `f9b79fe54bdbcdcd2aa28757a337cafc1e569439`.
- Tests assert idempotence, target `Triple Crown`, category-144 scope, contains semantics, and negative coverage for the existing compound crown aliases/categories.

## Acceptance state

Production acceptance is complete:

- Validate run `33920170815` succeeded.
- Context sync materialized the resolution on `main` at commit `73880fcb020b08bd8f5d419a27b5e7c2f8ffc11c`. The finding has both `canonical_resolution` and `review_resolution` targeting `Triple Crown`; open canonical findings dropped from 118 to 117 and the terminology review queue removed the `三冠` canonical-finding row.
- Sync translation context run `33920170804` completed successfully.
- Sync translation review plan run `33920170820` completed successfully.
- Live review routing now points to plan `tr-p3-67f8551f7780-3f1cbee05cc5-b5c0bcb3bd-409da8fe1e`, generated at `2026-09-04T21:21:31.957019Z` with 4100 candidates.
- A live repository search for the conjunction of this plan id and `cf-f1601c34df2912ee` returns no result, confirming the regenerated active plan no longer carries the blocker.

Finding `cf-f1601c34df2912ee` is production-accepted. Canonical-maintenance `completed_count` may advance from 124 to 125.
