# Canonical finding implementation: 火神鸣 / 火神鳴

Claim: `canonical-findings-maintenance-gpt56sol-20260903T183533Z`
Finding: `cf-baa64ebea736be2a`

## Evidence

- Live zh-CN source title: `火神鸣`, exact Skill-name entries under `text_data_dict.json` category `147`.
- JP player-facing unique Skill title: `火神鳴`.
- JP references identify `火神鳴` as the unique Skill of alternate-outfit Tamamo Cross and give the same activation/effect text as the zh-CN entry.
- Repository `glossary/skill_name_style.json` requires compact Vietnamese game-title rhythm while using JP wording as the semantic/identity guard and allows concise Hán-Việt compounds when faithful.

## Decision

Lock target: `Hỏa Thần Minh`.

This preserves the exact three-morpheme title identity (`火` / `神` / `鳴`) in compact Hán-Việt form and replaces the sentence-like current rendering `Hỏa thần vang`.

## Durable implementation

- `scripts/harden_kashinmei_finding.py` at commit `ff26f93777b8ec85e8a9d2c045eb239010c70f51` adds an exact, source-path-scoped community Skill-name rule, an explicit JP-backed review lock, and the accepted target to finding evidence.
- `tests/test_kashinmei_finding_hardening.py` at commit `a2566da0aae188c837022ce625af59d04355f47a` protects idempotence, canonical-resolution clearing of the active finding, and non-overmatch against longer source text or another file.

## Validation gate

Production validation is pending on the final implementation head. Require the repository Validate, Sync translation context, and Sync translation review plan surfaces to succeed, then confirm the refreshed canonical ledger no longer reports `cf-baa64ebea736be2a` through `active_findings(...)` and worker-facing unresolved review evidence is refreshed before acceptance.
