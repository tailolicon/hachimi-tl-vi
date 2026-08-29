# canonical-final-conflict-sweep — Race / Skill-Inheritance cross-domain checkpoint

Task: `canonical-final-conflict-sweep`
Worker: `worker-chatgpt-hourly-002`
Deterministic branch: `canonical-final-conflict-sweep`
Prior checkpoint: `work/orchestration/checkpoints/canonical-final-conflict-sweep-20260829T1807Z.md`

## Ownership / routing

- Took over the released primary maintenance claim on live `main` using optimistic concurrency.
- Preserved the prior partial-result checkpoint and branch evidence.
- Continued only the serial final conflict sweep; did not open translation/review/UI work and did not edit `localized_data/**`.

## Cross-domain inspection completed in this slice

### Skill / Inheritance

Inspected `scripts/harden_skill_inheritance_canon.py` and `tests/test_skill_inheritance_hardening.py` against the already-integrated Training/Support, Common UI/System, Resources/Gacha/Shop and Character/Training UI domains.

Findings:

1. The legacy global `因子 -> Spark` umbrella lock is deliberately disabled; actual Spark enforcement is narrowed to inheritance-description category 172 and `localize_dict.json` UI contexts.
2. Bare `提示`, `灵感`, `继承`, and `传承` are explicitly excluded from blind source-bridge aliases. Full Skill Hint compounds remain canonical, which avoids prose overmatch.
3. Affinity is restricted to exact observed Outgame0343/0345/0346/0347 UI keys rather than global `相性` matching.
4. Permanent tests already include negative prose/assets for generic factor, inspiration, compatibility and inheritance wording, plus item-scoped context-hash and hardener-idempotence coverage.
5. No new cross-domain target collision with Training/Support or Common UI labels was found in this inspected slice.

### Race

Inspected `scripts/harden_race_canon.py` and `tests/test_race_hardening.py` against the current integrated domains.

Findings:

1. Race class labels are scoped away from ordinary story prose.
2. Short grade/UI tokens such as OP / Pre-OP are exact/scoped and include negative coverage for unrelated text.
3. Racecourse aliases are item/context scoped; generic place prose such as travel-to-Tokyo is explicitly negative.
4. Named race identities retire conflicting reviewed locks and include contextual handling for the lossy `京城锦标` collapse so Miyako Stakes and Keio Hai Nisai Stakes do not compete globally.
5. Song/objective prose is explicitly covered as negative for named-race canonical context.
6. No new Race-vs-Skill/Inheritance/Common-UI collision was found in this inspected slice.

## Execution-backend status

A Shiro/DeepSeek Harness attempt was made for local combined execution but the MCP tunnel returned HTTP 429. Per repository policy this is capability-local and not treated as task completion or a reason to skip required acceptance evidence.

## Remaining work

The final sweep is not complete. Required remaining acceptance work:

- inspect Conditions/Mood and any remaining pre-existing canonical hardeners against integrated domains;
- inspect materialized registries/source-bridge/community terms for overlapping aliases with competing targets or hidden lower-priority locks;
- run combined hardeners idempotently on one integrated snapshot and full repository validation when an execution backend is available;
- rebuild retrospective review context, run production Sync, and prove a second unchanged Sync semantic no-op;
- perform representative positive/negative spot checks across all integrated domains;
- only then transition Phase 0 to retrospective translation Audit Round 1.

No canonical data change was justified by the evidence inspected in this slice.
