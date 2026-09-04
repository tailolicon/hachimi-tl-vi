# Canonical finding implementation checkpoint: いずれあなたに咲くフローラ

- Finding: `cf-fdc79513437ad3e5`
- zh-CN source: `终将为你绽放的花神`
- JP player-facing title: `いずれあなたに咲くフローラ`
- Character: Curren Bouquetd'or (`[花宿しのクチュール] カレンブーケドール`, character ID 1134)
- Proposed/locked Vietnamese target: `Flora rồi sẽ nở vì bạn`

## Evidence

The regenerated live review plan embeds this source as an open proper-name Skill finding in `text_data_dict.json` category 147. Current JP references for the playable Curren Bouquetd'or released 2026-06-15 identify her unique Skill as `いずれあなたに咲くフローラ`. The existing Vietnamese `Nữ thần hoa rồi sẽ nở vì bạn` converts the player-facing proper noun `フローラ` (Flora) into a generic noun phrase, losing the title identity.

References checked during implementation:
- https://playershi.com/uma_character/all/113401-currenbouquetdor/ — character ID 113401 and unique Skill `いずれあなたに咲くフローラ`.
- https://gamewith.jp/uma-musume/article/show/563843 — current Skill page identifies `いずれあなたに咲くフローラ` as Curren Bouquetd'or's unique Skill.
- https://www.inside-games.jp/article/2026/06/14/182940.html — confirms the playable `[花宿しのクチュール] カレンブーケドール` release on 2026-06-15.

## Durable implementation

- `scripts/harden_curren_bouquetdor_flora_finding.py` — commit `64082866b780b21798c2be09a846766d003cb742`
  - adds exact community canonical term `skill.curren_bouquetdor.flora`;
  - locks `Flora rồi sẽ nở vì bạn` and forbids the current identity-losing `Nữ thần hoa rồi sẽ nở vì bạn`;
  - adds explicit review lock `audit.finding.skill-curren-bouquetdor-flora`;
  - scopes matching to the exact title in `text_data_dict.json`.
- `tests/test_curren_bouquetdor_flora_finding_hardening.py` — commit `03e013e25e1d3ba32cf6ec9ffff9ebf300632d67`
  - verifies idempotence;
  - verifies canonical/review resolution removes the synthetic live-shape finding from `active_findings`;
  - verifies exact scoping does not overmatch longer source text or another file.

## Pending acceptance

Do not increment maintenance `completed_count` until Validate, Sync translation context, and Sync translation review plan succeed and regenerated live state proves `cf-fdc79513437ad3e5` is nonblocking.
