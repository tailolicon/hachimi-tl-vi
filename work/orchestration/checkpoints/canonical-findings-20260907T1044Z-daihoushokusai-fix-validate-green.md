# Canonical findings maintenance checkpoint — Daihoushokusai stale-scope fix validated

Finding: `cf-5310cb8fbcc8798f` (`大丰食祭`)

- Root-cause fix commit: `02eac50d6edaaba6285411916c4e1f6190f8c214`.
- Regression commit: `1a96b6af8ed6aedfc8380e3bf2afd49cb1587099`.
- Validate workflow run `34112783655` for the regression head completed successfully.
- Production Sync translation context run `34112783646` is queued/pending.
- Sync translation review plan run `34112783620` is queued/pending.
- To avoid waiting on only one queued production run, the previously accepted Sync-context job was also re-run as attempt 3 of run `34110827740`; it is currently pending and will checkout live `main` when a runner starts.
- `completed_count` remains 190. Live acceptance still requires a non-null canonical resolution for `cf-5310cb8fbcc8798f`, absence from `active_findings()`, and then an unchanged successful Context Sync that emits `Context is already current.`.
