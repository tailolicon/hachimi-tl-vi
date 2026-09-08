# Canonical finding checkpoint — running-style sequence

Finding: `cf-6ccc81e484da5f4a` (`领放][先行][居中][追赶`)

Live evidence already has all four player-facing strategy labels in `glossary/ui_community_terms.json`: `Front Runner`, `Pace Chaser`, `Late Surger`, `End Closer`. The existing hardener `scripts/harden_running_style_sequence_finding.py` adds the missing zh-CN aliases `领放` and `居中`, and the existing regression proves all four individual community rules match the reviewed source.

Gap found: `scripts/canonical_findings.py --refresh` cannot close this composite finding because its expected target is the four-label sequence while canonical refresh resolves against one rule target at a time. Therefore the worker-facing finding remains active even after the individual canonical rules are correct.

Durable fix in progress:
- `a1e541604351f863820e1db1238595c94c29343e` adds `scripts/resolve_running_style_sequence_finding.py`, which closes only this exact composite finding after verifying all four canonical community terms, required zh-CN aliases, preferred labels, accepted labels, source path, match mode, and expected target.
- `ef3398cba52e05563364a8b4b6b75d843f443aa3` wires that resolver through the already-production-invoked `resolve_running_style_narrative_finding.py`, so both Context Sync and translation-review plan sync execute it after canonical refresh.
- `3647fea41210036c953b8ad2c8ed8f5a69bbb83e` adds regression coverage for the resolver and idempotence.

Local pytest could not run because the inspection sandbox has no `pytest` executable. Production workflows triggered by the resolver/test changes remain the acceptance authority. Do not increment maintenance `completed_count` until production Context Sync passes, an unchanged/no-op Context Sync also passes, and the fresh review-plan state no longer exposes the finding.

`cf-55f0e8a1d70264a2` (`等级奖牌`) remains deferred: no new authoritative identity evidence was found in this pass.
