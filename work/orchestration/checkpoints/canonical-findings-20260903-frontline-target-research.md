# Canonical findings maintenance research — 前行 / JP 前列狙い

Claim: `canonical-findings-maintenance-auto11-20260903T082829Z`
Finding: `cf-e3ab912489ddc5f5`

The current priority batch exposes exact zh-CN Skill title `前行` in `text_data_dict.json` category 147. Embedded source-bridge risk `bridge.skill.frontline_target` already verifies JP identity `前列狙い` and marks zh-CN as lossy: the JP title means aiming/targeting the front positions, not simply “moving forward”. Existing curation therefore correctly deferred the current Vietnamese `Tiến lên` rather than locking the lossy zh-CN semantics.

Fresh external identity/semantic verification on 2026-09-03:

- GameWith and Game8 both list JP Skill `前列狙い` as a normal Dirt Skill and describe its late-race effect as preparing/aiming for the front.
- Umamusume Wiki maps JP `前列狙い` to released English Skill name `Forward, March!`, Skill ID 201682, and maps its upgrade `狙うは最前列！` to `Lead the Charge!`.

This is sufficient to confirm the source bridge identity and that current `Tiến lên` is semantically too generic. It is **not** by itself sufficient to select the project’s Vietnamese canonical title, because this repository localizes individual Skill names into Vietnamese rather than mechanically adopting Global English names. Before writing a lock, inspect current Vietnamese Skill-name style and any same-family canonical wording for `狙うは最前列！` / front-position aiming. Do not guess a target from the zh-CN title.
