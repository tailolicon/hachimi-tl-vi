# Canonical finding checkpoint — 素顔のココロ

Finding: `cf-c83afa810e490d16`
Source: `素顔のココロ`
Observed current target: `Trái tim chân thật`
Target: `Sugao no Kokoro`

## Evidence and diagnosis

This category-16 entry is Gold City's named solo song from STARTING GATE 08. Release catalog metadata exposes the Latin track identity as `SUGAO NO KOKORO`, while Japanese reading metadata gives `すがおのこころ`. Project song-title policy preserves verified Romanized identities rather than Vietnamese semantic calques, so the canonical player-facing target is `Sugao no Kokoro`.

## Durable implementation

- `scripts/harden_sugao_no_kokoro_song_finding.py` adds exact item-scoped category-16 community rule `song.sugao_no_kokoro` and matching terminology lock.
- Hardener commit: `e7223fe7d0004761214846549537f28bc8ad4f42`.
- `tests/test_sugao_no_kokoro_song_finding_hardening.py` proves positive resolution inside category 16 and non-resolution outside the song table.
- Regression commit: `4de29e147644953fb5b4b8b4a3be2da479fc614d`.
- Successor ordering trigger: `a11dd54786d51f688ea6a470af6c314b8d867b94`, created only after canonical materialization was already on live main.

## Production acceptance

Acceptance is complete.

- Hardener-head Validate `33930404566`: **success**.
- Regression-inclusive Validate `33930417964`: **success**, including pytest, `tlvi validate`, and index generation.
- Context Sync `33930404538`: **success**.
- Generated context commit `42b3710db1bde181192383732958b32a8ba71779` materialized the canonical lock and reduced `open_canonical_findings` from 115 to 114.
- Initial Translation Review Plan `33930404567`: **success**, but it began before context materialization, so it was not used alone as acceptance proof.
- Successor Validate `33931016991`: **success**.
- Successor Translation Review Plan `33931016988`: **success**, started after materialization.
- Live active plan `tr-p3-67f8551f7780-7419050b5eb3-b5c0bcb3bd-b803813a70` now embeds `song.sugao_no_kokoro` on the source item while `cf-c83afa810e490d16` is absent from its `canonical_findings`; the reviewer still sees the bad current translation as a normal correction candidate, but canonical maintenance no longer blocks it.

The finding is accepted. Maintenance may increment `completed_count` from 128 to 129 and continue with the next live active finding.
