# Canonical finding acceptance: ¡Qué alegría!

- Finding: `cf-e5e3ab3fd5da256c`
- zh-CN source: `可喜可贺大欢声！`
- JP player-facing title: `¡Qué alegría!`
- Character: Gran Alegria (`[すまいる・まい・うぇい！] グランアレグリア`)
- Locked target: `¡Qué alegría!`

## Evidence

The live retrospective review plan embedded `cf-e5e3ab3fd5da256c` as an open proper-name finding for the Skill title `可喜可贺大欢声！` in `text_data_dict.json` category 147. Public JP/community references identify Gran Alegria's unique Skill as `¡Qué alegría!`; the Chinese skill reference explicitly pairs `¡Qué alegría!` with `可喜可贺大欢声！`. Because the JP player-facing title is already Spanish, preserving it verbatim avoids translating a proper name through zh-CN.

References checked during implementation:
- https://umamusu.wiki/Game:Skills/101311 — `¡Qué alegría!`, unique Skill for `[smile my way!] Gran Alegria`, JP-only.
- https://wiki.biligame.com/umamusume/%C2%A1Qu%C3%A9_alegr%C3%ADa%21 — pairs `¡Qué alegría!` with `可喜可贺大欢声！`.

## Durable implementation

- `scripts/harden_que_alegria_finding.py` — commit `0abd7a6b53b095bfe34b965f8dc76d4d5b9afb47`
  - adds exact community canonical term `skill.que_alegria`;
  - adds explicit review lock `audit.finding.skill-que-alegria`;
  - scopes matching to exact `text_data_dict.json` title;
  - adds `¡Qué alegría!` to finding suggestions.
- `tests/test_que_alegria_finding_hardening.py` — commit `61490279b6a7e198c03d8eedf1584729d6103284`
  - verifies idempotence;
  - verifies canonical/review resolution makes the synthetic live-shape finding non-actionable;
  - verifies exact scoping does not overmatch longer source text or another file.

## Production acceptance

- Validate/test run `33879556413`: success.
- Sync translation context run `33879556397`: success; published `c020f326d08765ca62bcc7b4fb62702e20f0db9b`.
- Production ledger now has `canonical_resolution = skill.que_alegria -> ¡Qué alegría!` and `review_resolution = audit.finding.skill-que-alegria / lock`; `open_canonical_findings` decreased from 145 to 144.
- Sync translation review plan run `33879556401`: success.
- Regenerated active plan `tr-p3-67f8551f7780-bcb50de94ac3-b5c0bcb3bd-d968acad86` contains no occurrence of `cf-e5e3ab3fd5da256c`.

Acceptance complete. This finding counts as one newly completed maintenance unit.
