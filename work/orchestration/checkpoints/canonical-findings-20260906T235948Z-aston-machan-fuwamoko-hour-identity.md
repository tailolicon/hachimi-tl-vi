# Canonical finding identity checkpoint — ふわもこアワー

Finding: `cf-3236b7b35703be33`
Claim: `canonical-findings-maintenance-gpt56sol-chat-20260906T235044Z`
Worker: `gpt56sol-chat-20260907-0642-maintenance`

## Verified repository linkage

- The live finding is the exact Skill-title source `轻柔软绵时光`, scoped to `text_data_dict.json` category `147` rows `10870201` / `10870202` / `10870203`.
- Existing curation pins that source to Skill ID `110871` and explicitly deferred because the exact JP source had not yet been established.
- Character code `1087` is canonically Aston Machan; `108702xx` is the second outfit and is distinct from first-outfit `108701xx` / `Silent letter`.

## Fresh JP identity evidence

- U-tools direct Skill-ID page `https://xn--gck1f423k.xn--1bvt37a.tools/skills/110871` identifies Skill `110871` as `ふわもこアワー` (`フワモコアワー`) and links it to Valentine Aston Machan / card `108702`, `[溶けない砂糖菓子] アストンマーチャン`.
- GameWith `https://gamewith.jp/uma-musume/article/show/483299` independently identifies `ふわもこアワー` as Aston Machan (Valentine)'s unique Skill.
- The effect text on both JP references matches the expected short-distance mid-race forward-position speed Skill, providing an additional identity cross-check.

## Canonical decision for implementation

Use exact JP display title `ふわもこアワー` as the canonical target for this JP-only proper-name Skill. This follows the repository's established handling for verified JP-only stylized unique Skill titles (for example `もちっと・ハレハレ`): preserve the exact JP identity rather than retaining a zh-CN-derived Vietnamese semantic calque or inventing an English title.

Historical exact-title rendering `Khoảnh khắc mềm mại êm ái` must not remain accepted for this Skill. Do not reuse `Silent letter`. Do not edit `localized_data/**` directly; harden the canonical layers and let the normal generation/sync pipeline propagate the result.
