# Training / Support canonical hardening checkpoint — 2026-08-29T13:10Z

Task: `canonical-training-support`
Stage: `domain_work`
Branch: `canonical-training-support-hardening`

## Continued scope

Resumed from `canonical-training-support-20260829T1225Z.md`; did not restart the domain inventory. The prior validated Friendship Training, Support Pt, Energy, and scoped Friendship Gauge work remains intact.

## New canonical decisions and permanent coverage

Added exact, item-scoped hardening for two remaining player-facing Training UI labels whose current retrospective corpus text still used historical Vietnamese calques:

1. `Outgame352008` / `训练等级` -> `Training Level`
   - exact `localize_dict.json` key/path scope;
   - historical `Cấp huấn luyện` is forbidden by the community guard;
   - generic story prose about training or levels does not match.

2. `SingleMode0036` / `失败率` -> `Failure Rate`
   - exact `localize_dict.json` key/path scope;
   - historical `Tỷ lệ thất bại` is forbidden by the community guard;
   - generic narrative failure wording does not match.

Permanent implementation:

- `scripts/harden_training_support_labels.py`
- `tests/test_training_support_labels_hardening.py`
- materialized canonical glossary commit: `b10f641337c222dabf5e3d18f2c35a727f196648`

No `localized_data/**` files were edited.

## Validation evidence

The local shell path could not resolve `github.com`; per `work/worker_session_policy.json`, validation continued through the repository GitHub Actions execution path instead of treating one backend failure as a task blocker.

Temporary validation workflow run `33254221971` passed at head `a9a89631964160be1776b40bfac181aae4838023`:

- focused Training/Support regressions: `14 passed in 0.11s`;
- full pytest: `181 passed in 1.09s`;
- `tlvi --db /tmp/tlvi.db validate`: `ok: true`, no errors/warnings;
- `tlvi --db /tmp/tlvi.db index --out /tmp/index.json`: `ok: true`, 8 files;
- generated glossary delta for the two new labels: 99 insertions across `term_registry.json` and `ui_community_terms.json`.

A second successful workflow run `33254249941` validated the same branch changes and durably materialized the generated glossary as commit `b10f641337c222dabf5e3d18f2c35a727f196648`.

The temporary workflow was then removed; cleanup commit: `554f000c38127cbcc5496ab0c929463500eea323`.

## Remaining domain work — do not advance orchestration yet

The Training / Support domain is still `domain_work`. Continue from this checkpoint with:

1. generic Support Effect system labels and repeated support-effect result/status wording;
2. stat gain / bonus / cap / limit terminology specifically in Training/Support contexts;
3. classify any remaining Bond/Friendship variants before adding aliases; never restore a global bare-bond lock;
4. inspect for any additional facility/training-level variants before declaring the level vocabulary complete.

Only after the remaining substantive domain work and permanent regression coverage are complete should this task move to `ready_for_finalize`.
