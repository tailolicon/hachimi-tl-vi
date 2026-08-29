# Training / Support canonical hardening checkpoint — 2026-08-29T12:25Z

Task: `canonical-training-support`
Stage: `domain_work`
Branch: `canonical-training-support-hardening`

## Completed and validated in this session

Continued from the prior released checkpoint; did not restart the domain.

Materialized scoped canonical hardening for:

- `Friendship Training` — replaces historical `Huấn luyện Hữu nghị` / `huấn luyện tình bạn` calques while matching only the full mechanic compound.
- `Support Pt` — `localize_dict.json` `Common0160` (`支援点数`) with exact one-item scope; prose variants `Support Pts` / `Support Points` are accepted by the community rule.
- `Energy` — Career training gauge and gain/loss messages at `SingleMode0006`, `SingleMode0074`, `SingleMode0075`; exact localize-path scope prevents ordinary physical-strength prose from matching.
- `Friendship Gauge` — Support Effect descriptions in `text_data_dict.json` category `155` using `羁绊值`; the historical globally locked bare `progress.bond -> Gắn kết` mapping is disabled so generic friendship/bond prose is no longer forced to the mechanic label.

Canonical materialization commit:

- `f58562d4c3a822bc39be57750027773065d5da33` — `Materialize Training Support canonical hardening`

Validation evidence from GitHub Actions bridge after fixing the locked-path guard:

- focused regression: `9 passed in 0.06s`
- full pytest: `176 passed in 0.94s`
- `tlvi --db /tmp/tlvi.db validate`: `ok: true`, no errors, no warnings
- `tlvi --db /tmp/tlvi.db index --out /tmp/index.json`: `ok: true`, 8 files indexed
- generated glossary delta: 2 files, 192 insertions, 12 deletions

The temporary validation workflow was removed after the successful run; cleanup commit:

- `6784624a85c4d3b67ba57184eb3cf2197e7b4865`

No `localized_data/**` files were edited.

## Important test-discovered correction

The first bridge run produced `7 passed, 2 failed`: locked matching did not use `key_exact` because `locked_term_matches` receives source path/json path rather than a separate UI key. The locked Support Pt and Energy guards were therefore changed to `json_path_prefixes`, which is exact for their one-component `localize_dict.json` paths. The second run passed all focused and full tests.

## Remaining domain work — do not mark task complete

The Training / Support domain is still incomplete. Next worker should continue from this branch/checkpoint and resolve, with player-facing evidence and context-safe guards:

1. Training Level / facility-level terminology. Concrete current corpus example: `Outgame352008`, `训练等级`, historical VI `Cấp huấn luyện`.
2. Training success/failure/failure-rate UI. Concrete current corpus example: `SingleMode0036`, `失败率`, historical VI `Tỷ lệ thất bại`.
3. Generic Support Effect labels and repeated support-effect result/status wording.
4. Stat gain / bonus / cap / limit wording in Training/Support contexts.
5. Any remaining Bond/Friendship variants not covered by the category-155 Friendship Gauge rule must be classified before adding aliases; do not reintroduce a global bare-bond mapping.

After those are finished and validated, proceed with the task's normal completion/integration protocol. Do not advance orchestration state yet.
