# Canonical finding hardening — `麗走一直！ラーメン道`

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T210600Z`

Finding: `cf-2f9d7a7320e1c5db`

## Verified identity

The live finding is the exact category-147 Skill title `丽影飞驰！拉面道`. Fresh JP verification identifies Fine Motion's corresponding Skill as `麗走一直！ラーメン道`. The zh-CN title preserves the same graceful-running / ramen-path motif and is the repository's primary compression/style reference for Vietnamese Skill naming.

Following `glossary/skill_name_style.json`, the canonical Vietnamese title is `Lệ Ảnh Phi Trì! Đạo Ramen`: compact, title-like, faithful to the zh-CN motif, and guarded by the verified JP identity. The historical `Bóng đẹp phi nhanh! Đạo Ramen` is prose-like and is rejected.

## Hardening implemented

- `scripts/harden_reisou_ichoku_ramen_do_finding.py`
  - zh-CN alias `丽影飞驰！拉面道`
  - JP title `麗走一直！ラーメン道`
  - locked target `Lệ Ảnh Phi Trì! Đạo Ramen`
  - historical target `Bóng đẹp phi nhanh! Đạo Ramen` forbidden
  - exact matching in `text_data_dict.json`, category prefix `147`
  - review lock `audit.finding.fine-motion-reisou-ichoku-ramen-do`.
- `tests/test_reisou_ichoku_ramen_do_finding_hardening.py`
  - idempotence
  - canonical + review resolution over an existing defer
  - active-finding clearance
  - exact/source-path/category non-overmatch.

Implementation commits:

- hardener: `93cc436c608487d1c2bd0f02458018e258c8738e`
- regression test: `97c2a6ad939dfcf8f181fc4f728d8d9c236a3586`

## Production acceptance

- Validate run `34060057600`: success, including repository pytest and `tlvi validate`.
- Production Sync translation context run `34060057638`: success, including all finding hardeners and context-pipeline tests.
- Generated live main after Sync observed at `81f780dc2a9adaf1cc3f86c31a012902ca8e27f7`.
- Live `cf-2f9d7a7320e1c5db` resolves to locked term `reviewed.skill_name.858afd324e21` with target `Lệ Ảnh Phi Trì! Đạo Ramen` and review decision `audit.finding.fine-motion-reisou-ichoku-ramen-do` action `lock`.
- `active_findings` no longer returns this finding; active canonical blockers reduced from 151 to 150.

## Status

Accepted complete. This finding increments the shared maintenance completed count from 157 to 158. Re-route from live state after recording completion.
