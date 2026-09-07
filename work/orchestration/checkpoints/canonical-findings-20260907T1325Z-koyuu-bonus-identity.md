# Canonical finding checkpoint — 固有加成 identity research

Finding: `cf-5cc239af1c9d7710` (`固有加成`)

## Fresh repository evidence

- The live retrospective review batches still expose this finding as `status: open`, with `match_mode: contains`.
- The exact player-facing localize label exists at `localize_dict.json / Character0050`; the current Vietnamese corpus text is `Bonus riêng`.
- A longer companion label exists at `localize_dict.json / Character0196` with source `固有加成详情`; its current Vietnamese corpus text is `Chi tiết bonus riêng`.
- The repository also contains unrelated support-card category-150 *unique effect names*. Those are individual proper/display names and must not be conflated with this generic UI label.

## Fresh external identity verification

- Current JP support-card references label the generic support-card section `固有ボーナス`.
- Current English/Global-facing GameTora support-card pages render that same generic section as `Unique Effect` (for example Matikanefukukitaru SSR and Nice Nature SR).
- Therefore zh-CN `固有加成` is a semantic bridge for the generic Support-card **Unique Effect** section label, not a generic `bonus` noun.

## Vietnamese canonical recommendation

Use `Hiệu ứng riêng` for the generic player-facing label. This is already an observed Vietnamese rendering elsewhere in the repository and is semantically aligned with `Unique Effect`; it is clearer and less mixed-language than historical `Bonus riêng`.

The paired detail label should naturally become `Chi tiết hiệu ứng riêng` when review invalidation reaches it. Do not blindly patch `localized_data/**`.

## Scope / implementation guard

The finding alias is reusable inside `固有加成详情`, so an `exact` rule would violate the worker policy for this finding. Any canonical hardener should use `contains` only within the relevant localize UI keys/paths (at minimum Character0050 and Character0196), with negative regression coverage proving it does not affect category-150 support unique-effect *names* or unrelated prose.

## Next action

Implement an idempotent canonical hardener + regression tests for `固有加成 -> Hiệu ứng riêng`, then run Validate + production Context Sync + second unchanged Sync before counting the finding complete.
