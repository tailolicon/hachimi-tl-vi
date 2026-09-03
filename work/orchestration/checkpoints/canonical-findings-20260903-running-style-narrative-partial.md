# Canonical finding checkpoint — narrative 跑法 context

Claim lineage: `canonical-findings-maintenance-gpt56sol-20260903T110239Z` → `canonical-findings-maintenance-gpt56sol-20260903T1126Z`

Target finding: `cf-b17becec58edec45` (`跑法`).

## Live finding state

The live canonical findings ledger reports this finding as `status: open`, `match_mode: contains`, scoped to `text_data_dict.json`, with no canonical resolution. All three evidence rows are character-introduction/narrative strings under text-data category `163` where `跑法` means a natural-language manner/style of running, not the player-facing running-style category label.

The three proven narrative contexts are Maruzensky `163/1004`, Gold City `163/1040`, and Biko Pegasus `163/1054`; current reviewed targets naturally use `cách chạy` / `cách tôi chạy`.

## Implemented hardening

- `scripts/harden_running_style_narrative_finding.py` preserves canonical player-facing `common.style` / `跑法 → Style` while adding exact-source exclusions for the three durable narrative strings.
- `scripts/resolve_running_style_narrative_finding.py` resolves only `cf-b17becec58edec45`, only when every evidence row remains under `text_data_dict.json` category `163`, and only after `common.style` no longer matches any evidence row. Resolution is `layer: context_guard`, `term_id: common.style`, `target_vi: Style`; it does not lock narrative prose to a replacement phrase.
- `tests/test_running_style_narrative_finding_hardening.py` covers hardener idempotence, preservation of the ordinary player-facing `跑法 → Style` match, exclusion of all three narrative strings, resolver closure, and resolver idempotence.
- `.github/workflows/sync-context.yml` now runs the dedicated resolver after canonical refresh + generic context-guard resolution and watches the resolver path.

Implementation commits: `703283d378196601b9eeae4d5c0fbb04cadfa104`, `481d0aff66063cc2db56deae59eaac46f2b4eb44`, `7b49e5605e5b66c2bd95d3b1c54e2eabd1efe4cc`, `876b21062d109dc46c4e7c5b93263d726cd5e0f1`.

## Acceptance state

Implementation is published. Validate run `33750355712` and Sync translation context run `33750355770` were started from workflow commit `876b21062d109dc46c4e7c5b93263d726cd5e0f1`; they must complete successfully and the generated canonical ledger must persist the context-guard resolution before this finding is counted complete.
