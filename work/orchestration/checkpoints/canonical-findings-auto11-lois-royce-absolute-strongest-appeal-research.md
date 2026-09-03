# Canonical finding research: 絶対最強☆アピール宣言！

Finding: `cf-3c9ba1f70a4d56b7`

- zh-CN alias: `绝对最强☆展现宣言！`
- Repository locator: `47:101031`
- Verified JP title: `絶対最強☆アピール宣言！`
- Character: Royce and Royce / ロイスアンドロイス [Inspiring Genius]
- Proposed canonical Vietnamese target: `Tuyên Ngôn Phô Diễn☆Tuyệt Đối Mạnh Nhất!`
- Historical target observed in inheritance text: `Tuyên ngôn trình diễn☆tuyệt đối mạnh nhất!`

## Evidence

Repository curation had deferred this Skill solely because locator `47:101031` lacked verified Japanese wording. Current JP gameplay references (GameWith and Game8) independently identify Royce and Royce's unique Skill exactly as `絶対最強☆アピール宣言！`. A 4Gamer character introduction also describes Royce and Royce as especially skilled at `自己演出` (self-presentation), supporting the performative/self-promotional nuance of `アピール` rather than treating it as a generic stage performance.

The zh-CN alias `绝对最强☆展现宣言！` is therefore a direct localized bridge to the verified JP Skill. Vietnamese `Phô Diễn` preserves the deliberate self-presentation/appeal nuance more closely than the historical `trình diễn`, while `Tuyên Ngôn` preserves `宣言`. Keep the playful `☆` and final exclamation. Normalize individual Skill-title capitalization.

## Scope decision

Canonicalize only the complete Skill-title alias, scoped to `text_data_dict.json`, using `contains` because the live finding is embedded inside category-172 inheritance descriptions. Do not create generic rules for `绝对最强`, `展现`, or `宣言` independently.

Next: implement a finding hardener and regression using the accepted category-172 inheritance pattern, then require Validate + production context sync + refreshed live review-plan acceptance before incrementing maintenance completion accounting.
