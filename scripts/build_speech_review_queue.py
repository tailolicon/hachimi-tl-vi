from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHARACTERS = ROOT / "glossary/characters.json"
DEFAULT_BIBLE = ROOT / "glossary/speech_bible.json"
DEFAULT_EVIDENCE = ROOT / "glossary/speech_evidence.json"
DEFAULT_SAMPLES = ROOT / "glossary/speech_samples.json"
DEFAULT_OUTPUT = ROOT / "glossary/speech_review_queue.json"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_queue(
    characters: dict[str, Any],
    speech_bible: dict[str, Any],
    samples: dict[str, Any],
    speech_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    records = characters.get("characters", {})
    if not isinstance(records, dict):
        records = {}
    profiles = speech_bible.get("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
    evidence_profiles = (speech_evidence or {}).get("profiles", {})
    if not isinstance(evidence_profiles, dict):
        evidence_profiles = {}
    sample_records = samples.get("characters", {})
    if not isinstance(sample_records, dict):
        sample_records = {}

    queue: list[dict[str, Any]] = []
    curated = 0
    evidence_covered = 0
    sampled = 0
    for key, character in records.items():
        if not isinstance(character, dict):
            continue
        key = str(key)
        profile = profiles.get(key)
        fallback = evidence_profiles.get(key)
        evidence = sample_records.get(key, {})
        if not isinstance(evidence, dict):
            evidence = {}
        dialogue_count = int(evidence.get("dialogue_count", 0) or 0)
        if dialogue_count:
            sampled += 1
        if isinstance(profile, dict):
            curated += 1
            status = "curated"
            priority = 0
        else:
            status = "needs_curated_review"
            priority = 100 + min(dialogue_count, 10000)
            if isinstance(fallback, dict):
                evidence_covered += 1

        row: dict[str, Any] = {
            "character_key": key,
            "game_id": character.get("game_id"),
            "canonical": character.get("canonical"),
            "ja": character.get("ja", []),
            "zh_cn": character.get("zh_cn", []),
            "identity_status": character.get("identity_status"),
            "status": status,
            "priority": priority,
            "dialogue_count": dialogue_count,
            "has_evidence_profile": isinstance(fallback, dict),
        }
        if evidence:
            row["signals"] = evidence.get("signals", {})
            row["source_speakers"] = evidence.get("source_speakers", [])
            row["sample_count"] = len(evidence.get("samples", [])) if isinstance(evidence.get("samples"), list) else 0
        if isinstance(profile, dict):
            row["profile_status"] = profile.get("status")
        elif isinstance(fallback, dict):
            row["evidence_status"] = fallback.get("status")
        queue.append(row)

    queue.sort(
        key=lambda row: (
            row["status"] != "needs_curated_review",
            -int(row.get("priority", 0)),
            str(row.get("canonical") or ""),
        )
    )

    unmatched = samples.get("unmatched_speakers", [])
    if not isinstance(unmatched, list):
        unmatched = []
    npc_queue = []
    for row in unmatched:
        if not isinstance(row, dict):
            continue
        npc_queue.append(
            {
                "speaker": row.get("speaker"),
                "dialogue_count": int(row.get("dialogue_count", 0) or 0),
                "status": "needs_identity_review",
            }
        )

    needs_review = sum(1 for row in queue if row["status"] == "needs_curated_review")
    full_guidance_coverage = curated + evidence_covered
    return {
        "schema_version": 2,
        "source_commit": samples.get("source_commit"),
        "policy": {
            "purpose": "Prioritize curation of strong character speech profiles while tracking conservative evidence-only fallback coverage.",
            "review_rule": "Use source dialogue evidence plus reliable character information. Do not infer fixed pronouns, dialect, hierarchy, or relationships from punctuation statistics alone.",
            "completion": "Curated coverage means speech_bible.json has a reviewed profile. Runtime guidance coverage may also use lower-priority speech_evidence.json until curation is finished.",
        },
        "summary": {
            "character_count": len(queue),
            "curated_profiles": curated,
            "evidence_fallback_profiles": evidence_covered,
            "runtime_guidance_coverage": full_guidance_coverage,
            "runtime_guidance_missing": len(queue) - full_guidance_coverage,
            "needs_curated_review": needs_review,
            "characters_with_dialogue_samples": sampled,
            "unmatched_speaker_count": len(npc_queue),
        },
        "characters": queue,
        "unmatched_speakers": npc_queue,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build prioritized character speech-profile review queue.")
    parser.add_argument("--characters", type=Path, default=DEFAULT_CHARACTERS)
    parser.add_argument("--speech-bible", type=Path, default=DEFAULT_BIBLE)
    parser.add_argument("--speech-evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    characters = read_json(args.characters, {}) or {}
    speech_bible = read_json(args.speech_bible, {}) or {}
    speech_evidence = read_json(args.speech_evidence, {}) or {}
    samples = read_json(args.samples, {}) or {}
    if not all(isinstance(value, dict) for value in (characters, speech_bible, speech_evidence, samples)):
        raise SystemExit("characters, speech bible, speech evidence, and samples must be JSON objects")

    queue = build_queue(characters, speech_bible, samples, speech_evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = queue["summary"]
    print(
        f"characters={summary['character_count']} curated={summary['curated_profiles']} "
        f"evidence={summary['evidence_fallback_profiles']} runtime_coverage={summary['runtime_guidance_coverage']} "
        f"needs_curated={summary['needs_curated_review']} sampled={summary['characters_with_dialogue_samples']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
