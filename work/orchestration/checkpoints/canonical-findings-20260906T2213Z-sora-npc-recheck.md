# Canonical findings maintenance checkpoint — 空(NPC) recheck

- Claim: `canonical-findings-maintenance-chatgpt-sol-20260906T221248Z`
- Finding: `cf-a4a841b7c7df4aeb`
- Source: `空(NPC)`
- Unit outcome: research checkpoint; no reusable canonical reading promoted

## Live repository verification

- Current `scripts/canonical_findings.py::active_findings` blocks `open`/`deferred` rows that have no `canonical_resolution` and are not explicitly ignored.
- Current `main` contains `scripts/harden_sora_npc_finding.py`, whose narrow decision is explicitly item-scoped to category-152 paths `24`, `58`, `92`, `126`, `160`, and `194`.
- That hardener intentionally avoids promoting `Sora` as reusable canonical terminology because the kanji `空` admits multiple Japanese readings and repository evidence does not authoritatively establish this NPC's reading.
- A fresh default-branch code search for decision id `audit.finding.npc-sora-unverified-reading-ignore` finds the hardener implementation but no indexed accepted decision in `glossary/terminology_reviews.json`; therefore this worker did not assume the hardener had already reached production state.

## Fresh source recheck

- Fresh searches of the current official JP portal and current official Global-facing web surface did not produce an authoritative player-facing identity/readout for this category-152 NPC that establishes `空` as `Sora`.
- The official JP character directory provides canonical identities for named Uma Musume characters, but no evidence located in this recheck establishes this generic NPC's reading.

## Decision

Do **not** lock `空 -> Sora` as reusable canonical terminology. Preserve the narrow, item-scoped strategy already encoded by `scripts/harden_sora_npc_finding.py`.

No canonical/context mutation was applied in this unit because the Shiro execution backend terminated before repository scripts/validators could be run, and GitHub direct fallback cannot execute the required refresh/test pipeline. Applying the hardener without running its refresh/resolver/validation sequence would make durable generated state unverifiable.

## Continuation

A worker with a functioning execution backend may resume this specific finding by running the existing `scripts/harden_sora_npc_finding.py`, then the repository's canonical refresh/resolver and validation sequence, and only then confirming that `cf-a4a841b7c7df4aeb` leaves the active blocker set. Do not promote `Sora` beyond the six item-scoped NPC occurrences unless authoritative reading evidence appears.
