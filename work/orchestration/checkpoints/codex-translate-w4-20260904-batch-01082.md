# Translation worker checkpoint

- Worker: `codex-translate-w4-20260904`
- Mode: normal pinned-corpus translation (review cap full)
- Epoch: `zhcn-67f8551f7780`
- Batch: `batch-01082-s02`, 20 entries (`entry_index` 40–59)
- Result: `work/parallel/zhcn-67f8551f7780/results/b0010/batch-01082-s02.json`
- Completion marker: `work/parallel/zhcn-67f8551f7780/completed/b0010/batch-01082-s02.json`
- Validation: pinned source identity, numeric-token preservation, completion-marker schema, structural QA, and persistent quality guard passed for all 20 entries.
- Claim: published as an active live-main claim before translation; result and completion marker are ready for the aggregator.
- Publication rule: workers do not aggregate locally; aggregator owns `localized_data` updates.
