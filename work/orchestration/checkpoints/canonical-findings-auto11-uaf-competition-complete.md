# Canonical maintenance checkpoint — U.A.F. competition context complete

Claim: `canonical-findings-maintenance-chatgpt-20260831T1946Z`

Finding `cf-552896cb4b769204` is resolved on live `main`.

- source: `比赛` in `text_data_dict.json` category `120`, key `7`
- affected phrase: `15种独特的比赛`
- semantic context: U.A.F. fifteen athletic disciplines, not horse races
- generic canonical term remains: `race.generic` -> `Cuộc đua`
- existing hardener: `scripts/harden_uaf_competition_context_finding.py`, which excludes `15种独特的比赛` from generic race matching
- resolver wiring commit: `5ea2df39ca65fe15ebbca6b0ea21431b959d78bc`
- regression commit: `22220a2baeb16e7113a2e70464fbc4e9cd923810`
- Validate run `33432932026`: success
- Sync translation context run `33432932018`: success
- generated context commit: `f092f2083ade393939f3fc41d06613af7babc980`
- live canonical resolution: `layer=context_guard`, `term_id=race.generic`, `target_vi=Cuộc đua`

The guard is intentionally narrow: ordinary `比赛` race contexts still match `race.generic`; only the U.A.F. sports-discipline phrase is shielded. Retrospective review can therefore translate that occurrence by meaning (for example `môn thi đấu`) without being forced to use `Cuộc đua`.

Maintenance completed count advances from 106 to 107. Continue immediately with the next live unresolved canonical finding.
