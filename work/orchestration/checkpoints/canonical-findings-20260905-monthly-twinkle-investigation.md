# Canonical findings maintenance checkpoint — Monthly Twinkle accepted

The recurring in-world publication `月刊Twinkle` is represented by two proper-name findings:
- `cf-3f76c45986ceefe6`, scoped to `localize_dict.json` key `Champions187003`.
- `cf-fc0ace892355f4ce`, scoped to `localize_dict.json` key `Champions0507`.

Both findings' canonical source is the base alias `月刊Twinkle` with `match_mode=contains`; surrounding `号外` / `增刊` text is edition wording, not part of the canonical publication identity.

Evidence and decision:
- Cygames' official JP portal identifies Otonashi Etsuko as a reporter for the magazine `月刊トゥインクル`, establishing it as a recurring proper publication title.
- The pinned zh-CN UI preserves the title element `Twinkle` as `月刊Twinkle`.
- Established English-language Umamusume references render the publication as `Monthly Twinkle`.
- Canonical project target: `Monthly Twinkle`. This is a project/community canonical rendering, not a claim of an official Global localization.
- Matcher is item-scoped to `localize_dict.json` keys `Champions0507` and `Champions187003`; edition suffix wording remains ordinary containing-item text.

Durable implementation on `main`:
- `scripts/harden_monthly_twinkle_finding.py` commit `94ecd3f92f8d16e51642d772052b22ee177022b1`.
- Initial regression test commit `9f6f5cad5c84c9856514a548afa43195a110c2b4`.
- Regression expectation correction commit `0556f6276a5eac02b48f319f7ec9c629168576f3`; it preserves key scoping for the community matcher while matching the resolver's source-identity semantics for the review lock.
- Rule id `publication.monthly_twinkle`; review decision id `audit.finding.publication-monthly-twinkle`.

Production acceptance:
- Validate run `33904649681`: success.
- Sync translation context run `33904649747`: success.
- Generated context commit `7d1f9eb7610e26cf68f49f0134c662b9173bf4` resolves both findings to `Monthly Twinkle` with non-null `canonical_resolution` and `review_resolution`, adds the reviewed locked registry entry and community rule, and reduces `open_canonical_findings` from 124 to 122.
- Post-context Sync translation review plan run `33904649733`, attempt 2: success; completed at `2026-09-04T18:58:48Z` after consuming the regenerated context.
- Live code search confirms the permanent hardener and regression test remain on current `main`; historical review batches may still contain the old finding IDs as evidence, but they are no longer active blockers under `active_findings` semantics because the production generated context carries canonical/review resolution.

Acceptance status: complete for both findings. Maintenance completed count may advance by 2 (118 -> 120).
