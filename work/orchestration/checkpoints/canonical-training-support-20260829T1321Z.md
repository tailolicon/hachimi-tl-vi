# Training / Support canonical hardening checkpoint — 2026-08-29T13:21Z

Task: `canonical-training-support`
Stage: `domain_work`
Branch: `canonical-training-support-hardening`

## Continued scope

Resumed from `canonical-training-support-20260829T1310Z.md`; did not restart inventory. Prior validated Friendship Training, Support Pt, Energy, Friendship Gauge, Training Level and Failure Rate hardening remains intact.

## New canonical decision and permanent coverage

Hardened the remaining generic Support Card section label found in the retrospective corpus:

- `Character0331` / `支援效果` -> `Support Effects`
- exact `localize_dict.json` key/path scope only;
- historical `Hiệu ứng hỗ trợ` is forbidden by the community guard in this exact UI context;
- generic story prose about support/effects does not match.

Permanent implementation:

- `scripts/harden_training_support_labels.py`
- `tests/test_training_support_labels_hardening.py`
- materialized canonical glossary commit: `556b9412d`

No `localized_data/**` files were edited.

Terminology evidence: the current player-facing support-card vocabulary consistently presents the section as `Support effects`; the rule is still intentionally exact-key scoped rather than global.

## Validation evidence

Temporary GitHub Actions workflow run `33254711871`, job `99106304494`, completed successfully on the task branch:

- focused Training/Support regressions: `16 passed in 0.12s`;
- full pytest: `183 passed in 1.05s`;
- `tlvi --db /tmp/tlvi.db validate`: `ok: true`, no errors/warnings;
- `tlvi --db /tmp/tlvi.db index --out /tmp/index.json`: `ok: true`, 8 files;
- hardener materialized 48 glossary insertions across `term_registry.json` and `ui_community_terms.json` and committed them as `556b9412d`.

Temporary workflow cleanup commit: `c7156f74fdbd4d71665a1459e45c22deee66d06c`.

## Remaining domain work — do not advance orchestration yet

The Training / Support domain remains `domain_work`. Continue from here with:

1. stat gain / bonus / cap / limit terminology specifically in Training/Support contexts;
2. classify any remaining Bond/Friendship variants before adding aliases; never restore a global bare-bond lock;
3. inspect for any additional facility/training-level variants;
4. inspect repeated training-result/status labels not already covered.

Only after the remaining substantive domain work and permanent regression coverage are complete should the task move to `ready_for_finalize`.
