from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHARACTERS = ROOT / "glossary/characters.json"
DEFAULT_BIBLE = ROOT / "glossary/speech_bible.json"
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
) -> dict[str, Any]:
    records = characters.get("characters", {})
    if not isinstance(records, dict):
        records = {}
    profiles = speech_bible.get("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
    sample_records = samples.get("characters", {})
    if not isinstance(sample_records, dict):
        sample_records = {}

    queue: list[dict[str, Any]] = []
    covered = 0
    sampled = 0
    for key, character in records.items():
        if not isinstance(character, dict):
            continue
        profile = profiles.get(str(key))
        evidence = sample_records.get(str(key), {})
        if not isinstance(evidence, dict):
            evidence = {}
        dialogue_count = int(evidence.get("dialogue_count", 0) or 0)
        if dialogue_count:
            sampled += 1
        if isinstance(profile, dict):
            covered += 1
            status = "covered"
            priority = 0
        else:
            status = "needs_review"
            # Prioritize characters with lots of actual dialogue evidence, then
            # stable game IDs. Saturate to keep the score readable.
            priority = 100 + min(dialogue_count, 10000)

        row: dict[str, Any] = {
            "character_key": str(key),
            "game_id": character.get("game_id"),
            "canonical": character.get("canonical"),
            "ja": character.get("ja", []),
            "zh_cn": character.get("zh_cn", []),
            "identity_status": character.get("identity_status"),
            "status": status,
            "priority": priority,
            "dialogue_count": dialogue_count,
        }
        if evidence:
            row["signals"] = evidence.get("signals", {})
            row["source_speakers"] = evidence.get("source_speakers", [])
            row["sample_count"] = len(evidence.get("samples", [])) if isinstance(evidence.get("samples"), list) else 0
        if isinstance(profile, dict):
            row["profile_status"] = profile.get("status")
        queue.append(row)

    queue.sort(
        key=lambda row: (
            row["status"] != "needs_review",
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

    needs_review = sum(1 for row in queue if row["status"] == "needs_review")
    return {
        "schema_version": 1,
        "source_commit": samples.get("source_commit"),
        "policy": {
            "purpose": "Prioritize human/AI-assisted curation of compact speech profiles; this queue is not prompt guidance.",
            "review_rule": "Use source dialogue evidence plus reliable character information. Do not infer fixed pronouns, dialect, hierarchy, or relationships from punctuation statistics alone.",
            "completion": "A character is covered only when speech_bible.json contains a reviewed profile for the same character key.",
        },
        "summary": {
            "character_count": len(queue),
            "covered_profiles": covered,
            "needs_review": needs_review,
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
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    characters = read_json(args.characters, {}) or {}
    speech_bible = read_json(args.speech_bible, {}) or {}
    samples = read_json(args.samples, {}) or {}
    if not all(isinstance(value, dict) for value in (characters, speech_bible, samples)):
        raise SystemExit("characters, speech bible, and samples must be JSON objects")

    queue = build_queue(characters, speech_bible, samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = queue["summary"]
    print(
        f"characters={summary['character_count']} covered={summary['covered_profiles']} "
        f"needs_review={summary['needs_review']} sampled={summary['characters_with_dialogue_samples']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
