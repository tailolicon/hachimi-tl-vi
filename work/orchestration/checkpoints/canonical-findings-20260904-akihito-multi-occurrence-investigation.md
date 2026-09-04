# Canonical finding maintenance checkpoint — 明人(NPC) multi-occurrence investigation

Finding `cf-9a0b738dae85c3a2` is the next active proper-name blocker under investigation after accepted Masato maintenance count 104.

## Live evidence

The active review plan remains `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0`. GitHub code search scoped to that exact plan reports five batch files containing `明人(NPC)`: `b0134`, `b0135`, `b0136`, `b0138`, and `b0139`.

Direct batch reads establish at least these exact `text_data_dict.json` paths:

- `152/35` — `b0138`, current rendering `Akihito (NPC)`
- `152/69` — `b0139`, current rendering `Akihito (NPC)`
- `152/103` — `b0135`, current rendering `Akihito (NPC)`
- `152/137` — `b0136`, current rendering `Akito (NPC)`

The inconsistent current renderings (`Akihito` vs `Akito`) are additional evidence that no reusable reading should be canonized without authoritative identity evidence. The canonical finding itself is open/deferred and has no suggested target.

## Safety constraint / continuation

Do **not** create a broad category-`152` ignore and do **not** promote either `Akihito` or `Akito` as canonical. Before implementing a scoped ignore, enumerate every `明人(NPC)` occurrence inside the five live batch files and record every exact item path. The current evidence indicates at least one additional occurrence not represented by the four paths above.

Once all exact paths are enumerated, use the same item-scoped hardening shape proven for Toru, Nozomi, and Masato: `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, exact `json_path_prefixes`, regression test, then production Validate + context Sync + review-plan Sync before incrementing maintenance count.
