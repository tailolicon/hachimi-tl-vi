# Canonical findings maintenance research — 会心の一歩

Claim: `canonical-findings-maintenance-gpt56sol-20260903T074300Z`

Finding `cf-07a7131770d2b792` is an active exact proper-name blocker for zh-CN `会心一步` in `text_data_dict.json`. Repository curation maps it to Skill ID `202712`, JP **`会心の一歩`**. Current Vietnamese is **`Bước quyết tâm`**.

## Repository evidence

- `work/curation/results/term-0014/claim-fb03cfe69b6848b7b60ec688a52ddf34.json` verifies Skill ID 202712 / JP `会心の一歩` and previously deferred only because the project had not settled the nuance of `会心`.
- Review snapshots place the title in `text_data_dict.json`, category `147`; the canonical finding itself is already `match_mode: exact`, so hardening can remain narrow.
- `glossary/skill_name_style.json` prefers compact, commercial-game skill titles and permits concise Hán-Việt wording where it is intelligible and faithful.

## Fresh semantic evidence

Current JP references confirm the identity and its Skill family:
- https://gamewith.jp/uma-musume/article/show/413769 — `会心の一歩`, normal Skill, upper Skill `王手`.
- https://game8.jp/umamusume/546716 — same Skill/effect and upper Skill `王手`.

Japanese dictionary evidence for `会心`:
- https://dictionary.goo.ne.jp/word/%E4%BC%9A%E5%BF%83/ — `心にかなうこと。期待どおりにいって満足すること` (something goes as hoped / to one's satisfaction), with a secondary sense of understanding/mastery.
- https://kotobank.jp/word/%E4%BC%9A%E5%BF%83-457651 — same core meaning: matching one's intention and giving satisfaction.

Therefore **`Bước quyết tâm` is a semantic error**: Vietnamese `quyết tâm` corresponds determination/resolve, while JP `会心` describes satisfaction/being exactly to one's liking. The gameplay relation to `王手` also supports a deliberate, well-landed step rather than an emotional resolve.

## Canonical decision

Use **`Bước Chân Đắc Ý`**.

Rationale:
- `Đắc ý` directly captures the JP sense of a result/move that goes exactly as intended and gives satisfaction.
- `Bước Chân` naturally renders `一歩` as a Skill title rather than a sentence.
- The four-unit title is compact and readable in Vietnamese, matching the repository's skill-name style better than a literal explanatory gloss.
- It avoids inventing an official English title; current English-oriented databases still mark this Skill as JP-only.

Hardening should add an exact source alias `会心一步`, target `Bước Chân Đắc Ý`, forbid `Bước quyết tâm`, scope to `text_data_dict.json` category `147`, add a terminology-review lock carrying JP `会心の一歩`, and add positive/negative resolver regressions.
