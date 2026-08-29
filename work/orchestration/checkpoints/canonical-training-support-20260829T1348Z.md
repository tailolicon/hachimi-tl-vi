# Training / Support canonical hardening checkpoint — 2026-08-29T13:48Z

Task: `canonical-training-support`
Stage: `domain_work`
Branch: `canonical-training-support-hardening`

## Continued scope

Resumed from `canonical-training-support-20260829T1321Z.md`; did not restart inventory. Prior validated Friendship Training, Support Pt, Energy, Friendship Gauge, Training Level, Failure Rate, and Support Effects hardening remains intact.

## New canonical decisions and permanent coverage

Added exact-key community hardening for the remaining Career stat-limit / max-Energy labels observed in the retrospective corpus:

1. `SingleMode400100` / `{0}的上限已<color=#FF6D26>达到极限</color>` requires the established player term `Stat Cap`.
2. `SingleMode400102` / `{0}的上限` requires `Stat Cap`.
3. `SingleMode400103` / `体力最大值` requires `Max Energy`, consistent with the already-hardened `Energy` system term.

Historical calques such as `Giới hạn của`, `giới hạn tối đa`, and `Thể lực tối đa` are forbidden only in these exact localize keys. Generic story prose about limits, maximum values, physical stamina, etc. remains outside the rule.

Permanent implementation changed:

- `scripts/harden_training_support_labels.py` — commit `553f3e41cbb2dbc2ed3ed8e4ce0b409535300134`
- `tests/test_training_support_labels_hardening.py` — commit `0d0aba88861fe738692299f5285a3b4ec5b30e5b`

No `localized_data/**` files were edited.

Terminology evidence: current established Umamusume community documentation consistently calls per-stat upper bounds `Stat Caps`, while scenario/training documentation uses `Energy` as the training resource. The repository rule is intentionally exact-key scoped rather than a global alias.

## Validation evidence

Local container Git access failed with DNS resolution for `github.com`; per the execution-backend rule this was not treated as a task blocker. Validation continued through GitHub Actions run `33255884360`, job `99109386381` at branch head `6d89b349bbe216b3321ddc84bcb08eee551e7660`.

Results:

- focused Training/Support regressions: `20 passed in 0.14s`;
- full pytest: `187 passed in 1.52s`;
- `tlvi --db /tmp/tlvi.db validate`: `ok: true`, no errors/warnings;
- `tlvi --db /tmp/tlvi.db index --out /tmp/index.json`: `ok: true`, 8 files;
- hardener generated a `ui_community_terms.json` delta of 75 insertions.

The generated glossary delta was validated but is not materialized by the read-only validation workflow; a later domain checkpoint/finalization must run the permanent hardener and commit the generated glossary before integration.

## Remaining domain work — do not advance orchestration yet

The Training / Support domain remains `domain_work`. Continue from here with:

1. classify remaining Bond/Friendship variants before adding any aliases; never restore a global bare-bond lock;
2. inspect remaining facility/training-level variants;
3. inspect repeated training-result/status labels and stat-gain/bonus wording not covered by the exact stat-cap rules;
4. materialize the validated 75-line community glossary delta before final integration.

Only after the remaining substantive domain work and permanent regression coverage are complete should the task move to `ready_for_finalize`.
