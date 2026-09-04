# Canonical finding triage — Aoharu combustion family

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260904T0208Z`
Candidate: `cf-15165b78a43e8c28`

## Result

Do **not** harden this finding yet. It is distinct from the already accepted Aoharu Ignition family, and current repository evidence explicitly leaves the combustion-family titles unresolved.

## Evidence

- `scripts/harden_aoharu_ignition_finding.py` is for `アオハル点火` (Aoharu Ignition), not `アオハル燃焼`.
- `work/orchestration/checkpoints/canonical-findings-20260903-aoharu-regenerated-complete.md` records the accepted Ignition target `Thắp lửa thanh xuân` under `skill.aoharu_ignition.family`; reusing that target for combustion would conflate two different JP Skill families.
- Historical curation `work/curation/results/term-0061/claim-gpt56sol-7329809774194ea2.json` explicitly defers all five `燃烧青春` variants (`・体`, `・力`, `・智`, `・根`, `・速`) because no verified Japanese aliases or canonical mappings were available. That is stronger repository evidence than the current localized examples and forbids inventing a target from zh-CN alone.

## Decision

`cf-15165b78a43e8c28` remains evidence-blocked. No glossary rule, terminology lock, canonical-resolution mutation, or `completed_count` increment is valid from the currently available evidence.

Continue maintenance by selecting another active blocker that already has authoritative JP/Global evidence. Do not use the evidence-blocked `cf-735331afc1ace008` (`奔跑到何处`) or Drowa findings merely to keep the lane busy, and do not infer NPC readings from current Vietnamese output alone.
