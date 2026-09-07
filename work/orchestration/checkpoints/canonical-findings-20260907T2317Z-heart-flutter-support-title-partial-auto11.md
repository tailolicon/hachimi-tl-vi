# Canonical finding checkpoint — heart-flutter support unique-effect title

Finding: `cf-34bb9869a98908b7` (`怦然心动的记忆♪`, category 150 key `20044`).

## Live diagnosis

- Fresh `active_findings` routing after Corner Recovery acceptance selects this finding before later unresolved blockers.
- The current text is `Ký ức khiến tim rung động♪`.
- The blocker is an overlapping matcher conflict, not evidence that the whole support unique-effect title is itself either Skill: `心动` is locked as `Nhịp tim rộn ràng` (JP `胸の高鳴り`) while the longer `怦然心动` is locked as `Trái tim rung động` (JP `トキメキハート`).
- Repository curation evidence independently verifies those two Skill identities. Existing review results defer this category-150 title because both substring locks cannot be satisfied naturally at once.
- The repository already uses narrow full-source exclusions plus evidence-checked context-guard resolution for the same `心动` alias in non-Skill category-128 prose.

## Durable source work

- `bd3f9a6d71604d6beed3bee4b550fd39b34c835d` extends `scripts/harden_heart_flutter_song_description_finding.py` so both nested Skill aliases exclude exactly `怦然心动的记忆♪`, while preserving direct Skill matches.
- `52eec0b6e88a007fef1230c8a5b7896a97e779ae` adds `scripts/resolve_heart_flutter_support_title_finding.py`, which resolves only `cf-34bb9869a98908b7` and only after live matcher checks prove neither locked Skill term still matches its evidence.
- `a641d91c250228cd37c9bdfe6c6a5b5a8de80056` wires that evidence-checked resolver into production Context Sync and adds its path to push triggers.
- `19353380662f61f89b2c6fb9c79cc96c0d9739cb` expands permanent regression coverage: both Skill identities remain matchable directly, category-128 prose stays excluded, category-150 title excludes both aliases, and the new resolver refuses to close before hardening but closes afterward.

## Acceptance still pending

Do not increment maintenance `completed_count` beyond 202 yet. Wait for CI/production validation of the regression head, then run the repository-required production Context Sync acceptance sequence. Only after the production Sync succeeds, the finding is no longer active on fresh `main`, and the required unchanged/no-op Sync gate succeeds may this unit be counted complete.
