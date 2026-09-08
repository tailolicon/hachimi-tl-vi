# Canonical finding complete — U缘奇遇 / Encounter with U

Claim: `canonical-findings-maintenance-auto11-20260908T000940Z`
Finding: `cf-7082ecae529c1a53`

## Production result

The zh-CN inheritance alias `U缘奇遇` is now canonically locked to **Encounter with U**, the repository-verified title for Skill 111051. The lock is deliberately item-scoped to `text_data_dict.json` category `172` with `match_mode: contains`; it does not globalize the alias into unrelated prose.

## Durable source

- hardener: `68a7956e4e14a3d6d07410dc2fdc6e9b77f41401` (`scripts/harden_encounter_with_u_finding.py`);
- regression: `6b950c310f08a61b8f6e32ed92ddd31057918680` (`tests/test_encounter_with_u_finding_hardening.py`).

The hardener records `Encounter with U` as the accepted/preferred Skill title, rejects the semantic calque `Kỳ ngộ nhờ duyên U`, and writes the explicit reviewed lock `audit.finding.skill-encounter-with-u` with the same category-172 scope.

## Acceptance

- Validate run `34172688828` succeeded on the regression commit.
- Applying production Context Sync `34172676784` / job `101895876440` succeeded, passed **846 tests**, ran the new hardener, and persisted generated canonical context on `main`.
- Unchanged Context Sync `34172688836` / job `101896397317` succeeded, passed **848 tests**, reported `encounter_with_u_changed=false`, and ended with exactly `Context is already current.`.
- Retrospective review-plan run `34172676785` / job `101895876488` detected concurrent canonical-input movement, rebuilt from fresh `main`, passed **848 tests**, then successfully published plan `tr-p3-67f8551f7780-10f25c6097a3-b5c0bcb3bd-508e626e29`.
- Live `work/parallel_state.json` points to that exact plan with 2,937 unresolved entries / 147 batches.
- Live canonical ledger carries the reviewed `audit.finding.skill-encounter-with-u` lock targeting `Encounter with U`; the accepted plan was generated after that lock and hardener were reapplied from fresh `main`.

This finding satisfies the canonical-maintenance acceptance chain and may increment maintenance `completed_count` from **203 to 204**.
