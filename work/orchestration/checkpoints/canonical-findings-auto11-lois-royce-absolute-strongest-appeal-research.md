# Canonical finding implementation: 絶対最強☆アピール宣言！

Finding: `cf-3c9ba1f70a4d56b7`

- zh-CN alias: `绝对最强☆展现宣言！`
- Repository locator: `47:101031`
- Verified JP title: `絶対最強☆アピール宣言！`
- Character: Royce and Royce / ロイスアンドロイス [Inspiring Genius]
- Canonical Vietnamese target: `Tuyên Ngôn Phô Diễn☆Tuyệt Đối Mạnh Nhất!`
- Historical target: `Tuyên ngôn trình diễn☆tuyệt đối mạnh nhất!`

## Evidence and scope

Repository curation had deferred locator `47:101031` only because its JP wording was unverified. Current JP gameplay references (GameWith and Game8) independently identify Royce and Royce's unique Skill exactly as `絶対最強☆アピール宣言！`; 4Gamer character material describes Royce and Royce as especially skilled at `自己演出` (self-presentation), supporting the performative/self-promotional nuance of `アピール`.

Canonicalize only the complete Skill-title alias in `text_data_dict.json`, using `contains` for category-172 inheritance descriptions. `Phô Diễn` preserves the deliberate self-presentation nuance better than generic `trình diễn`; keep `☆`/`!` and normalize Skill-title capitalization. Do not generalize component words.

## Implementation

- Hardener: `scripts/harden_lois_royce_absolute_strongest_appeal_finding.py`, commit `a882b7637d1880298bdcc760867ca90055498884`.
- Regression: `tests/test_lois_royce_absolute_strongest_appeal_finding_hardening.py`, commit `de782da768037bf93aed04af4bcf1f805dbfff8c`.
- Community rule: `skill.lois_royce.absolute_strongest_appeal`.
- Terminology decision: `audit.finding.skill-lois-royce-absolute-strongest-appeal`.
- Regression proves production-shape resolution, idempotence, longer inheritance-text coverage, and no resolution in `localize_dict.json`.

## Acceptance complete

Acceptance was verified against live `main` after production synchronization:

- Validate run `33812964057`: `completed/success`.
- Sync translation context run `33812964043`: `completed/success`.
- Sync translation review plan run `33812964020`: `completed/success`.
- Refreshed active review plan: `tr-p3-67f8551f7780-85802ab3af81-b5c0bcb3bd-14006a3bf2`.
- Live batch `...-b0213` embeds `skill.lois_royce.absolute_strongest_appeal` for `绝对最强☆展现宣言！`, with preferred target `Tuyên Ngôn Phô Diễn☆Tuyệt Đối Mạnh Nhất!` and `canonical_findings: []`.

Finding `cf-3c9ba1f70a4d56b7` is therefore accepted on live `main` and may count as one completed canonical-maintenance unit.
