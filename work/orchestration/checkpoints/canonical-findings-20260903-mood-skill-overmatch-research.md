# Canonical findings maintenance research — 干劲十足 Skill-title overmatch

Claim: `canonical-findings-maintenance-auto11-20260903T082829Z`

Live review plan `tr-p3-67f8551f7780-72a4da558038-b5c0bcb3bd-556cac99d6` exposes active finding `cf-d91595f0ee324d4a` on exact `text_data_dict.json` source text `干劲十足`. The item is a Skill title under category/path prefix `147`, while embedded generic Mood context also matches the shorter bridge alias `干劲` and incorrectly requires player-facing state term `Mood`.

Repository curation evidence independently identifies `干劲十足` as JP Skill title `意気込み十分`, not the generic Mood state. Historical curated targets include `Khí thế tràn đầy` and `Tràn đầy quyết tâm`; therefore this finding should resolve the **context overmatch** first and must not blindly normalize the Skill title to `Mood`.

Required hardening direction:

- keep the finding exact to full source `干劲十足` in `text_data_dict.json`;
- exclude this exact Skill-title context from generic `干劲` / Mood source-bridge matching;
- preserve the separate Skill-title canonical decision rather than using the state-term target;
- add a regression proving generic Mood contexts still match `干劲`, while this exact Skill title does not inherit `Mood`.

Do not select between the conflicting historical Vietnamese Skill-title variants from stale curation artifacts without checking the current canonical Skill registry/locked source. The immediate systemic defect is the generic Mood overmatch, and the next continuation step is to inspect the live Skill-name canonical source for JP `意気込み十分` before writing the resolver/hardener.