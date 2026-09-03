# Canonical finding accepted: Turf surface context

- Finding: `cf-b5b4efe029e4fb75`
- zh-CN source alias: `草地`
- Canonical gameplay target: `Turf`
- Implementation checkpoint: `work/orchestration/checkpoints/canonical-findings-20260903-turf-surface-context-implementation.md`

## Final accepted shape

- Base `common.surface.turf` retains JP `芝` and no longer broadly matches zh-CN `草地`.
- `common.surface.turf.zhcn` handles standalone `草地` with `match_mode: exact`, preventing narrative grass/grassland prose from being normalized to the racing-surface label.
- `common.surface.turf.aptitude` preserves the known composition `SingleMode0078 / 草地适性 / Turf Aptitude` with a narrow `localize_dict.json` + exact-key scope instead of restoring a global substring matcher.
- `audit.finding.turf-surface-zhcn-context` supplies the explicit review lock.

## Acceptance evidence

- The first production context-sync attempt correctly rejected an integration regression in `草地适性` (`1 failed, 570 passed`), so that implementation was not accepted.
- The corrected scoped-composition implementation was exercised by production context sync run `33787710136`; all finding hardeners ran and the full context test gate completed with **572 passed**.
- That successful workflow committed and safely rebased generated context onto `main` as `94d3e8f84aa9bdfbb91bbf22544ff40063892839`.
- Live generated `glossary/ui_community_terms.json` contains both `common.surface.turf.zhcn` and `common.surface.turf.aptitude`, while the base Turf rule carries only JP `芝`.
- Live routing subsequently regenerated to plan `tr-p3-67f8551f7780-8e23c3422de6-b5c0bcb3bd-07702278e0`; code search scoped to that plan identity plus `cf-b5b4efe029e4fb75` returns no matching blocker rows.
- The generated context commit was pushed by the repository workflow using `GITHUB_TOKEN`, so it did not emit a separate push-triggered Validate run; the authoritative production context workflow itself executed the full pytest gate after applying all hardeners and passed 572/572 tests before publishing generated context.

Acceptance conclusion: the finding is no longer an active retrospective-review blocker and counts as one completed canonical-finding maintenance unit.
