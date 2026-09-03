# Canonical finding implementation: 烈華の洗礼

- Finding: `cf-5beb3f07936f9c9e`
- zh-CN source: `烈华的洗礼`
- JP player-facing title: `烈華の洗礼`
- Character/identity: Gentildonna unique Skill
- Canonical target: `Lễ thanh tẩy của hoa rực cháy`
- Live blocker evidence: current retrospective-review rows still embed the finding as `open` / `defer` for the Skill title because earlier curation lacked a verified JP identity.

## Evidence and decision

Current external references identify `烈華の洗礼` as Gentildonna's unique Skill. Earlier repository curation explicitly deferred `烈华的洗礼` because the JP alias had not yet been verified. The existing Vietnamese title is semantically compatible with the now-verified Japanese title, and there is no stronger official Global English title or repository evidence demonstrating that the current Vietnamese wording is wrong. Therefore this hardening locks the existing target instead of introducing translation churn from an unsupported alternate rendering.

Evidence consulted:

- Game8 Uma Musume Skill page for `烈華の洗礼`, which associates the Skill with Gentildonna.
- umamusu.wiki Skill record for `烈華の洗礼`, which identifies it as the Unique Skill for Gentildonna.
- Official Uma Musume character page for canonical Roman character identity `Gentildonna`.
- Repository curation `work/curation/results/term-0059/claim-gpt56sol-20260827T045608Z-1f6a3c.json`, which records that the prior defer was specifically due to missing verified JP alias evidence.

## Scope decision

The live finding uses `match_mode: contains`, `source_paths: ["text_data_dict.json"]`, with no key or JSON-path prefix. As with the accepted Hop Step・Getchu♡ finding, the canonical rule uses the complete Skill title as an `exact` alias and restricts it to `text_data_dict.json`. This is narrower than the worker finding while still covering its recorded source scope. The permanent regression also proves that this exact rule does not resolve a longer source containing the title or the same text in another source file.

## Durable implementation

- `scripts/harden_rekka_no_senrei_finding.py` — commit `68c166551097a93a341e8f985f4f4fa38ecf8852`
  - adds exact community canonical term `skill.rekka_no_senrei`;
  - adds explicit review lock `audit.finding.skill-rekka-no-senrei`;
  - adds `Lễ thanh tẩy của hoa rực cháy` to the finding's suggested targets;
  - is idempotent and fails closed if the finding is absent.
- `tests/test_rekka_no_senrei_finding_hardening.py` — commit `eb3e3773247742f6ded7bb892be89fc053c57134`
  - reproduces the live finding shape;
  - proves canonical + review resolution and `active_findings(...) == []` after hardening;
  - proves negative behavior for longer containing text and another source file.

## Acceptance pending

Do not increment maintenance `completed_count` until repository validation, translation-context sync, and translation-review-plan sync succeed and live regenerated state proves this finding no longer blocks its review rows.
