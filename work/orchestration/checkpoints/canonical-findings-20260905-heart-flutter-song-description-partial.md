# Canonical finding checkpoint — generic 心动 in song-description prose

Finding: `cf-251ca78d8992cf8d`
Canonical Skill term: `reviewed.skill_name.3346bd209f49`
Canonical Skill target: `Nhịp tim rộn ràng`

## Diagnosis

The live finding is not asking to rename the Skill. The existing locked Skill rule for zh-CN `心动` is valid, but it overmatches ordinary prose in `text_data_dict.json` category 128, item `1025`:

`疾驰的一等星闪耀着，充满勇气与希望的歌曲。\n心动的预感――那就是比赛开始的信号`

Here `心动的预感` describes a fluttering/exciting premonition before the race; it is not the distinct Skill title. The current Vietnamese prose already treats it generically rather than as the Skill name.

## Durable repair

- Hardener: `scripts/harden_heart_flutter_song_description_finding.py`
- Hardener commit: `4a693dc0e4126002224f3ab85aeb434d94a191c1`
- The hardener appends the full source description to `reviewed.skill_name.3346bd209f49.exclude_source_contains`, minimizing scope while preserving direct Skill matches.
- Initial regression commit: `069c93530c2af1238324dcb5e1ab74465993aea9`
- Initial production Validate `33928399567`: **success**.
- Initial Context Sync `33928399621`: **success**, including all hardeners, finding refresh, context-guard resolver, tests, and generated-context commit step. However, live `glossary/canonical_findings.json` still showed `cf-251ca78d8992cf8d.canonical_resolution = null` afterward.

## Resolver wiring correction

Inspection of `scripts/resolve_context_guard_findings.py` showed that a neutralized overmatch is closed only when the finding ID is registered in `GUARDS`/`POSITIVE_EVIDENCE_GUARDS`. The Skill exclusion itself was correct, but this new finding ID had no resolver registration.

- Resolver wiring commit: `26ca0c8d51e5c59bd7048777c609a3fb4b442e7f`
- Registration maps `cf-251ca78d8992cf8d` to locked term `reviewed.skill_name.3346bd209f49` / `Nhịp tim rộn ràng`.
- The resolver remains evidence-backed: it refuses to close the finding if that Skill rule still matches any evidence row; it writes a `context_guard` resolution only after the overmatch is actually neutralized.
- Expanded regression commit: `7b47c43cad7df167d5cacc5d9ed45f638b85c0aa`
- The expanded regression asserts hardener idempotence, positive direct Skill matching, no category-128 prose match, and exact resolver output `{layer: context_guard, term_id: reviewed.skill_name.3346bd209f49, target_vi: Nhịp tim rộn ràng}`.
- Production Validate `33928805667`: **success** on the resolver-wiring regression head.
- Production Context Sync `33928805680`: pending runner allocation at the latest checkpoint.
- Push-triggered Review Plan `33928805723`: not yet acceptance proof. Use it only if its actual rebuild starts after production context materialization; otherwise require a later successor rebuild.

## Acceptance pending

Do not increment maintenance `completed_count` above 126 until:

1. Context Sync `33928805680` (or a newer equivalent run containing commits `26ca0c8d...` and `7b47c43...`) succeeds;
2. live `glossary/canonical_findings.json` shows `cf-251ca78d8992cf8d` resolved by `context_guard` to `reviewed.skill_name.3346bd209f49`;
3. a successor Translation Review Plan rebuild starts from the materialized context and succeeds; and
4. the affected regenerated worker-facing item no longer exposes this finding as a blocker.
