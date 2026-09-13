# Canonical finding maintenance — Queen Elizabeth II Cup duplicate scope

Finding: `cf-02cb6811d87107a6` (`伊丽莎白女王杯`).

## Live evidence

- Live `active_findings` semantics currently treat 92 findings as active after the prior Rank Medal item-scoped ignore.
- This finding is `match_mode: exact`, `source_paths: [text_data_dict.json]`, but has an empty `json_path_prefixes` scope.
- Both retained evidence rows are in category `111` (`111/194` and `111/26`) and already render `Queen Elizabeth II Cup`.
- Live `term_registry.json` already contains locked term `race.queen_elizabeth_ii_cup`, zh-CN alias `伊丽莎白女王杯`, target `Queen Elizabeth II Cup`, source path `text_data_dict.json`, with allowed prefixes `32`, `33`, `111`.
- A separate finding `cf-b095e50c9330bb30` for the same exact source and category `111` is already canonically resolved to that term/target.
- A full `canonical_findings.py --refresh` experiment on a detached live-main snapshot was **not persisted** because it changed broad derived review state and raised the active count; maintenance must stay item/finding scoped.

## Safe resolution

Repair only `cf-02cb6811d87107a6` from retained evidence by setting `json_path_prefixes` to `[["111"]]`, then set its canonical resolution to locked term `race.queen_elizabeth_ii_cup` / `Queen Elizabeth II Cup` only after verifying the locked registry term still covers source/path/prefix/target. Preserve the existing review decision; do not modify the shorter `女王杯` rule in this unit.
