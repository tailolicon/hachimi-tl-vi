# Canonical finding completion — regenerated 超长距离 context guard

Claim: `canonical-findings-maintenance-auto11-20260903T082829Z`
Finding: `cf-9f625a03a4f08c41`

This was not a new terminology decision. It was a regenerated finding ID for the already-hardened generic `长距离` -> `Long` matcher overmatching the distinct `超长距离...` Skill compound.

Completed systemic resolution:

- retained the existing `common.distance.long` exclusion for `超长距离`;
- added post-refresh resolver `resolve_regenerated_super_long_distance_context_finding.py` that checks every durable evidence row against the live matcher and only writes a context-guard resolution when the old `Long` overmatch is truly absent;
- added regression proving the resolver refuses to close the finding before the hardener is applied and resolves it only afterward;
- wired the resolver after canonical refresh in Sync translation context.

Validation/publication evidence:

- Validate run `33737494279` completed successfully;
- Sync translation context run `33737494611` completed successfully;
- generated context commit `d496a96036bea8d5c8434c6d473ddaa00c97ac63` is on main;
- downstream live review plan `tr-p3-67f8551f7780-e0ccd58c88ff-b5c0bcb3bd-2fdb136a6b`, generated `2026-09-03T09:15:24.636968Z`, contains no occurrence of `cf-9f625a03a4f08c41`.

This regenerated finding is durably resolved and may be counted complete.