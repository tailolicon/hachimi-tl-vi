# Canonical finding checkpoint: Tanino Gimlet / Aufheben

- Finding: `cf-1e27154bb898948c`
- zh-CN source: `霹雳中的奥伏赫变`
- Verified JP Skill identity: `霹靂のアウフヘーベン` (Skill ID 100841, Tanino Gimlet)
- Project canonical Vietnamese title selected: `Aufheben giữa lôi đình`
- This is a project canonical title. It is **not** asserted to be an official Global/English localization.

## Evidence and decision

The prior checkpoint correctly rejected promoting inherited variants such as `Wall Crack Aufheben`, `Lôi Đình Phá Bích`, or `Long Trời Lở Đất - Aufheben` without stronger evidence. The remaining ambiguity was whether the loanword itself should be semantically flattened or preserved.

Japanese dictionary evidence identifies `アウフヘーベン` as German **Aufheben**. The pinned game identity independently establishes that the Skill is `霹靂のアウフヘーベン`. This makes preserving `Aufheben` the least lossy treatment of the distinctive title element; `giữa lôi đình` gives the thunder motif a compact Vietnamese form without pretending an external official localization exists.

Reference evidence consulted during this maintenance unit:
- Kotobank entry for `止揚`, describing German `Aufheben` / Japanese `アウフヘーベン` and its philosophical loanword identity.
- National Diet Library catalog/search records using `アウフヘーベン / Aufheben`, corroborating the Latin spelling.
- Repository-pinned curation evidence for Skill ID 100841 / JP `霹靂のアウフヘーベン`.

## Durable implementation

- `scripts/harden_tanino_gimlet_aufheben_finding.py`
  - exact `skill_name` community rule for `霹雳中的奥伏赫变`
  - target `Aufheben giữa lôi đình`
  - scoped to `text_data_dict.json` category `147`
  - terminology-review lock records JP identity and explicitly labels the target project-canonical rather than official Global
- `tests/test_tanino_gimlet_aufheben_finding_hardening.py`
  - verifies idempotent hardening
  - verifies `review_resolution`
  - verifies community-layer `canonical_resolution`
  - verifies category/path scoping does not leak

Regression commit: `98a33682015b7fccc9b0c911300345540dac5a91`.
GitHub Actions `Validate` for that commit completed successfully. `Sync translation review plan` run `33757177896` was still pending at the time of this checkpoint, so generated glossary/ledger/review-plan state had not yet been treated as published resolution.
