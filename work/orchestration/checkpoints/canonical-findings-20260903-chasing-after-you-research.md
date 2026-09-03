# Canonical findings maintenance research — Chasing After You

Claim: `canonical-findings-maintenance-gpt56sol-20260903T072035Z`

Finding `cf-04c407aa449b0c6e` (`逐君之形`) is active under `scripts/canonical_findings.py::active_findings(...)`: status is `open` and `canonical_resolution` is null.

## Existing repository evidence

- `work/curation/results/term-0087/gpt56sol-term0087-20260826T105314Z-d87f2b.json` maps zh-CN `逐君之形` to Skill ID `100251` and verifies the JP title `アナタヲ・オイカケテ`; the older curation decision deferred because the stylized katakana title lacked a stable localization decision.
- The finding is exact-scoped to `text_data_dict.json`, category `147`, and represents a Skill proper name.

## Fresh canonical evidence

- The current English release identifies Manhattan Cafe [Creeping Shadow]'s unique Skill `アナタヲ・オイカケテ` as **Chasing After You**.
- Game8's current English Manhattan Cafe guide and the current Umamusu Wiki game page independently expose the same English title for the same JP Skill identity.
- Therefore this is no longer a choice between speculative Vietnamese paraphrases: the stable source-backed English localization is available and should replace the semantic zh-CN-derived current rendering `Hình bóng đuổi theo người`.

Evidence checked 2026-09-03:
- https://game8.co/games/Umamusume-Pretty-Derby/archives/568614
- https://umamusu.wiki/Game%3AManhattan_Cafe_%28Creeping_Shadow%29

## Intended hardening

Add an idempotent `scripts/harden_*_finding.py` rule scoped exactly to `text_data_dict.json/147` for source alias `逐君之形`, preferred/accepted target `Chasing After You`, plus an explicit terminology-review lock to the same target. Add a regression proving `refresh_canonical_resolutions(...)` resolves `cf-04c407aa449b0c6e` in category 147 and does not resolve the same source outside that category.

The authoritative `.github/workflows/sync-translation-review-plan.yml` already runs all `scripts/harden_*_finding.py`, refreshes canonical findings, runs tests, rebuilds the review plan, and publishes generated state to `main` on matching push paths; do not hand-edit generated review-plan state.
