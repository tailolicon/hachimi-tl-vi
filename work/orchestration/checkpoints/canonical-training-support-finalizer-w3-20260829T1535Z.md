# Training/Support finalization W3 checkpoint

- Live Training/Support integration is already on `main` at `75a505e824f6e88f6f72cad25376999333c4046f`.
- Validate workflow run `33258276615` completed successfully for that integration commit.
- Production `Sync translation context` run `33258276616` originally failed at `apply_terminology_reviews.py` because the locked registry is internally conflicting for JA `ラジオNIKKEI賞`.
- W3 reran the sync job (attempt 2). The rerun checked out live `main` at `1732a86f72a62e257e26ca03ff4f8fa9019e94ce` and reproduced the same exact conflict, proving this is a live pre-existing Race canonical blocker rather than transient workflow failure.
- Training/Support hardening itself has scoped regression coverage: category-155 `羁绊值` maps to `Friendship Gauge`, `progress.bond` is not matched there, and bare bond prose outside the scoped source/path does not match the Friendship Gauge rule.
- Do not mark Training/Support complete until the Race lock conflict is resolved and production Sync + unchanged second Sync no-op proof complete successfully.
- Next finalizer should preserve the integrated Training/Support work, fix/resolve the `ラジオNIKKEI賞` registry conflict canonically (not by patching localized examples), rerun Sync, then continue required spot checks and orchestration transition.
