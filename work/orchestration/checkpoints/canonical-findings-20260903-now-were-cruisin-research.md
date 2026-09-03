# Canonical finding research — `疾走乎 疾走乎！`

Finding: `cf-0cc9beacf4d177a8`

## Identity

- The repository's older category-147 entries use key family `10340101`–`10340103` for source title `疾走乎,疾走乎！`; historical curation already identified this as Skill `100341` but deferred because canonical identity was not yet established.
- Current public Umamusume data identifies Skill ID `100341` as Inari One's unique Skill JP `快走かな、快走かな！`.
- The released English/Global-facing title is **`Now We're Cruisin'!`**. Inari One `[Edomurasaki]` was released to EN on 2026-05-28, and current Umamusume Wiki skill/playable data pairs ID `100341`, JP `快走かな、快走かな！`, and EN `Now We're Cruisin'!`.

References:
- https://umamusu.wiki/Game:Skills/100341
- https://umamusu.wiki/Game:Inari_One_(Edomurasaki)
- https://game8.jp/umamusume/460499 (independent JP identity check: `快走かな！、快走かな！`)

## Canonical decision

Lock the project target to **`Now We're Cruisin'!`** rather than preserving one-off Vietnamese calques such as `Chạy đi, chạy đi!` / `Chạy nhanh nào, chạy nhanh nào!`.

Scope hardening must cover both proven source surfaces without broad substring leakage:
- category `147`: exact Skill-title alias `疾走乎,疾走乎！` (plus punctuation-normalized variants only if needed);
- category `172`: inheritance/factor prose containing `疾走乎 疾走乎！`.

Use item invalidation, preserve JP identity in the terminology-review lock, and add permanent tests for idempotence, both positive scopes, out-of-scope rejection, finding resolution, and removal from `active_findings()`.
