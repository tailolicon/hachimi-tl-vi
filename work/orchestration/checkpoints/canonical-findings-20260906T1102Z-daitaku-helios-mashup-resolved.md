# Canonical finding — Daitaku Helios Mashup Skill resolved

Resolved active finding `cf-1c74738dc57289c2` for zh-CN `跟上我的Mashup！`.

- Existing curation pins this entity to Skill ID `110651` and had correctly deferred it because the surrounding Japanese title was not yet verified.
- Independent JP references identify Skill `110651` as Daitaku Helios [Joyful Jamboree!]'s unique Skill `ノッてけ、マッシュアップ！`.
- No official Global title was verified for this JP-only Skill, so the canonical target preserves the exact Japanese title instead of deriving a Vietnamese title from the zh-CN semantic bridge.
- Added reviewed lock `audit.finding.skill-daitaku-helios-notteke-mashup` and community rule `skill.daitaku_helios.notteke_mashup`.
- The rule is constrained to `text_data_dict.json` and matches the complete distinctive Skill title as a substring so it also resolves inheritance/Spark descriptions containing the title; it does not generalize component words.
- Ran canonical refresh followed by the full production post-refresh resolver surface. Active-finding semantics decreased from `147` to `146`.
- Regression validation after rebasing over concurrent review progress: `30 passed` across the new hardener test plus terminology/context/scoped-resolution suites.
- Canonical artifacts integrated to live `main` at commit `95c89addc9db42d85cc7069984886cbddc224c26` via non-forced fast-forward push after rebasing onto the then-live `main`.
