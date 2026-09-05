# Canonical finding evidence — 钻石桥 / ポンテ・デ・ディアマン

Finding: `cf-8758bee3b2929016`

## Live blocker

The current active review plan `tr-p3-67f8551f7780-1c10cf952358-b5c0bcb3bd-ba5642134a`, batch `b0127`, still exposes this finding as `open` / `proper_name` for `钻石桥`. The current Vietnamese text `Cầu Kim Cương` is therefore not safe to approve from the zh-CN bridge.

## Identity evidence

- Historical project curation pins `钻石桥` to Skill ID `120671` and JP title `ポンテ・デ・ディアマン`, and explicitly deferred literal translation pending canonical Roman-letter spelling.
- Current JP skill databases independently identify `ポンテ・デ・ディアマン` as Satono Diamond's `[シュヴァリエ・ブル]` unique Skill and give the same gameplay effect.
- Repository policy says zh-CN is a semantic bridge, while official Global terminology is preferred where verifiable, then official JP identity; an established Roman-letter proper-name spelling should be used only when confident.

## Bounded conclusion

Do **not** lock `Cầu Kim Cương`. The JP identity is verified, but this pass did not verify a sufficiently authoritative official/current Global localization or canonical Roman-letter spelling for `ポンテ・デ・ディアマン`. Search hits for guessed spellings such as `Ponte de Diamant` were not authoritative enough to cross the lock threshold.

Keep the finding active/deferred until an official Global player-facing title or a strong canonical Roman spelling is verified. No `localized_data/**` example was changed.