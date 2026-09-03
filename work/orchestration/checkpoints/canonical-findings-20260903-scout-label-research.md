# Canonical findings maintenance research — Character0146 / 奖池

Claim: `canonical-findings-maintenance-gpt56sol-20260903T074300Z`

Finding `cf-3caafd7a2224e00e` is an active exact system-label blocker for zh-CN `奖池` at `localize_dict.json` key `Character0146`. The current Vietnamese is `Kho quà`.

## Live-plan evidence

The current generated retrospective plan marks this finding `open`, exact-match, source-scoped to `localize_dict.json`, with concept `Prize pool UI label` and no review action/target. The same live item records key `Character0146` and current text `Kho quà`.

## Cross-locale identity evidence

A maintained Hachimi Global-English localization maps the exact same stable key:

- `Character0146`: `Scout`
- neighbors: `Character0134`: `Change Outfit`, `Character0147`: `Other`

Repository: `C-rrptd/Hachimi-TL-Global-EN`, `localized_data/localize_dict.json`.

This is stronger identity evidence than translating the zh-CN surface form `奖池` literally. It shows that the key is a scouting/recruitment UI label, while `奖池` is a lossy source-bridge rendering. The local project already uses Vietnamese `chiêu mộ` for scouting/recruitment race context in the `Aim! The Strongest Team` event, so the same user-facing concept has an established Vietnamese wording.

## Canonical decision

Use **`Chiêu mộ`**.

Rationale:
- Preserves the stable cross-locale identity `Scout` instead of the misleading zh-CN surface `奖池`.
- Matches existing project wording for scouting/recruitment context.
- `Kho quà` incorrectly describes a reward container and should be forbidden for this key.
- The rule should be exact and source-path/key scoped because generic `奖池` can legitimately mean a prize/reward pool elsewhere.

Hardening should therefore target only `localize_dict.json` / `Character0146`, add a source-bridge guarded canonical term with preferred `Chiêu mộ`, forbid `Kho quà`, and add regressions proving no longer string or other key/path inherits this correction.
