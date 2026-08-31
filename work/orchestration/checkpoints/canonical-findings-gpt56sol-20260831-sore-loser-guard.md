# Canonical findings maintenance checkpoint — 不服输 descriptor guard

Claim: `canonical-findings-maintenance-gpt56sol-20260831T154738Z-a9f4`

Resolved implementation for live blocking finding `cf-857f68c97ee8efed` (`不服输的傲娇少女`):

- added `scripts/harden_sore_loser_descriptor_context_finding.py`
- the hardener preserves locked Skill `skill.201072` / `不服输` in legitimate Skill-flavored phrases while excluding the ordinary descriptor `不服输的傲娇少女`
- added `tests/test_sore_loser_descriptor_context_finding_hardening.py`
- regression proves the descriptor no longer matches the Skill lock, `超×9不服输！` still matches, and the finding resolves through the context-guard layer
- added `cf-857f68c97ee8efed` to `scripts/resolve_context_guard_findings.py`

Source commits on main:
- hardener: `8b203847fab2adea4c8684c3372070c316c4ac63`
- regression: `5999ca65f35de0a9e5fe955d5635c14e2b499a75`
- resolver guard: `2403bb1c35e762f457a41d4da3c73bb31d4aaf67`

`sync-context.yml` is responsible for running every finding hardener, refreshing canonical findings, resolving context guards, running the full pytest suite, and committing generated glossary state. Validation/generation remains to be observed live before counting this finding fully resolved.
