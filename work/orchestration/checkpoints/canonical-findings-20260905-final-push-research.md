# Canonical finding research — Final Push

Claim: `canonical-findings-maintenance-gpt56sol-20260906-0057-a13`

Finding: `cf-062d5c0208457997`

## Live finding

- exact zh-CN source: `一逃到底`
- scope: `text_data_dict.json`, category `147`
- evidence locator: `147/2005501`
- current Vietnamese: `Dẫn đầu tới cùng`
- current status: active (`open`, no `canonical_resolution`; existing review action is `defer`)
- repository curation already pins the underlying Skill identity to ID `200552`, Japanese `押し切り準備`, and explicitly flags `一逃到底` as a lossy/non-title-equivalent zh-CN bridge.

## Identity verification

Current Global-reference evidence maps Japanese Skill `押し切り準備` / ID `200552` to the English player-facing title **Final Push** and its gold upgrade `逃亡者` to **Unrestrained**. Independent current reference material lists the same `Final Push (押し切り準備) / Unrestrained (逃亡者)` pair for Front Runner skills.

Sources checked:
- Uma Musume Pretty Derby Wiki, `Game:Skills/200552` — `Final Push`, Japanese `押し切り準備`, upgrade `Unrestrained`.
- Uma Musume Global Reference Document — `Final Push (押し切り準備) / Unrestrained (逃亡者)`.
- Repository pinned curation: `glossary/source_bridge_risks.generated.json`, record `curation.bridge.3361eb0505995e36`.

## Resolution direction

Use canonical target `Final Push`, not the literal zh-CN-derived `Dẫn đầu tới cùng`.

Implement as an exact, item-scoped Skill rule for `一逃到底` under `text_data_dict.json` category `147`; preserve the JP identity `押し切り準備` in the review decision and reject the historical lossy target. Add regression coverage proving the rule resolves the finding only in the intended Skill scope and does not overmatch other paths/categories.

This checkpoint is research/provenance only. Do not increment `completed_count` until the hardener is integrated, validation passes, production context/review-plan sync publishes the canonical resolution, and live review evidence no longer carries the finding.
