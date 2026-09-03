# Canonical findings maintenance research — Champions Meeting league labels

Claim: `canonical-findings-maintenance-gpt56sol-20260903T074300Z`

This checkpoint resolves two active exact system-label findings in `localize_dict.json`:

- `cf-10ef1d1f7bea118d`: zh-CN `公开联赛`, key `Champions0601`, current VI `Giải đấu mở`.
- `cf-c0936acad5f22c2f`: zh-CN `等级联赛`, key `Champions0602`, current VI `Giải đấu theo hạng`.

## Identity evidence

The stable Hachimi keys are exposed by maintained Global-English localization as:

- `Champions0601`: **Open League**
- `Champions0602`: **Graded League**

Repository evidence: `C-rrptd/Hachimi-TL-Global-EN/localized_data/localize_dict.json`.

Current Global Champions Meeting documentation/guides also use these same proper UI labels, so these are established released terminology rather than translation guesses.

## Repository policy fit

The project already keeps established gameplay/event mechanics in English/Romanized form and locks `Champions Meeting` itself as an English event name. Literal Vietnamese paraphrases therefore create needless divergence from the released UI identity.

## Canonical decision

Lock:

- `公开联赛` -> **`Open League`**
- `等级联赛` -> **`Graded League`**

Forbid the current literal forms `Giải đấu mở` and `Giải đấu theo hạng` for these exact labels.

Both rules can safely be exact-source scoped to `localize_dict.json`: unlike generic bridge vocabulary such as `奖池`, these complete labels identify the two Champions Meeting league classes and do not require a broad contains matcher.

Hardening should add exact community rules plus terminology-review locks, and regressions proving longer strings and other source paths do not inherit the mappings.
