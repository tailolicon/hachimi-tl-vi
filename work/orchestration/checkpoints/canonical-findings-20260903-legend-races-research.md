# Canonical findings maintenance research — Legend Race labels

Claim: `canonical-findings-maintenance-gpt56sol-20260903T074300Z`

Two active proper-name findings are tied to transfer-blocking UI sentences in `localize_dict.json`:

- `cf-cf51d5270ed06b18`: zh-CN substring `传奇比赛`, item key `Character0335`, current VI sentence uses `Giải đấu Huyền thoại`.
- `cf-6f1b22f01d3e293a`: zh-CN substring `每日传奇比赛`, item key `Character408001`, current VI sentence uses `Đua Huyền thoại Hằng ngày`.

## Stable cross-locale evidence

Maintained Hachimi Global-English data maps the same keys as:

- `Character0335`: `Cannot transfer Veteran Umamusume that are currently running in a Legend Race.`
- `Character408001`: `You cannot transfer Veteran Umamusume that are registered for a Daily Legend Race.`

This pins the named game-mode identities to **Legend Race** and **Daily Legend Race**, rather than literal Vietnamese paraphrases of the zh-CN bridge.

## Canonical decision

Lock the key-scoped source aliases:

- `传奇比赛` -> **`Legend Race`** on `Character0335`.
- `每日传奇比赛` -> **`Daily Legend Race`** on `Character408001`.

Use `match_mode: contains` with exact key scopes because both findings occur inside complete transfer-warning sentences. This resolves the existing item-scoped findings without creating a broad source-wide matcher for unrelated text.

Forbid the current local paraphrases `Giải đấu Huyền thoại` and `Đua Huyền thoại Hằng ngày` inside those exact item scopes. Regression coverage must prove the mappings do not apply to another key or source path.
