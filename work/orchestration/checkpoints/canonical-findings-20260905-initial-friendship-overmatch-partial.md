# Canonical finding completion — Initial Friendship overmatch

Claim: `canonical-findings-maintenance-gpt56sol-20260905-0930-a11`
Finding: `cf-375c57aaf697bbff`
Source alias: `初始牵绊值`
Canonical target: `Initial Friendship`

## Resolution

The defect was matcher precedence/overmatch rather than a localized-translation defect. Category-155 compounds such as `友情加成&初始牵绊值提升` were incorrectly eligible for the generic `牵绊值 -> Friendship Gauge` matcher even though the repository already had the narrower `support.initial_friendship.effect155 -> Initial Friendship` concept.

Permanent hardening adds all established Initial Friendship compounds — `初始牵绊值`, `初始羁绊值`, `初始羁绊槽上升` — to `exclude_source_contains` on the generic Friendship Gauge locked/community rules while preserving true category-155 Friendship Gauge cases.

## Durable implementation

- `5d6129c685faf46226bfdb06791e98c160533d82` — permanent `scripts/harden_friendship_gauge_variant_finding.py` exclusion hardener.
- `dcbf1b7086cc9a56f04d68b5cf7550f071f7d06e` — regression coverage for all Initial Friendship compounds plus the positive bare Friendship Gauge case.

## Production acceptance evidence

- Validate run `33956175966` on exact head `dcbf1b7086cc9a56f04d68b5cf7550f071f7d06e`: **success**.
- Sync translation context run `33956175984` on the same exact head: **success**. The hardener reported already-current/idempotent generated state; regenerated Initial Friendship resolution changed successfully; final generated Context Sync was current/no-op.
- Sync translation review plan run `33956175973` on the same exact head: **success**.
  - full suite: **728 passed**;
  - hardener: `friendship_gauge_variant_hardening_changed=false`;
  - regenerated Initial Friendship resolver: `changed=true`;
  - plan builder: `changed=false`;
  - final workflow proof: `Canonical terminology and translation review plan/gate are already current.`
- Live `glossary/canonical_findings.json` is empty after production Sync, so `cf-375c57aaf697bbff` is no longer an active blocker.
- Permanent regression explicitly proves a true category-155 source such as `牵绊值达到100以上时` still matches the generic Friendship Gauge term, while each `友情加成&{Initial Friendship compound}提升` source does **not** match that generic term.
- Existing canonical `support.initial_friendship.effect155` remains the scoped owner for `初始牵绊值` / `初始羁绊值` / `初始羁绊槽上升`, preferred `Initial Friendship`.

Maintenance `completed_count` advances **135 -> 136**.
