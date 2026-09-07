# Canonical findings maintenance checkpoint — Character0146 Scout accepted

- Claim: `canonical-findings-maintenance-sonnet-w1-20260907T011135Z`
- Worker: `sonnet-w1-20260907-0759-maintenance`
- Unit: exactly one canonical finding
- Finding: `cf-3caafd7a2224e00e` (`奖池`, exact `localize_dict.json` / `Character0146`)

## Verification performed on fresh live `main`

- Fetched/rebased onto live `main` (`a189284ce0` at claim time) before touching anything.
- `python3 scripts/harden_character0146_scout_finding.py` → `character0146_scout_hardening_changed=false`: the community term `common.scout.character0146` and review decision `audit.finding.character0146-scout` were already durably persisted on `main` by an earlier production Sync (commit `6f80f9d3f1`, `Sync translation context from pinned source`).
- Dispatched a fresh production `Sync translation context` run against live `main`: https://github.com/tailolicon/hachimi-tl-vi/actions/runs/34072385242 → `success`, `Test context pipeline` (full pytest) green, `Commit generated context if changed` step ran and produced **no new commit** — an unchanged no-op Sync, proving the resolution is stable under regeneration.
- Confirmed via `python3 scripts/canonical_findings.py --findings glossary/canonical_findings.json` (read-only, no `--refresh`) that live `glossary/canonical_findings.json` reports `active=137` and `cf-3caafd7a2224e00e` carries:
  - `canonical_resolution`: `{"layer": "locked", "term_id": "reviewed.source_bridge.ae9ecc8e8014", "target_vi": "Chiêu mộ"}`
  - `review_resolution`: `{"decision_id": "audit.finding.character0146-scout", "action": "lock", "target_vi": "Chiêu mộ"}`
  - i.e. the finding is excluded from `active_findings()` and is durably resolved.
- Fresh `Validate` CI on the exact commit that carries this claim's non-null progress evidence: https://github.com/tailolicon/hachimi-tl-vi/actions/runs/34072285784 → `success`.

## Caution noted for future maintainers

Running `scripts/canonical_findings.py --refresh` **in isolation** (without the rest of the `sync-context.yml` pipeline, in particular `scripts/resolve_context_guard_findings.py` and the other `resolve_regenerated_*_finding.py` / `resolve_running_style_narrative_finding.py` scripts that run after it) transiently nulls out every `context_guard`-layer `canonical_resolution` and reopens those findings, because `refresh_canonical_resolutions()` does not itself know about the `context_guard` layer. This was observed locally, reverted with `git checkout -- glossary/canonical_findings.json` before anything was committed, and replaced with dispatching the full `sync-context.yml` workflow instead. Do not run `canonical_findings.py --refresh` standalone against the real ledger; always run the full Sync pipeline (or the `sync-context.yml` workflow) so context-guard resolvers reapply afterward.

## Outcome

`cf-3caafd7a2224e00e` is accepted complete: canonical resolution durable on live `main`, proven stable across an unchanged no-op Sync, and Validate CI green. Releasing this claim now; this worker session stops after this one unit per its run instructions.
