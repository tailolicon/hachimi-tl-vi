# Canonical finding completion — 马娘 profile shorthand

Claim: `canonical-findings-maintenance-auto11-20260903T082829Z`
Finding: `cf-cd337bc7f688a0d4`

Completed systemic hardening:

- added scoped community term `common.world.umamusume.profile_shorthand` for contained zh-CN `马娘` -> `Mã Nương`;
- scope is limited to `text_data_dict.json` category `144`, where the live evidence is character-profile prose using generic `赛马娘` species references;
- retained `common.world.umamusume` as the authoritative general full-token canonical rather than globalizing the collision-prone short token `马娘`;
- regression proves the shorthand rule applies in category 144 and does not apply to the same token outside that category.

Validation evidence:

- Validate run `33735019994` completed successfully for the hardener/regression commit set.
- Sync translation context run `33735020023` completed successfully and published generated context commit `0e5c954ac9236dcfac5aedbcbac9336fffecaa9a`.
- Live `glossary/ui_community_terms.json` contains `common.world.umamusume.profile_shorthand` with category-144 scope.
- The rebuilt live review plan `tr-p3-67f8551f7780-1225cdedaf6a-b5c0bcb3bd-db8b9e96b9`, generated at `2026-09-03T08:48:21.373207Z`, is downstream of that generated context and contains no occurrence of `cf-cd337bc7f688a0d4`.

This finding is therefore counted complete. Continue canonical maintenance from the next live active finding.