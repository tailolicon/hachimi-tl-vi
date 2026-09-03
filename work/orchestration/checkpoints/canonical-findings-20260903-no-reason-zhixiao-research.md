# Canonical finding checkpoint — No Reason unique Skill

Finding: `cf-0fe33e249eca596b`

Source zh-CN alias: `知宵欺敌 百战不殆`

Live finding shape on `main` is `status: open`, `match_mode: contains`, `source_paths: [text_data_dict.json]`, no json-path prefix, `canonical_resolution: null`, `review_resolution: null`. Evidence is the three inheritance-factor rows for trainee id `109601`, currently rendered as `Thấu thời lừa địch, trăm trận không nguy`.

## Identity evidence

Fresh external verification identifies this as No Reason's unique Skill. Japanese sources use the exact title `知宵欺敵、百戦不殆`; GameWith and 4Gamer both identify it as No Reason's unique Skill, and the current Umamusume Wiki marks the trainee/Skill as JP-only rather than exposing an official English-release Skill name.

Because the zh-CN title is effectively the same title in simplified characters rather than a divergent localization, there is no source-bridge identity conflict. The existing Vietnamese wording is semantically aligned and can be canonicalized instead of inventing a speculative English name.

## Proposed canonical decision

Lock the item-scoped Skill alias to `Thấu thời lừa địch, trăm trận không nguy` for `text_data_dict.json`, with `match_mode: contains` so the alias covers the longer inheritance-factor strings without overmatching unrelated source paths. Do not patch `localized_data/**` directly.

Next: add a permanent `harden_*_finding.py` hardener plus regression coverage proving contains-scope resolution and idempotence; then run repository validation / production Sync before marking the finding accepted.
