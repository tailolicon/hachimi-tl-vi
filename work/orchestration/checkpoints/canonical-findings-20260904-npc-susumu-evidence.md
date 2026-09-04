# Canonical finding evidence checkpoint: 進 (NPC)

- Finding: `cf-0ed1b3254699aa40`
- zh-CN source: `进(NPC)`
- JP written name represented by the finding: `進`
- Existing Vietnamese/Latin rendering in reviewed entries: `Susumu (NPC)`
- Evidence keys: `text_data_dict.json` category 152, keys `39`, `5`, and `73`

## Live finding state

The generated live finding remains unresolved (`canonical_resolution: null`) and has an explicit `defer` review decision. Repository policy says defer remains blocking; therefore this checkpoint does **not** increment maintenance completion.

## Verification performed

- Confirmed all three finding evidence rows currently render the NPC as `Susumu (NPC)` but the finding itself contains no verified Japanese reading.
- Checked repository code/history for a resolved identity; no canonical lock for this NPC was found.
- Checked current public web results for an authoritative Uma Musume NPC identity/readout; no source was found that establishes that `進` is read `Susumu` rather than another valid Japanese reading.
- Located a public archived JP `master.mdb` mirror, but the available connector cannot query the binary database directly in this runtime, so it does not provide acceptable reading evidence by itself.

## Continuation

Do not lock `Susumu` from the kanji alone. Resume this finding only when a source can establish the Japanese reading for category-152 NPC `進` (ideally current JP master data, an official player-facing source, or another structured game-data source with reading/Latin identity). Until then preserve the defer and continue maintenance on another active blocker rather than inventing a canonical name.
