# Canonical finding research — 灯穗 / Inari One unique skill

Finding: `cf-3a460c751596bfac`

## Live repository state

- `scripts/canonical_findings.py::active_findings` treats this row as blocking because it is `open`, has `canonical_resolution: null`, and its review decision is `defer`.
- Source scope: `text_data_dict.json`, category/path prefix `172`, `match_mode: contains`.
- Existing curation evidence identifies the underlying Skill as `47/110341` and explicitly deferred it because no verified Japanese alias/stable target was available at that time.
- Current translated inheritance text renders the title as `Bông lúa ánh sáng`, but that is not sufficient evidence for a canonical lock.

## Fresh identity evidence

- Biligame/BWIKI skill page: https://wiki.biligame.com/umamusume/%E7%81%AF%E7%A9%82
  - identifies the JP title as `灯穂` and the Simplified Chinese title as `灯穗`;
  - its effect text matches the live inheritance Skill identity.
- umamusu.wiki Skill ID page: https://umamusu.wiki/Game%3ASkills/110341
  - directly maps Skill ID `110341` to JP `灯穂`;
  - identifies it as the unique Skill for `[夢ノ金原] Inari One`.
- Game8 and GameWith independently identify `灯穂` as the unique Skill belonging to the alternate Inari One.

This resolves the JP identity of the source, but not the player-facing English/Vietnamese canonical target.

## Global/community check

- Current community Global datasets expose the alternate outfit as `Fields of Gold`, but the Skill page itself is still marked JP-only and does not expose an official Global Skill title.
- One English community article renders the Skill as `Lantern`, but a single secondary translation is not strong enough to override the repo's evidence-first policy for a named player-facing Skill.
- Community Global schedule data indicates `Fields of Gold` Inari One is imminent, so an official Global Skill title may become directly verifiable shortly. Do not pre-empt that with a guessed lock.

## Decision

Keep `cf-3a460c751596bfac` unresolved/deferred. Do **not** lock `Bông lúa ánh sáng`, `Lantern`, `Tosui/Tōsui`, or another semantic/romanized target without stronger player-facing evidence.

Recommended continuation: re-check official/current Global game data for `[Fields of Gold] Inari One` once that content is live; if an official Global Skill title exists, use it as the preferred canonical target and implement the normal hardener + regression + production Validate / Sync translation context / Sync translation review plan gates. If Global still lacks the Skill, seek at least two independent established English/Vietnamese community renderings before considering a community lock.

Maintenance `completed_count` remains 88 because this is a research checkpoint, not a production-accepted resolution.
