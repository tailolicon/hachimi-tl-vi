# Canonical finding completion — Gran Alegria cheer prose overmatch

- Finding: `cf-46e2b74188810a3f`.
- Hardening: `1e6535627e39d3016d9e9c0aaf0145b3b6af87dc`.
- Regression: `d69d39668050977b5f1618413155e908bcc17709`.
- Validate run `34082785723`: success.
- Production Sync run `34082776208`, attempt 2: success.
- Required unchanged production Sync rerun job `101622020307`: success; all context-pipeline tests passed (`797 passed`) and the publish step reported `Context is already current.`
- Live `glossary/canonical_findings.json` retains the historical row with `status: open`, but its `review_resolution` is the explicit `ignore` decision `audit.finding.gran-alegria-cheer-prose-overmatch`. By `active_findings()` semantics, an ignored review-resolution row is non-blocking.
- Regression coverage proves the exact ordinary-prose sentence no longer matches the locked Gran Alegria character term, while `[特雷森学园]放声欢呼` still resolves to `Gran Alegria`.
- This finding is production-accepted and the maintenance completed counter may advance by one.
