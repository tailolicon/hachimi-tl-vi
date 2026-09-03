# Canonical finding implementation: Hop Step・Getchu♡

- Finding: `cf-77cc4a473bc04bcd`
- zh-CN source: `活力蹦跳・锁定胜利♡`
- JP player-facing title: `ホップステップ・ゲッチュ♡`
- Canonical target: `Hop Step・Getchu♡`
- Live blocker evidence: current retrospective review batch `tr-p3-67f8551f7780-9aa64f11a189-b5c0bcb3bd-739ce7e45e-b0140` embeds the finding as `open` / `defer` for category-147 Skill-title rows.

## Scope decision

The live finding has `match_mode: contains`, `source_paths: ["text_data_dict.json"]`, no exact keys, and no JSON-path prefix. `refresh_canonical_resolutions()` requires a canonical rule to cover the finding's recorded scope. Adding a category prefix to the canonical rule would therefore fail to cover this existing finding. The production rule instead uses the complete Skill title as an `exact` alias and restricts it to `text_data_dict.json`. This is narrower than the finding's substring matcher while still covering its source scope.

Permanent regression coverage also verifies that the exact rule does not resolve a longer source containing the title and does not resolve the same text in `localize_dict.json`.

## Durable implementation

- `scripts/harden_hop_step_getchu_finding.py` — commit `859457bf31b349d1a74acff150867272948acd43`
  - adds community canonical term `skill.hop_step_getchu`;
  - adds explicit review lock `audit.finding.skill-hop-step-getchu`;
  - adds `Hop Step・Getchu♡` to the live finding's suggested targets;
  - is idempotent and fails closed if the finding is absent.
- `tests/test_hop_step_getchu_finding_hardening.py` — commit `49dff72877add509ffee2483b0c208b5298f3b88`
  - reproduces the live finding shape;
  - proves canonical + review resolution and `active_findings(...) == []` after hardening;
  - proves negative behavior for longer containing text and another source file.

## Production acceptance in flight

Commit `49dff72877add509ffee2483b0c208b5298f3b88` triggered all required production workflows:

- Validate: run `33781663765`.
- Sync translation context: run `33781663759`.
- Sync translation review plan: run `33781663779`.

At checkpoint creation these runs had been queued/pending. Do not increment maintenance `completed_count` until the workflows succeed and live regenerated state confirms that `cf-77cc4a473bc04bcd` no longer blocks the corresponding review rows.
