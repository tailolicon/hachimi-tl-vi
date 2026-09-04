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

Required production acceptance is still pending. Push-triggered Validate, Sync translation context, and Sync translation review plan were started from the implementation/test commits. Do not increment canonical-maintenance `completed_count` above 124 until the required runs succeed and the regenerated active review plan no longer contains `cf-f1601c34df2912ee`.
