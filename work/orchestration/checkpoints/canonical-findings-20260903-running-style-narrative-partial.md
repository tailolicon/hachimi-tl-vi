# Canonical finding checkpoint — narrative 跑法 context

Claim lineage: `canonical-findings-maintenance-gpt56sol-20260903T110239Z` → `canonical-findings-maintenance-gpt56sol-20260903T1126Z`

Target finding: `cf-b17becec58edec45` (`跑法`).

## Resolution

The generic player-facing rule remains `跑法 → Style`, but the three proven character-introduction prose contexts under `text_data_dict.json` category `163` are excluded from that matcher so natural Vietnamese `cách chạy` wording is not forced into the UI label.

Implemented by:
- `scripts/harden_running_style_narrative_finding.py` — exact-source exclusions for Maruzensky `163/1004`, Gold City `163/1040`, and Biko Pegasus `163/1054`, while preserving ordinary `跑法 → Style` matching;
- `scripts/resolve_running_style_narrative_finding.py` — resolves only this finding, only for category-163 evidence, and only after `common.style` no longer overmatches any evidence row;
- `tests/test_running_style_narrative_finding_hardening.py` — idempotence, positive UI-match preservation, narrative exclusions, and resolver closure coverage;
- `.github/workflows/sync-context.yml` — runs the dedicated resolver after canonical refresh/context guards.

Implementation commits: `703283d378196601b9eeae4d5c0fbb04cadfa104`, `481d0aff66063cc2db56deae59eaac46f2b4eb44`, `7b49e5605e5b66c2bd95d3b1c54e2eabd1efe4cc`, `876b21062d109dc46c4e7c5b93263d726cd5e0f1`.

## Acceptance state

Accepted complete.

- Validate run `33750355712` completed successfully for workflow commit `876b21062d109dc46c4e7c5b93263d726cd5e0f1`.
- Sync translation context run `33750355770` completed successfully, including the new hardener, dedicated resolver, terminology queue rebuild, full test suite, and generated-context publication.
- Generated commit `42f013906461cd351816b0fa220a732ec8dc8b80` persists `canonical_resolution = {layer: context_guard, term_id: common.style, target_vi: Style}` for `cf-b17becec58edec45`.
- The same generated commit removes `跑法` from the canonical-finding review queue and reduces `open_canonical_findings` from 219 to 218.

The narrative `跑法` overmatch is therefore canonically hardened without weakening the player-facing `Style` term.
