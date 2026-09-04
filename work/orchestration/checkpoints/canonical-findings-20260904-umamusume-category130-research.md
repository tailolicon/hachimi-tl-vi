# Canonical findings maintenance research — 马娘 shorthand in category 130

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260904T0208Z`
Finding: `cf-93e25a8c1b655cdc`

Live review evidence identifies this as a `contains` finding for zh-CN `马娘` under `text_data_dict.json` category `130`, with suggested Vietnamese target `Mã Nương` and concept `generic horse-girl shorthand`.

A concrete live item is `自主训练赛马娘` at JSON path `["130", "394"]`. The same review item already matches authoritative community rule `common.world.umamusume`, whose `赛马娘` alias requires preferred/accepted `Mã Nương` and forbids `Uma Musume`. Therefore the semantic target is already authoritative; the unresolved finding is caused by the shorter contained token `马娘` not being covered at this category-specific scope.

Repository precedent is directly applicable: completed finding `cf-cd337bc7f688a0d4` used scoped community term `common.world.umamusume.profile_shorthand` to resolve the same short token `马娘` in category `144`, deliberately avoiding a global alias because the short token is collision-prone. Its Validate and Sync/rebuilt-review-plan acceptance path is documented in `canonical-findings-20260903-umamusume-shorthand-complete.md`.

Safe hardening direction:

- add a distinct category-130, `text_data_dict.json`-scoped supplemental community rule for contained `马娘` -> `Mã Nương`;
- do not broaden `common.world.umamusume.profile_shorthand` from category 144 and do not add `马娘` globally;
- preserve `common.world.umamusume` as the authoritative full-token species canonical;
- regression must prove category-130 text matches the supplemental short-token rule while the same short token outside categories explicitly scoped by supplemental rules does not gain a match;
- acceptance requires Validate success, production Sync translation-context success, and a downstream rebuilt live translation-review plan with no occurrence of `cf-93e25a8c1b655cdc`.

No localized-data text is patched by this maintenance step. Next action is to implement the scoped hardener/regression, then run the standard acceptance chain before counting the finding complete.
