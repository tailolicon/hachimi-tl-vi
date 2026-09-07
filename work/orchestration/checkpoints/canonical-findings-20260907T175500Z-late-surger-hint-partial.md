# Canonical finding partial — Late Surger hint Skill

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T174916Z`
Finding: `cf-b6119398fbb3b37f`

## Finding

The exact Skill title `居中诀窍○` remained locked by `reviewed.skill_name.337707aae500` as `Mẹo Sashi○`, while the permanent player-facing running-style vocabulary locks 差し / 差行 to **Late Surger**. This is a systemic canonical conflict rather than an isolated translation-line issue.

## Durable fix

- Added a permanent hardener update for `reviewed.skill_name.337707aae500` so its target regenerates as **`Mẹo Late Surger○`** and explicitly supersedes the legacy Sashi wording.
- Isolated worktree verification ran `scripts/enforce_player_facing_canon.py` twice. The first pass changed generated context; the second pass reported every hardener section `false`, confirming local idempotence.
- The regenerated term was directly inspected and had `target_vi: Mẹo Late Surger○` while preserving the exact zh-CN alias `居中诀窍○` and JP identity `差しのコツ○`.
- Fix commit on the temporary branch: `f043553eb51a7f97e30bcd7973876af850a59d4f`.
- GitHub PR #37 was merged to `main` as `52899e7046d1b8964c4ee1ae94c9fdcec6281a2b`.

## Acceptance still required

At checkpoint time no GitHub Actions run had yet appeared for merge commit `52899e7046d1b8964c4ee1ae94c9fdcec6281a2b`. Therefore this finding is **not yet maintenance-complete** and `completed_count` must remain **198**.

Successor should:

1. confirm a production Context Sync on a `main` head containing `52899e7046d1b8964c4ee1ae94c9fdcec6281a2b` succeeds and persists the hardener result;
2. verify regenerated `canonical_findings.json` no longer blocks `cf-b6119398fbb3b37f` on legacy Sashi wording;
3. run/confirm the required second production Context Sync is unchanged/no-op;
4. only then record completion and increment `completed_count` from 198 to 199.
