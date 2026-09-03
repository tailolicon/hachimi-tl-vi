# Canonical findings maintenance research — 五行之兽彩光合奏

Claim: `canonical-findings-maintenance-gpt56sol-20260903T074300Z`

Finding `cf-078ae8e41d26c58b` is an active proper-name blocker for zh-CN `五行之兽彩光合奏`. Current reviewed output is `Hợp tấu ánh sắc của Ngũ Hành Thú`.

## Repository evidence

- Source entries are Skill-name rows in `text_data_dict.json` category `147`, including keys `10980201`, `10980202`, and `10980203`.
- Older curation (`term-0013`) deferred the title because the stylized imagery had not yet been tied to a stable JP identity.
- `glossary/skill_name_style.json` requires JP wording to guard the original motif when zh-CN materially reshapes imagery.

## Fresh identity evidence

The zh-CN title maps to JP unique Skill **`五獣挙りて彩光奏づ`** for Copano Rickey `[光彩陸離☆招福衣]`.

Evidence checked 2026-09-03:
- https://wiki.biligame.com/umamusume/%E4%BA%94%E7%8D%A3%E6%8C%99%E3%82%8A%E3%81%A6%E5%BD%A9%E5%85%89%E5%A5%8F%E3%81%A5 — explicitly pairs `五獣挙りて彩光奏づ` with zh-CN `五行之兽彩光合奏`.
- https://wiki.biligame.com/umamusume/%E5%9B%A0%E5%AD%90%3A%E4%BA%94%E7%8D%A3%E6%8C%99%E3%82%8A%E3%81%A6%E5%BD%A9%E5%85%89%E5%A5%8F%E3%81%A5 — key `10980201` is the factor for the same JP Skill title, matching the repository key family.
- https://umamusu.wiki/Game%3ACopano_Rickey_%28%E5%85%89%E5%BD%A9%E9%99%B8%E9%9B%A2%E2%98%86%E6%8B%9B%E7%A6%8F%E8%A1%A3%29 — identifies the same JP-only unique Skill for that Copano Rickey variant.

This proves the semantic bridge is materially lossy: JP says `五獣` (five beasts), while zh-CN rewrites it as `五行之兽` (beasts of the Five Elements). The existing Vietnamese `Ngũ Hành Thú` therefore preserves a zh-CN invention that is absent from the JP identity.

## Canonical decision

Use **`Ngũ Thú Tề Tựu, Tấu Khúc Sắc Quang`**.

Rationale:
- `Ngũ Thú` restores the JP `五獣` motif and removes the unsupported Five-Elements interpretation.
- `Tề Tựu` captures `挙りて` in a compact literary title rhythm.
- `Tấu Khúc Sắc Quang` keeps the `彩光` + `奏づ` image without turning the Skill name into explanatory prose.
- The target follows the repository's compact literary/Hán-Việt style for stylized unique Skill names.

Hardening should match the exact zh-CN alias in `text_data_dict.json`, remain source-path scoped, forbid the old `Hợp tấu ánh sắc của Ngũ Hành Thú` rendering, add a terminology-review lock carrying JP `五獣挙りて彩光奏づ`, and include a regression proving longer strings containing the alias do not inherit this proper-name mapping.
