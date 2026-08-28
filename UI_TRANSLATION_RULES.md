# UI translation and layout rules

This file is mandatory context for any worker translating `localize_dict.json` or other fixed-size UI text.

## Goal

A UI translation passes only when it satisfies **all three**:

1. it conveys the correct meaning;
2. it uses the correct Uma Musume player-facing terminology for common gameplay labels and named mechanics/events/modes;
3. it fits the fixed control.

Semantic readability alone is not enough.

## Player-facing terminology rule

Do not assume a Japanese/Chinese source term should be semantically calqued into Vietnamese. The project intentionally keeps many common gameplay labels in their EN-version/player-facing form.

Before translating or keeping a gameplay/system label:

1. check `glossary/ui_community_terms.json` first;
2. if it matches, use an accepted English/Romanized form from that file even when an older `term_registry.json` entry still contains a Vietnamese target;
3. otherwise check locked `glossary/term_registry.json`;
4. use established official/player-facing terminology for unresolved named systems;
5. translate generically only when the concept is genuinely generic.

Current Vietnamese output is never evidence of correctness.

### Common EN terms

The current player-facing reference includes terms such as `Trainer`, `Support Card`, `Mood`, `Speed`, `Stamina`, `Power`, `Guts`, `Wit`, `Aptitude`, `Rating`, `Condition`, `Legacy`, `Guest Legacy`, `Inspiration`, `Spark`, `Scenario`, `Track`, `Turf`, `Dirt`, `Distance`, `Sprint`, `Mile`, `Medium`, `Long`, `Style`, `Front Runner`, `Pace Chaser`, `Late Surger`, `End Closer`, `Skill`, `Unique Skill`, and `Evolution Skill`.

Examples:

| Source concept | Reject | Preferred |
| --- | --- | --- |
| スピード / 速度 | Tốc độ | **Speed** |
| スタミナ / 耐力 | Thể lực | **Stamina** |
| 根性 / 毅力 | Ý chí | **Guts** |
| 賢さ / 智力 | Trí tuệ | **Wit** |
| やる気 / 干劲 | Tinh thần / Hứng khởi | **Mood** |
| サポートカード / 支援卡 | Thẻ hỗ trợ | **Support Card** |
| 芝 / 草地 | Sân cỏ | **Turf** |
| 短距離 / 短距离 | Cự ly ngắn | **Sprint** |
| 中距離 / 中距离 | Cự ly trung bình | **Medium** |
| 長距離 / 长距离 | Cự ly dài | **Long** |
| 逃げ / 领跑 | Nige | **Front Runner**, compact **Front** |
| 先行 | Senko | **Pace Chaser**, compact **Pace** |
| 差し / 差行 | Sashi | **Late Surger**, compact **Late** |
| 追込 / 追马 | Oikomi | **End Closer**, compact **End** |
| 英雄量表 / ヒーローゲージ | Thanh Anh hùng | **Hero Gauge** |
| 英雄技能 / ヒーロースキル | Kỹ năng Anh hùng | **Hero Skill** |
| 英雄联盟赛 / リーグオブヒーローズ | Liên minh Anh hùng / Hero League | **League of Heroes**, compact **LoH** |
| 主要阶段 / メインステージ | Giai đoạn chính when used as the named LoH stage | **Main Stage** |
| 特别阶段 / エクストラステージ | Giai đoạn đặc biệt when used as the named LoH stage | **Extra Stage** |

Do not generalize a matched game term to unrelated generic prose. Use source/key/context and registry metadata.

If the repository does not identify an unfamiliar named mechanic, do not invent a Vietnamese canonical label. Verify it or defer.

## Skill category vs skill name

`Skill`, `Unique Skill`, and `Evolution Skill` are gameplay category labels and stay English.

The **proper name of an individual skill is different**: it should normally be localized into a concise Vietnamese/Hán-Việt ability name according to `glossary/style_rules.json`. Do not keep an individual skill name in English merely because the word `Skill` itself stays English, and do not turn a skill name into a long effect description.

## Label levels

Use the shortest level that still makes sense in context:

1. **Full** — roomy screens, descriptions, help text.
2. **Compact** — normal buttons, tabs, menu tiles.
3. **Micro** — very small chips, counters, bottom navigation, narrow header buttons.

Canonical full/compact/micro forms live in `glossary/ui_short_forms.json`. Named/common gameplay terms that should remain player-facing live in `glossary/ui_community_terms.json`.

## Hard writing rules

- Prefer 1–3 short words for buttons and menu tiles.
- Do not stack synonyms with `/` just to preserve every source nuance.
- Do not repeat context already visible in the screen. On a Gacha screen, `Lịch sử` is better than `Lịch sử Gacha`.
- Keep `Uma Musume` in prose, but `Uma` is allowed in cramped labels.
- Preserve canonical English/Romanized gameplay terms even when surrounding grammar is shortened.
- Preserve placeholders, tags, runtime tokens, and the source newline count.
- Never insert a new newline just to rescue an overlong translation. Shorten the wording instead.
- If the source already has one newline, each translated line must independently fit its side of the control.
- Avoid verbose helper words such as `thực tế`, `chức năng`, `dành cho`, `được dùng để`, or duplicated nouns when a compact label is clear.
- Prefer natural Vietnamese nouns/verbs for genuinely generic UI: `Đổi`, `Kho quà`, `Tủ cúp`, `Danh hiệu`, `Lịch sử`.
- A compact label may omit information already unambiguous from icon/header/screen, but must not change the action or mechanic.

## Visual-width budget

Character count is not enough because CJK glyphs and Latin/Vietnamese letters have different widths. Use this mental model for short labels:

- CJK kana/hanzi: about `1.0` unit each.
- Vietnamese/Latin letter or digit: about `0.55–0.60` unit.
- Space/punctuation: about `0.3–0.4` unit.

For a source line up to roughly 8 CJK-width units, aim for:

`target_width <= max(5.0, source_width * 1.55 + 0.5)`

This is a heuristic, not permission to fill the entire budget. Shorter is usually better.

Examples of generic compacting:

| Source concept | Bad | Preferred |
| --- | --- | --- |
| 奖杯陈列室 | Phòng trưng bày cúp | **Tủ cúp** |
| 简介 / 训练员名片 | Hồ sơ / Danh thiếp Trainer | **Hồ sơ / Trainer** |
| 物品 / 转换 | Vật phẩm / Chuyển đổi | **Vật phẩm / Đổi** |
| 支援卡详情 | Chi tiết Support Card | **Chi tiết thẻ** |
| 历史 | Lịch sử Gacha | **Lịch sử** when already on the Gacha screen |
| 每日1次 | 1 ngày 1 lần | **1 lần/ngày** |

## Control budgets

When layout metadata is known, use these targets:

- tiny chip / counter: 1 short word or <= ~6 visual units;
- header / pill button: <= ~7 visual units;
- normal button / tab: <= ~8 visual units;
- menu tile: <= 2 source-prescribed lines, each <= ~8 visual units;
- bottom navigation: 1 word whenever possible;
- dialog title: <= ~12 visual units;
- description/body copy: prioritize natural Vietnamese; compact-label rules do not apply.

A canonical gameplay name may exceed a generic micro-label ideal. Shorten surrounding grammar or use an explicitly accepted compact alias (`LoH`, `Front`, `Pace`, `Late`, etc.); do not translate the mechanic into Vietnamese merely to save width.

## Canonical overrides

`glossary/ui_overrides.json` contains key-level and legacy exact-text fixes.

Policy-v2 UI-review-generated overrides are considered **untrusted during the policy-v3 reset**. The application layer skips an override whose reason identifies it as `Reviewed by UI pipeline ui-p2-...` until a current review either revises or reconfirms that key.

Manual/non-v2 overrides remain active unless they conflict with a newer explicit player-facing terminology policy; such conflicts must be reviewed, not silently trusted.

## Worker QA before persisting

For every short `localize` entry:

1. identify whether it is a label/action rather than prose;
2. identify any common gameplay term or named mechanic/event/mode/resource/stage;
3. consult `ui_community_terms.json` **before** conflicting legacy term mappings;
4. reject Vietnamese calques when an accepted player-facing English/Romanized form exists;
5. if this is an individual skill name, apply the skill-name localization policy instead of the generic keep-English rule;
6. consult `ui_short_forms.json`;
7. compare visual width to the source line;
8. remove redundant context and slash compounds;
9. ensure source newline count is unchanged;
10. prefer the shortest natural wording that preserves action and canonical terminology.

If the established term itself is uncertain, defer instead of inventing one.

## Screenshot QA

A release-quality UI pass should check at least Home, Menu, Gacha, Training, Support/Card details, Shop/Exchange, Missions, Race entry, Profile, League of Heroes, Champions Meeting, and common dialogs on Android and Windows.

Reject a UI string when it:

- protrudes outside its control;
- overlaps an icon, badge, counter, or neighboring label;
- wraps to an extra line not present in the source;
- clips Vietnamese diacritics;
- becomes visibly smaller than neighboring labels because best-fit had to shrink it too far;
- leaves raw Chinese/Japanese that is supposed to be translated;
- translates a known EN-version gameplay term into Vietnamese against the player-facing registry;
- keeps an individual skill name as a bland untranslated English title when a proper localized Vietnamese/Hán-Việt skill name is expected;
- invents a Vietnamese name for a mechanic/event the player community recognizes by another canonical/player-facing term.
