# Canonical maintenance checkpoint — Dirt surface complete

Claim: `canonical-findings-maintenance-chatgpt-20260831T1946Z`

Finding `cf-62610c0599d7a197` is resolved on live `main`.

- source: `沙土` in `text_data_dict.json` category `131`, key `71`
- semantic context: player-facing race surface Dirt
- canonical target: `Dirt`
- canonical community term: `common.surface.dirt`
- hardener: `scripts/harden_dirt_surface_finding.py`
- hardener commit: `f9271c55b4bf64c7d2b87f92927a031373aeb001`
- regression: `tests/test_dirt_surface_finding_hardening.py`
- regression commit: `6a1a8fd26fc446e6876c2804f8468bd202f445dd`
- Validate run for hardener `33433152491`: success
- Sync translation context run `33433152489`: success
- Validate run for regression `33433166561`: success
- generated context commit: `ee240e94f32da7185a8e9ce35815081b12b577b4`
- live canonical resolution: `layer=community`, `term_id=common.surface.dirt`, `target_vi=Dirt`

The hardener adds the zh-CN alias `沙土` to the already-established Dirt surface term instead of introducing a duplicate concept. This prevents literal Vietnamese forms such as `sân cát` from passing canonical review where the game-facing surface label is Dirt.

Maintenance completed count advances from 107 to 108. Continue immediately with the next live unresolved canonical finding.
