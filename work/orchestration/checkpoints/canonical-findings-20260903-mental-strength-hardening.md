# Canonical finding checkpoint — `精神力量`

Finding: `cf-1fb0ec7c1c77dfb1`

## Evidence and decision

The live finding has three high-confidence evidence rows, all in `text_data_dict.json` category 147 (`3100801`, `3100802`, `3100803`). Each complete source string is `精神力量` and each current Vietnamese value is `Sức mạnh tinh thần`. The finding explicitly requires treating the complete phrase independently rather than normalizing the embedded `力量` substring to the Power stat or assuming an unrelated Skill identity from `精神力`.

Before hardening, `community_term_matches` on `精神力量` at category 147 matched `common.stat.power` through the substring alias `力量`, yielding a false Power conflict. The existing Power-context test already documents that `cf-1fb0ec7c1c77dfb1` must not be resolved merely by the generic Power context guard.

Use a narrow canonical community rule instead: exact source `精神力量`, `text_data_dict.json`, target `Sức mạnh tinh thần`. Also exclude `精神力量` from the generic Power term's substring matching. Exact source matching prevents longer prose from overmatching; source-path scope is required because the original canonical finding itself is source-path scoped and `refresh_canonical_resolutions()` only resolves a finding when the canonical rule covers the finding scope.

## Durable changes

- `scripts/harden_mental_strength_phrase_finding.py` added on `main` at commit `4699e007266f3cd1bd10f237898f0928d00baade`.
- First regression test commit: `b504067df42c244c86515e8a389455b66375bb47`.
- First production Context Sync run `33772265947` and Review-plan Sync run `33772265842` both succeeded.
- Production inspection found the first rule was too narrow for ledger reconciliation: it used `json_path_prefixes: [["147"]]`, while `cf-1fb0ec7c1c77dfb1` has no `json_path_prefixes`. `scripts/canonical_findings.py::_rule_covers_finding` therefore correctly refused to mark the broader finding resolved even though the item matcher was correct.
- Commit `70bda2a022217413c90290225399a002a38ff51a` removes that category prefix from the exact community rule, retains the text-data source-path guard, and preserves the Power exclusion.
- Commit `3f8c99536b7874b7468428df45b03265f81d0d29` adds a permanent regression that constructs the original source-path-scoped finding, runs `refresh_canonical_resolutions`, asserts `canonical_resolution == {layer: community, term_id: reviewed.context.mental_strength.text147, target_vi: Sức mạnh tinh thần}`, and asserts `active_findings()` becomes empty.

## Production acceptance

- Corrected-head validation run `33773044395` completed successfully.
- Corrected-head Context Sync run `33773044394` completed successfully.
- Corrected-head Review-plan Sync run `33773044371` completed successfully; its `sync` job finished all steps, including `Enforce canon and publish retrospective translation review plan`.
- Fresh live-`main` inspection after those workflows shows `cf-1fb0ec7c1c77dfb1.canonical_resolution == {"layer":"community","term_id":"reviewed.context.mental_strength.text147","target_vi":"Sức mạnh tinh thần"}`.
- Repository routing semantics define `active_findings` as only `open`/`deferred` rows without `canonical_resolution` and without an explicit ignore resolution. Therefore the live row, although its ledger `status` remains `open`, is excluded from active maintenance blockers.
- Fresh Review-plan Sync published active plan `tr-p3-67f8551f7780-55e83f8331e2-b5c0bcb3bd-ca33d092ad` on `main` at `2026-09-03T15:35:29.070726Z`.

Production acceptance is complete. Maintenance completion count may advance from 30 to 31 for `cf-1fb0ec7c1c77dfb1`.
