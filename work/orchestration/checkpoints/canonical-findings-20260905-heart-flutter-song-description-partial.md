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
- Regression: `tests/test_heart_flutter_song_description_finding_hardening.py`
- Regression commit: `069c93530c2af1238324dcb5e1ab74465993aea9`
- The hardener appends the full source description to `reviewed.skill_name.3346bd209f49.exclude_source_contains`, minimizing scope while preserving direct Skill matches.
- Regression asserts idempotence, a positive direct Skill match, and no match for the category-128 prose item.

## Acceptance pending

Do not increment maintenance `completed_count` above 126 until production Validate succeeds, Context Sync materializes the context guard and succeeds, and a successor Translation Review Plan rebuild confirms `cf-251ca78d8992cf8d` is absent from the affected worker-facing item.
