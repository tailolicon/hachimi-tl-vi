# Canonical finding research: North Flight / Arrow Line

- Finding: `cf-c78e8d766172c136`
- zh-CN source: `熠熠华丽的箭线`
- Scope: `text_data_dict.json`, category `147`
- Current Vietnamese: `Mũi tên hoa lệ rực sáng`
- Affected current-plan rows observed: three level variants under `10820201` / `10820202` / `10820203`

## Identity verification

The source is not a generic arrow phrase. Current JP data for North Flight `[水縹の一閃]` identifies character/card ID `108202` and its unique Skill as:

`煌めき華やぐアローライン`

Independent current Japanese references consulted during this maintenance unit agree on that exact Skill name, including the North Flight `[水縹の一閃]` character pages on WikiWiki/VIP Uma, U-tools, and current skill-list references.

This matters because the zh-CN bridge `熠熠华丽的箭线` semantically translates the katakana title element `アローライン`. The present Vietnamese `Mũi tên hoa lệ rực sáng` further flattens that named `Arrow Line` identity into a generic arrow phrase.

## Repository style evidence

The repository already preserves Latin/English identity for distinct Skill names where the JP title uses a distinctive foreign-name element (for example maintained `... Arrow` terms such as `Acrobat Arrow`). The live `skill_name_style` policy also prefers preserving proper-name identity over unconsciously calquing Skill titles.

## Candidate project canonical

`Arrow Line rực rỡ`

Rationale:
- preserves the explicit `アローライン / Arrow Line` identity;
- compactly captures `煌めき華やぐ` without carrying over the zh-CN calque structure;
- remains a project Vietnamese canonical and does not claim an official Global localization.

Do not harden this candidate until the currently running Aufheben sync has finished, to avoid creating avoidable workflow/concurrency churn. After that sync is validated, this candidate can use the same exact category/path-scoped hardener + regression pattern if no stronger official/project lock has appeared on live `main`.
