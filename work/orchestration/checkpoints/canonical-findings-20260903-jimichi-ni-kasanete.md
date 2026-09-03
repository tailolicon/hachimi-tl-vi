# Canonical finding: Skill 203412 / 地道に重ねて

- Live finding: `cf-7ade7cc862703b5a`
- zh-CN bridge: `踏实努力`
- JP Skill: `地道に重ねて`
- Skill ID: `203412`
- Current Vietnamese: `Nỗ lực bền bỉ`
- Project canonical candidate: `Tích lũy bền bỉ`

## Evidence and rationale

The live finding explicitly identifies Skill 203412 as JP `地道に重ねて` and flags zh-CN `踏实努力` as a lossy bridge. Repository curation already notes that the bridge shifts the Japanese nuance toward generic diligent effort. The Japanese `重ねて` carries the identity of steadily accumulating/building something up, so `Tích lũy bền bỉ` preserves that accumulation image more faithfully than the current bridge-derived `Nỗ lực bền bỉ`.

This is a project Vietnamese canonical title, not an assertion of an official Global localization.

## Durable implementation

- Hardener published on `main`: commit `91bc603131a6ded36737bfdcf77ad25030e859dd` (`scripts/harden_jimichi_ni_kasanete_finding.py`).
- Regression tests published on `main`: commit `1fe8b7d71ac85ddde518d1e4d0f6acb15c90d38b` (`tests/test_jimichi_ni_kasanete_finding_hardening.py`).
- Canonical rule is exact-match, item-scoped, `text_data_dict.json`, category/path prefix `147`, with `Nỗ lực bền bỉ` explicitly forbidden for this named Skill.
- Negative coverage verifies no resolution in another category, another source file, or longer generic prose containing `踏实努力`.
- Clean-worktree targeted validation: `10 passed` for the new finding tests plus context-sync auto-hardener and terminology-review application tests.

## Acceptance state

Do not advance maintenance completion yet. Verify GitHub Validate + production `Sync translation context`, then confirm live generated `glossary/canonical_findings.json` has a non-null canonical resolution for `cf-7ade7cc862703b5a` pointing to `Tích lũy bền bỉ`.
