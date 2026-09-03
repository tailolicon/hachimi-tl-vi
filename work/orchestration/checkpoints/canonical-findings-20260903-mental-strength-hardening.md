# Canonical finding checkpoint — `精神力量`

Finding: `cf-1fb0ec7c1c77dfb1`

## Evidence and decision

The live finding has three high-confidence evidence rows, all in `text_data_dict.json` category 147 (`3100801`, `3100802`, `3100803`). Each complete source string is `精神力量` and each current Vietnamese value is `Sức mạnh tinh thần`. The finding explicitly requires treating the complete phrase independently rather than normalizing the embedded `力量` substring to the Power stat or assuming an unrelated Skill identity from `精神力`.

Before hardening, `community_term_matches` on `精神力量` at category 147 matched `common.stat.power` through the substring alias `力量`, yielding a false Power conflict. The existing Power-context test already documents that `cf-1fb0ec7c1c77dfb1` must not be resolved merely by the generic Power context guard.

Use a narrow canonical community rule instead: exact source `精神力量`, exact `text_data_dict.json` category 147, target `Sức mạnh tinh thần`. Also exclude `精神力量` from the generic Power term's substring matching. This fixes the collision without claiming a JP/Global Skill identity that the repository has not proven.

## Durable changes

- `scripts/harden_mental_strength_phrase_finding.py` added on `main` at commit `4699e007266f3cd1bd10f237898f0928d00baade`.
  - Adds `reviewed.context.mental_strength.text147` with exact source/category scope and preferred `Sức mạnh tinh thần`.
  - Adds `精神力量` to `common.stat.power.exclude_source_contains` so the embedded `力量` alias cannot normalize this phrase to Power.
- `tests/test_mental_strength_phrase_finding_hardening.py` added on `main` at commit `b504067df42c244c86515e8a389455b66375bb47`.
  - Verifies exact category-147 `精神力量` matches only the new term.
  - Verifies longer `精神力量很重要` does not overmatch the exact rule.
  - Verifies plain stat `力量` still resolves to `Power`.
- Direct local hardener/idempotence/matcher assertions passed (`manual mental-strength check=pass`).

## Acceptance continuation

Do not increment maintenance completion count from 30 to 31 yet. Wait for the push-triggered production Context Sync and Review-plan Sync associated with the hardener/test commits. After both succeed, refresh live `main`, confirm `cf-1fb0ec7c1c77dfb1.canonical_resolution.target_vi == "Sức mạnh tinh thần"` with the intended scoped term and confirm `scripts.canonical_findings.active_findings` excludes the finding. Only then mark it production-accepted and advance the maintenance count.
