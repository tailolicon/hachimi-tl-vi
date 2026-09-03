# Canonical finding validation: legacy Uma Musume Stakes scope migration

Claim: `canonical-findings-maintenance-gpt56sol-20260903T183533Z`

Finding: `cf-0dae34861911a969`
Final implementation head under validation: `19b9eb1174bf15a408dbf87fef320df9a5b21795`

## Gate discovery

The final head triggered exactly the three required production workflows:

- Validate: `33790501576`
- Sync translation context: `33790501299`
- Sync translation review plan: `33790501552`

## Verified state

- Validate `33790501576`: **completed / success** on head `19b9eb1174bf15a408dbf87fef320df9a5b21795`.
- Sync translation context `33790501299`: **completed / success** on the same head.
- Sync translation review plan `33790501552`: **completed / success** on the same head.
- The newly generated live review plan is `tr-p3-67f8551f7780-feb351e8dc2e-b5c0bcb3bd-db93968fb0`, generated at `2026-09-03T18:28:50.055027Z`.
- Repository search for `cf-0dae34861911a969` combined with that live plan id returns no match, while historical checkpoints/results still contain the old finding as expected. This confirms the refreshed plan no longer embeds the finding as an active blocker.

## Acceptance

Accepted. The legacy-scope regression is validated end-to-end and the refreshed production review context no longer blocks entries on `cf-0dae34861911a969`. Maintenance completed count may advance from 39 to 40.
