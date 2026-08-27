# Parallel curation workers

This protocol lets many independent agents curate character speech profiles and terminology without editing canonical glossary files directly.

Translation workers and curation workers are separate. Curation workers **must not** edit `localized_data`, translation progress, translation claims/results, or canonical glossary registries.

## Source of truth

Before claiming work, every curation worker must read:

1. `GAME_CONTEXT.md`
2. `CONTEXT_MAINTENANCE.md`
3. `PARALLEL_CURATION.md`
4. `work/curation/active_plan.json`
5. the active plan path named by `active_plan.json`
6. the relevant evidence files for its batch

For terminology batches involving skill names, also read `glossary/skill_name_style.json`. For player-facing gameplay/UI terminology, read `glossary/ui_community_terms.json` when relevant.

Repository state, not private chat memory, is authoritative.

The active plan is pinned to the same `source_commit` used by the current context queues. A worker must never silently switch to a newer moving upstream branch.

## Work types

### Speech batches

Batch IDs are `speech-NNNN` and normally contain 5 characters.

For each assigned character use:

- `glossary/characters.json` for canonical identity and aliases,
- `glossary/speech_samples.json` for bounded real dialogue evidence,
- `glossary/speech_evidence.json` for conservative fallback signals,
- `glossary/speech_bible.json` to avoid contradicting already curated profiles,
- reliable public/official character information when useful.

The output is compact **Vietnamese translation guidance**, not biography prose. Paraphrase facts; do not copy long profile text from websites.

A strong profile should capture only translation-relevant properties such as register, rhythm, formality, explicit self-reference, useful anti-rules, and a few concrete translation rules.

Never infer a fixed Vietnamese pronoun pair, dialect, hierarchy, romance/intimacy, or relationship solely from punctuation statistics. Source scene/context always outranks a general profile.

### Terminology batches

Batch IDs are `term-NNNN` and normally contain 20 unique source entities.

Use:

- `glossary/terminology_review_queue.json`,
- `glossary/generated_candidates.json`,
- `glossary/term_registry.json`,
- `glossary/observed_terms.json`,
- `glossary/characters.json`,
- `glossary/ui_community_terms.json` for common EN/player-facing gameplay terms,
- `glossary/skill_name_style.json` for individual skill-name decisions,
- reliable current/public game references when needed.

For every item choose exactly one explicit action:

- `lock`: the mapping is sufficiently verified and should become canonical;
- `defer`: reviewed, but evidence is insufficient or ambiguity remains;
- `ignore`: this item should not be a canonical terminology concept.

When uncertain, **defer rather than guess**. Character/racehorse proper names must never be literal semantic calques from Chinese. Do not use UmaTL English translation text as AI input.

#### Skill-name curation rule

Individual skill names use a different policy from generic gameplay labels. `Skill`, `Unique Skill`, `Evolution Skill`, stats, Distance/Style labels and other listed gameplay concepts follow the English/player-facing policy in `ui_community_terms.json`; the **proper name of a skill** is localized into a concise Vietnamese/Hán-Việt ability title according to `skill_name_style.json`.

For a `skill_name` item:

- treat the zh-CN title as the primary **compression/style reference**: learn from how short and title-like it is instead of expanding it into explanatory Vietnamese;
- use the verified JP title/alias as the semantic/reference guard for wordplay, proper nouns, role/title imagery and distinctions that zh-CN may flatten;
- aim for roughly 2–4 meaningful title units when the source is compact, without forcing an unnatural word count;
- prefer natural Hán-Việt compounds when evocative and intelligible; otherwise use polished concise Vietnamese in the style of commercial-game/LoL ability localization;
- keep distinctive gimmicks instead of normalizing them away: e.g. `弧线教授 / 弧線のプロフェッサー` keeps the **Giáo Sư** image;
- preserve symbols such as `○`, `×`, `◎`, `☆` exactly;
- never turn a skill title into a sentence explaining its effect;
- exact `canonical_examples` in `skill_name_style.json` intentionally supersede older conflicting skill-name wording for translation/reference purposes. Do not use the older wording as evidence that the old style is preferred.

Current canonical examples include `弧线教授 → Giáo Sư Cung Tuyến`, the `弯道加速/回复/巧者` graded families in compact Vietnamese, and `强攻策 → Cường Công Kế`. Illustrative examples in the policy are **not** locks until their JP identity/nuance is verified.

If an already-merged old skill-name lock conflicts with an exact `skill_name_style.json` canonical example, do not silently create a second conflicting lock in an ordinary batch. Treat the policy example as the translation override and leave canonical-registry migration to a dedicated maintenance change.

## Lease and atomic claim

The active plan specifies `lease_minutes` (currently 45).

A worker owns at most one curation batch at a time.

For a candidate batch, first check:

- `work/curation/merged/<batch_id>.json` — if present, skip;
- `work/curation/claims/<batch_id>.json` — if a non-expired claim exists, skip.

To atomically claim an unclaimed batch, create:

`work/curation/claims/<batch_id>.json`

using the repository contents API/create-file operation. Creation must fail rather than overwrite if another worker won the race.

Claim schema:

```json
{
  "schema_version": 1,
  "plan_id": "ctx-...-v1",
  "batch_id": "speech-0001",
  "claim_id": "UNIQUE_WORKER_GENERATED_ID",
  "worker_id": "descriptive-session-id",
  "claimed_at": "ISO-8601 UTC",
  "heartbeat_at": "ISO-8601 UTC",
  "expires_at": "ISO-8601 UTC",
  "lease_minutes": 45
}
```

If create fails because the claim appeared concurrently, pick another batch.

Stale claims are reaped automatically. A worker should heartbeat its own claim while doing substantial work by replacing the claim file with the same `claim_id` and a refreshed `heartbeat_at`/`expires_at`.

Never replace another active worker's claim.

## Speech result schema

Write one result file only after all characters in the batch are covered:

`work/curation/results/<batch_id>/<claim_id>.json`

```json
{
  "schema_version": 1,
  "plan_id": "ctx-...-v1",
  "batch_id": "speech-0001",
  "claim_id": "...",
  "worker_id": "...",
  "profiles": [
    {
      "character_key": "1059",
      "canonical": "Mejiro Dober",
      "register": ["...", "..."],
      "tempo": "compact guidance",
      "politeness": "compact guidance",
      "self_reference": "optional; only when evidence supports it",
      "translation_rules": [
        "At least two concrete Vietnamese translation rules.",
        "Do not invent unsupported speech quirks."
      ],
      "anti_rules": ["optional compact anti-rules"],
      "source_urls": ["optional reliable references"],
      "evidence_note": "optional short paraphrased reasoning/evidence note",
      "confidence": "high|medium|low"
    }
  ]
}
```

The result must cover **all and only** character keys in the claimed batch. Canonical names must match the plan exactly.

## Terminology result schema

Write:

`work/curation/results/<batch_id>/<claim_id>.json`

```json
{
  "schema_version": 1,
  "plan_id": "ctx-...-v1",
  "batch_id": "term-0001",
  "claim_id": "...",
  "worker_id": "...",
  "decisions": [
    {
      "source_zh_cn": "弧线教授",
      "action": "lock",
      "target_vi": "Giáo Sư Cung Tuyến",
      "kind": "skill_name",
      "term_id": "optional.stable.id",
      "ja": ["弧線のプロフェッサー"],
      "zh_tw": [],
      "source_aliases": [],
      "note": "verified skill-title decision following skill_name_style.json"
    },
    {
      "source_zh_cn": "ambiguous item",
      "action": "defer",
      "note": "why it remains unresolved"
    }
  ]
}
```

The result must cover **all and only** source strings in the batch. `target_vi` is mandatory for `lock` and omitted for `defer`/`ignore`.

## Completion marker

After the complete result is committed, create:

`work/curation/completions/<batch_id>/<claim_id>.json`

```json
{
  "schema_version": 1,
  "plan_id": "ctx-...-v1",
  "batch_id": "speech-0001",
  "claim_id": "...",
  "worker_id": "...",
  "completed_at": "ISO-8601 UTC",
  "result_path": "work/curation/results/speech-0001/<claim_id>.json"
}
```

The merge workflow verifies that completion, current claim and result all carry the same active `plan_id`, `batch_id` and `claim_id`.

## Canonical merge ownership

Curation workers never edit these directly:

- `glossary/speech_bible.json`
- `glossary/terminology_reviews.json`
- `glossary/term_registry.json`
- `glossary/speech_review_queue.json`
- `glossary/terminology_review_queue.json`

`.github/workflows/merge-curation.yml` is the sole parallel-curation merge owner. It:

1. validates exact batch coverage and current claim ownership;
2. merges speech profiles without silently overwriting an existing curated profile;
3. appends explicit terminology decisions;
4. runs `apply_terminology_reviews.py` conflict validation;
5. rebuilds both review queues;
6. runs context tests and translation validation;
7. writes `work/curation/merged/<batch_id>.json`.

A conflicting lock or profile stops the merge instead of silently selecting one answer.

## Worker loop

After completing one batch, immediately read the current active plan again, claim another unmerged/unclaimed batch, and repeat until the session/tool limit is approaching or no assignable batch remains.

Recommended mix with many sessions:

- roughly 1/3 of sessions on `speech-*` until fallback profiles are upgraded;
- roughly 2/3 on `term-*` because terminology has far more items.

## Ready-to-paste prompt for another agent

```text
Continue tailolicon/hachimi-tl-vi as a parallel curation worker. Do not rely on chat history. Read GAME_CONTEXT.md, CONTEXT_MAINTENANCE.md, PARALLEL_CURATION.md, work/curation/active_plan.json and the active plan it points to on main. For terminology involving individual skill names, also read glossary/skill_name_style.json; use zh-CN as the compact naming-style reference, JP as the semantic/reference guard, prefer concise natural Hán-Việt or polished Vietnamese ability titles, preserve symbols, and never expand a skill name into an effect sentence. Generic gameplay labels remain English according to glossary/ui_community_terms.json. Atomically claim one available unmerged curation batch using work/curation/claims/<batch_id>.json and the active plan_id. Prefer speech batches if fewer speech workers are active; otherwise take terminology. For speech, use characters.json plus pinned speech_samples/speech_evidence and reliable public/official references when useful, producing compact paraphrased Vietnamese translation guidance without inventing pronouns, dialect, relationships or lore. For terminology, review every assigned source entity and choose lock/defer/ignore; defer when uncertain, never literal-calque Chinese character/racehorse names, and do not use UmaTL English translation text as AI input. Write only claim-scoped results under work/curation/results and then a completion marker under work/curation/completions. Never edit speech_bible.json, terminology_reviews.json, term_registry.json, review queues, localized_data, or translation progress directly; merge workflows own canonical files. Heartbeat the claim during long work. After completing a batch, immediately claim another and repeat until the session/tool limit is approaching or no assignable batch remains.
```
