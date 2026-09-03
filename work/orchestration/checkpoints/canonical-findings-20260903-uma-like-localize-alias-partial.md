# Canonical finding checkpoint — Uma Like! localize alias

Claim: `canonical-findings-maintenance-gpt56sol-20260903T110239Z`

Target finding: `cf-b56eee53b345a2bd` (`马赞` → **Uma Like!**).

## Live finding state

The generated live canonical-findings ledger shows this finding as `status: open`, `match_mode: contains`, scoped to `localize_dict.json`, with `canonical_resolution: null` and `review_resolution: null`. Evidence contains Home music UI keys `Home424022` and `Home424023`, currently rendered with generic Vietnamese `thích` even though the project already treats `马赞` / `ウマいね！` as the named feature **Uma Like!** inside League of Heroes.

## Hardening decision

Keep the existing `event.loh.uma_like` term unchanged with `key_prefixes: [Heroes]`. Add a separate bridge `common.uma_like.localize_alias` for `马赞`, preferred/accepted `Uma Like!`, scoped only to `localize_dict.json`, `match_mode: contains`.

Add explicit reviewed lock `audit.finding.uma-like-localize-alias` mapping `马赞` to `Uma Like!`.

## Regression coverage

`tests/test_uma_like_localize_alias_finding_hardening.py` verifies:

- idempotence;
- the existing Heroes-key term remains unchanged;
- the live `localize_dict.json` finding resolves through the bridge;
- reviewed target is `Uma Like!`;
- the same alias does not canonicalize through this bridge in `text_data_dict.json`.

## Acceptance state

Implementation and regression test are published. Full Validate/Sync acceptance and generated-ledger persistence are still required before this finding is counted complete.
