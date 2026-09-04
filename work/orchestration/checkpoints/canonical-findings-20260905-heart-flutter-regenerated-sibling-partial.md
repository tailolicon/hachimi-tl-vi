# Canonical finding checkpoint — regenerated 心动 song-prose sibling

Finding: `cf-7b678d0f1ed3e725`
Related accepted finding: `cf-251ca78d8992cf8d`
Canonical Skill term: `reviewed.skill_name.3346bd209f49`
Canonical Skill target: `Nhịp tim rộn ràng`

## Live diagnosis

The generated terminology queue placed this finding immediately beside the already-accepted `cf-251ca78d8992cf8d` on the same category-128 source description. Its concept is the same false-positive condition: generic prose `心动` must not be interpreted as the locked Skill title. The existing hardener already excludes the full source description, so this regenerated ID needs resolver registration rather than a second semantic rule.

## Durable implementation

- Resolver commit `3b869c761f3127a5689747de34f0201a1608453c` registers `cf-7b678d0f1ed3e725` with the same evidence-backed locked-term guard as `cf-251ca78d8992cf8d`.
- The resolver still refuses to close either finding if the Skill rule matches any evidence row.
- Regression commit `c3af5a5a7efc2850d63e9511a2b88f9ecfcb9c1d` expands `tests/test_heart_flutter_song_description_finding_hardening.py` so both finding IDs must resolve to the exact `context_guard` result after the prose exclusion.

## Acceptance pending

Do not increment maintenance above 127 until production Validate `33930123751`, Context Sync `33930123738`, and Translation Review Plan `33930123755` succeed and live regenerated context no longer exposes `cf-7b678d0f1ed3e725` as an active blocker.
