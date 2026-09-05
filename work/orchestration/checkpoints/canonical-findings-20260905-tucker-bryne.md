# Canonical finding research — Tucker Bryne

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260905T185100Z`

Finding: `cf-7b242406970feaef`

## Live finding

- zh-CN source: `塔可布莱恩`
- active review evidence: `text_data_dict.json`, category `120`
- source item includes `乘着塔可布莱恩的梦想`
- historical Vietnamese: `Mang theo giấc mơ của Tako Brian`
- finding match mode: `contains`
- path scope: `text_data_dict.json`, category prefix `120`
- concept: `Deserted Island scenario character name`
- kind: `proper_name`

Repository identity evidence also maps character ID `9049` to `塔可布莱恩` and marks the speaker as needing identity review, so the finding is not a generic phrase or incidental prose name.

## Identity evidence

The official Cygames character portal page for `タッカーブライン` displays the Latin player-facing name **Tucker Bryne** and describes her as the Deserted Island Project chief / field supervisor. This directly matches the scenario role represented by zh-CN `塔可布莱恩`.

Independent Lantis-distributed music metadata also credits `Tucker Bryne (CV: Yu Kobayashi)` for the character's scenario song, supporting the same Latin spelling.

Evidence checked 2026-09-05:

- https://umamusume.jp/character/tuckerbryne
- Amazon Music / Lantis WINNING LIVE 28 metadata for `Tucker's Grindin' Island`

Therefore the canonical identity is `Tucker Bryne`; the historical `Tako Brian` rendering is an unverified zh-CN phonetic guess and should be rejected.

## Durable hardening

- `ab173b338af6e199fbfd2044ab616dadd3aadbba` adds `scripts/harden_tucker_bryne_finding.py` with scoped rule `proper_name.tucker_bryne.scenario120` and explicit lock `audit.finding.tucker-bryne-scenario120`.
- `b35f6fdbc1f78c555dcf57b1d37a1e8496802b39` adds regression coverage for idempotence, canonical/review resolution, active-finding clearance, and category-120 containment.

## Production verification

All required production checks completed successfully for `b35f6fdbc1f78c555dcf57b1d37a1e8496802b39`:

- Validate: GitHub Actions run `33985852172` — success.
- Sync translation context: run `33985852142` — success.
- Sync translation review plan: run `33985852145` — success.
- Live generated context contains `proper_name.tucker_bryne.scenario120` with preferred `Tucker Bryne` and propagated review-plan context.
- Live `glossary/canonical_findings.json` is empty after production refresh, so `cf-7b242406970feaef` is no longer an active blocker.

Maintenance resolution is complete for Tucker Bryne. The prior verified maintenance handoff already counted this finding in `completed_count = 140`; this checkpoint reconfirms that evidence and MUST NOT increment the count again.
