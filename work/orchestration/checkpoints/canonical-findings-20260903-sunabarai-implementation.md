# Canonical finding implementation checkpoint — 砂払い

Finding: `cf-81da4aef1ab84dec`
Source bridge: `洗尘`
Pinned Skill ID: `202842`
JP identity: `砂払い`
Canonical target: `Phủi cát`

## Evidence

- Repository curation had deferred `洗尘` because the exact JP title was then unverified.
- Current external skill tables independently identify Skill `202842` as JP `砂払い` and map the zh-CN title `洗尘` to that same ID.
- Current English skill data renders `砂払い` as `Dust Off`, confirming the Japanese action is brushing/removing sand/dust rather than the literary zh-CN calque represented by the old Vietnamese `Tẩy trần`.
- Repository Dirt/Sand Skill conventions already use direct natural Vietnamese titles such as `砂浴び` -> `Tắm cát`.

External verification used during maintenance:
- https://wiki.biligame.com/umamusume/%E7%BC%BA%E5%A4%B1%E6%8A%80%E8%83%BD%E5%9B%A0%E5%AD%90%E6%A3%80%E6%B5%8B%E9%A1%B5
- https://wiki.biligame.com/umamusume/%E4%B8%AD%E6%97%A5%E6%96%87%E5%AF%B9%E6%AF%94%E8%A1%A8
- https://gametora.com/umamusume/skills

## Implementation

- `scripts/harden_sunabarai_finding.py` at commit `1ec0152c0cb7cd12e373a6cdd5d233b122f658ad`.
- `tests/test_sunabarai_finding_hardening.py` at commit `064d75a0148ea3d9e5eb43ab93d3a4b3c4ab02ec`.
- Rule is exact and scoped to `text_data_dict.json` category `147`.
- Historical target `Tẩy trần` is forbidden for this Skill identity.
- Negative regression coverage prevents matching other categories or prose.

Acceptance remains pending production Validate/Sync and a refreshed review plan proving the finding is no longer active.
