# Canonical finding implementation checkpoint — ごぼう抜き

Finding: `cf-9b54f5a3c1dcb88f`
Source bridge: `一跃而上`
Pinned Skill: `202852`
JP identity: `ごぼう抜き`
Canonical target: `Vượt một mạch`

## Evidence

- Existing pinned curation identifies Skill `202852` as Japanese `ごぼう抜き` and explicitly marks zh-CN `一跃而上` as not title-equivalent.
- Current Umamusume skill references independently identify Skill `202852` as `ごぼう抜き`; it is the lower Skill upgrading to `一網打尽`.
- Japanese dictionary definitions for racing use `ごぼう抜き` for passing several competitors successively / in one sweep.
- The repository already locks the upgraded `一網打尽` as `Tóm gọn một mẻ`; the lower title should likewise preserve the racing idiom rather than the Chinese bridge calque.

External verification used during maintenance:
- https://umamusu.wiki/Game%3ASkills/202852
- https://gamewith.jp/uma-musume/article/show/435237
- https://www.kanjipedia.jp/kotoba/0001420600
- https://kotobank.jp/word/%E7%89%9B%E8%92%A1%E6%8A%9C%E3%81%8D-504200

## Implementation

- `scripts/harden_gobounuki_finding.py` at commit `d0a90e749375415010c8c63c031c9997376518a3`.
- `tests/test_gobounuki_finding_hardening.py` at commit `3f2dd50af6b5ec4d5d6d6a111de560dfcd280116`.
- Exact rule scoped to `text_data_dict.json` category `147`.
- Canonical target is `Vượt một mạch`; historical `Vọt thẳng lên` is forbidden.
- Negative tests reject other categories and prose overmatch.

Acceptance remains pending production Validate/Sync and a refreshed review plan proving `cf-9b54f5a3c1dcb88f` is no longer active.
