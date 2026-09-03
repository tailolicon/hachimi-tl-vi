# Canonical finding: 永井正道 / Masamichi Nagai

- Live finding: `cf-1bd479584e40d767`
- Source alias: `永井正道`
- Canonical Latin spelling: `Masamichi Nagai`
- Source scope: `text_data_dict.json`, `match_mode: contains`

## Evidence and rationale

This finding was originally raised because Skill alias `正道` overmatched inside creator name `永井正道`. The durable resolution has two complementary parts: the Skill rule excludes the full creator name, and the creator credit has its own verified Latin identity.

POPHOLIC's official creator profile lists `永井 正道` as `Masamichi Nagai` and explicitly names Umamusume: Pretty Derby `はじまりのSignal` among his works. MusicBrainz independently credits `永井正道 (Masamichi Nagai)` on Umamusume WINNING LIVE 01.

## Durable implementation

- Existing overlap hardener: `scripts/harden_righteous_path_creator_overlap_finding.py`, which keeps `永井正道` in `skill.righteous_path.exclude_source_contains`.
- Creator hardener: `scripts/harden_masamichi_nagai_finding.py` (`12c5fabda5ec362058c1f395d27c1d2b2763e98e`).
- Creator regression test: `tests/test_masamichi_nagai_finding_hardening.py` (`629fa76e1b026a69e49d397f33cd4cdcd60f7a02`).
- Context-guard resolver registration: `scripts/resolve_context_guard_findings.py` (`09c30588e80fd8800f9ffaa87e1b07df94bce2a3`).
- Context regression test fixture corrected to the live locked-term schema in `002f83f2c998abdda692907b8afaa6ff9385a09d`; its full test job passed, including pytest, `tlvi validate`, and index generation.

## Production acceptance

- Production Sync translation context run `33766947719` checked out resolver commit `09c30588e80fd8800f9ffaa87e1b07df94bce2a3`, ran the full hardener set, refreshed canonical findings, ran context-guard resolution successfully, and passed the context pipeline (`548 passed`).
- Live `glossary/canonical_findings.json` resolves the `永井正道` finding to canonical target `Masamichi Nagai` via reviewed proper-name lock `reviewed.proper_name.f6075d794672` / `audit.finding.masamichi-nagai-creator`.
- The separate `skill.righteous_path` exclusion remains the regression-protected guard preventing `正道` from matching inside the creator name. The negative regression test proves the resolver would keep the context finding open if that exclusion were absent.

The systemic overmatch is neutralized and the full creator identity is canonicalized. This finding is durably resolved and maintenance `completed_count` may advance by one.
