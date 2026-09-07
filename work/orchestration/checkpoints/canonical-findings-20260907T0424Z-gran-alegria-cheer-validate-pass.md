# Canonical finding checkpoint — Gran Alegria cheer prose validation passed

- Finding: `cf-46e2b74188810a3f` (`放声欢呼` false-positive inside ordinary prose).
- Hardening commit: `1e6535627e39d3016d9e9c0aaf0145b3b6af87dc`.
- Regression test commit: `d69d39668050977b5f1618413155e908bcc17709`.
- The hardener adds an exact full-source exclusion to `character.gran_alegria` for the offending prose only, plus an explicit `ignore` review decision for this context-rule finding. It does not remove the verified `放声欢呼 -> Gran Alegria` identity alias globally.
- Regression coverage proves the exact prose no longer produces a locked Gran Alegria match, while a genuine identity string `[特雷森学园]放声欢呼` still resolves to `Gran Alegria`; the hardener is idempotent.
- Validate run `34082785723` completed successfully on the regression-test commit.
- Production Sync run `34082776208` is in progress. At checkpoint time restore/apply/audit hardening succeeded and the normal finding-hardener pass was running.
- Do not mark the finding complete until production Sync succeeds, the live regenerated ledger no longer returns this finding from `active_findings`, the genuine identity alias remains functional, and a subsequent unchanged production Sync succeeds.
