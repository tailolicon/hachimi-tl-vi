# Canonical finding checkpoint — 脚色十分

Finding: `cf-642f6b7fcbe6af58`
Source: `脚色十分`
Key: `localize_dict.json` / `Race9467001`
Observed current target: `Dư lực dồi dào`
Target: `Fully Charged`

## Diagnosis

`脚色十分` is the named race mechanic/state whose English/Global terminology is `Fully Charged`. The canonical rule is deliberately key-scoped to `Race9467001` rather than generalized to unrelated prose.

The first production Context Sync correctly materialized the scoped community term, but the active review plan still carried `cf-642f6b7fcbe6af58`. Root cause: the historic worker finding was emitted as an exact `localize_dict.json` finding with `key_exact=[]` (source-wide declaration), while `scripts/canonical_findings.py::_rule_covers_finding` correctly refuses to claim that a narrower `key_exact=[Race9467001]` rule covers a source-wide finding. Thus the rule was safe but the observed finding could not close.

## Durable implementation

- `scripts/harden_fully_charged_finding.py` adds exact item-scoped community rule `race_state.fully_charged` and terminology decision `audit.finding.race-state-fully-charged`, restricted to `localize_dict.json` key `Race9467001`.
- Hardener commit: `d698be10b27bc242631c2d5b0a2969a5e6673bf5`.
- Initial hardener regression commit: `d575c97fb7d2de51e95903ffbc6664e4059ad014`.
- `scripts/resolve_scoped_canonical_overrides.py` now has a conservative evidence-bounded fallback: a narrower scoped community rule may close an overbroad worker finding only when an explicit review lock agrees with the rule target and every durable evidence row is inside the scoped rule. It does not broaden the canonical rule; any later evidence outside scope prevents this resolution on refresh. Resolver commit: `4c6e9c1cdde4f389ad7dd5bd5e20b59df6067afc`.
- `tests/test_scoped_canonical_override_resolution.py` adds positive coverage for the Fully Charged-shaped case and negatives for outside-scope evidence and missing evidence. Regression commit: `5975b27128b9b5e361d7314080a2487fc16bfa75`.

## Live read-back

- `glossary/ui_community_terms.json` on live main contains `race_state.fully_charged`, preferred/accepted `Fully Charged`, forbidden old Vietnamese calques, source `脚色十分`, exact key `Race9467001`.
- `glossary/terminology_review_queue.json` is empty on live main.
- Active plan `tr-p3-67f8551f7780-116121e718ef-b5c0bcb3bd-6fad1b114f` still contains the finding in batch `b0032`; this plan predates the resolver-repair production sync and is the evidence that motivated the resolver fix.

## Production gate state — verified 2026-09-05

The finding is **not accepted yet** and `completed_count` remains `129`.

Earlier generation:
- Validate run `33931287087`: `completed`, conclusion `success`.
- Sync translation context run `33931287046`: `completed`, conclusion `success`.
- Sync translation review plan run `33931287106`: still `in_progress` at the last read; it is not sufficient because the pre-repair plan still exposed the blocker.

Resolver-repair generation:
- Validate run `33931908274` for commit `5975b27128b9b5e361d7314080a2487fc16bfa75`: `in_progress` at latest read.
- Sync translation context run `33931908035`: `pending` at latest read.
- After those pass, verify live `glossary/canonical_findings.json` / worker-facing batch no longer treats `cf-642f6b7fcbe6af58` as active, then require a successor Translation Review Plan generated from the repaired context to succeed.

## Acceptance pending

Do **not** increment `129 -> 130` until repaired Validate + Context Sync succeed, live canonical read-back proves the finding resolved under evidence-bounded scope, and a successor review plan no longer exposes the blocker.
