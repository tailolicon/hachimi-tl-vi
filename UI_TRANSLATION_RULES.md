# UI translation and layout rules

This file is mandatory context for any worker translating `localize_dict.json` or other fixed-size UI text.

## Goal

A translation is not acceptable merely because it is semantically correct. It must also fit the control it is rendered in. For fixed-size UI, **semantic clarity + visual fit** outrank literal completeness.

## Label levels

Use the shortest level that still makes sense in context:

1. **Full** — roomy screens, descriptions, help text.
2. **Compact** — normal buttons, tabs, menu tiles.
3. **Micro** — very small chips, counters, bottom navigation, narrow header buttons.

Canonical full/compact/micro forms live in `glossary/ui_short_forms.json`.

## Hard writing rules

- Prefer 1–3 short words for buttons and menu tiles.
- Do not stack synonyms with `/` just to preserve every source nuance.
- Do not repeat context already visible in the screen. On a Gacha screen, `Lịch sử` is better than `Lịch sử Gacha`.
- Keep `Uma Musume` in prose, but `Uma` is allowed in cramped labels.
- Preserve placeholders, tags, runtime tokens, and the source newline count.
- Never insert a new newline just to rescue an overlong translation. Shorten the wording instead.
- If the source already has one newline, each translated line must independently fit its side of the control.
- Avoid verbose helper words such as `thực tế`, `chức năng`, `dành cho`, `được dùng để`, or duplicated nouns when a compact label is clear.
- Prefer natural Vietnamese nouns/verbs: `Đổi`, `Kho quà`, `Tủ cúp`, `Danh hiệu`, `Lịch sử`.
- A compact label may omit information that is already unambiguous from the icon, section header, or current screen, but must not change the action or game mechanic.

## Visual-width budget

Character count is not enough because CJK glyphs and Latin/Vietnamese letters have different widths. Use this mental model for short labels:

- CJK kana/hanzi: about `1.0` unit each.
- Vietnamese/Latin letter or digit: about `0.55–0.60` unit.
- Space/punctuation: about `0.3–0.4` unit.

For a source line up to roughly 8 CJK-width units, aim for:

`target_width <= max(5.0, source_width * 1.55 + 0.5)`

This is a heuristic, not permission to fill the entire budget. Shorter is usually better.

Examples:

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

## Canonical overrides

`glossary/ui_overrides.json` contains reviewed key-level and legacy exact-text fixes. The release/aggregation pipeline reapplies these after worker output, so a later batch cannot accidentally regress a reviewed screen.

Do not delete or expand an override without screenshot evidence that the replacement fits better.

## Worker QA before persisting

For every short `localize` entry:

1. identify whether it is a label/action rather than prose;
2. consult `glossary/ui_short_forms.json`;
3. compare visual width to the source line;
4. remove redundant context and slash compounds;
5. ensure the source newline count is unchanged;
6. prefer the shortest natural Vietnamese wording that preserves the action/mechanic.

If uncertain between a literal long label and a compact clear label, choose the compact clear label.

## Screenshot QA

A release-quality UI pass should check at least Home, Menu, Gacha, Training, Support/Card details, Shop/Exchange, Missions, Race entry, Profile, and common dialogs on Android and Windows.

Reject a UI string when it:

- protrudes outside its control;
- overlaps an icon, badge, counter, or neighboring label;
- wraps to an extra line not present in the source;
- clips Vietnamese diacritics;
- becomes visibly smaller than neighboring labels because best-fit had to shrink it too far;
- leaves raw Chinese/Japanese that is supposed to be translated.

When a screenshot exposes a recurring fixed-control problem, add a reviewed override instead of repeatedly hand-fixing generated output.
