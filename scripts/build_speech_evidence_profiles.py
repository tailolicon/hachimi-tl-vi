from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHARACTERS = ROOT / "glossary/characters.json"
DEFAULT_BIBLE = ROOT / "glossary/speech_bible.json"
DEFAULT_SAMPLES = ROOT / "glossary/speech_samples.json"
DEFAULT_OUTPUT = ROOT / "glossary/speech_evidence.json"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_rules(signals: dict[str, Any]) -> list[str]:
    rules = [
        "Đây là profile evidence-only: chỉ dùng để giữ nhịp/punctuation đã có trong source; không suy diễn tính cách, quan hệ, dialect hay đại từ.",
        "Wording và scene context luôn ưu tiên hơn thống kê corpus. Không thêm cảm thán, ngập ngừng, câu hỏi hay slang nếu source hiện tại không có.",
    ]
    exclamation = float(signals.get("exclamation_per_100_lines", 0) or 0)
    question = float(signals.get("question_per_100_lines", 0) or 0)
    ellipsis = float(signals.get("ellipsis_per_100_lines", 0) or 0)

    if exclamation >= 100:
        rules.append(
            "Corpus của nhân vật có mật độ cảm thán cao; khi source thực sự có dấu/cấu trúc cảm thán, giữ lực và nhịp tương ứng trong tiếng Việt."
        )
    elif exclamation <= 25:
        rules.append(
            "Corpus có ít cảm thán; tránh tự khuếch đại câu source trung tính thành giọng quá phấn khích."
        )

    if question >= 30:
        rules.append(
            "Câu hỏi xuất hiện tương đối thường; khi source là câu hỏi/phản vấn, giữ rõ sắc thái nghi vấn thay vì chuyển thành câu kể."
        )

    if ellipsis >= 150:
        rules.append(
            "Dấu ngắt/ellipsis xuất hiện nhiều trong corpus; khi source có khoảng ngập ngừng hoặc ngắt nhịp, giữ cấu trúc đó thay vì làm câu quá trơn."
        )
    elif ellipsis <= 50:
        rules.append(
            "Corpus có ít ellipsis; không tự thêm dấu ba chấm/ngập ngừng vào câu source không có."
        )
    return rules


def build_evidence_profiles(
    characters: dict[str, Any],
    speech_bible: dict[str, Any],
    samples: dict[str, Any],
) -> dict[str, Any]:
    character_records = characters.get("characters", {})
    if not isinstance(character_records, dict):
        character_records = {}
    curated = speech_bible.get("profiles", {})
    if not isinstance(curated, dict):
        curated = {}
    sample_records = samples.get("characters", {})
    if not isinstance(sample_records, dict):
        sample_records = {}

    profiles: dict[str, dict[str, Any]] = {}
    with_samples = 0
    without_samples = 0
    for key, character in sorted(character_records.items(), key=lambda item: str(item[0])):
        key = str(key)
        if key in curated or not isinstance(character, dict):
            continue
        sample = sample_records.get(key, {})
        if not isinstance(sample, dict):
            sample = {}
        dialogue_count = int(sample.get("dialogue_count", 0) or 0)
        signals = sample.get("signals", {}) if isinstance(sample.get("signals"), dict) else {}
        source_speakers = sample.get("source_speakers", [])
        if not isinstance(source_speakers, list):
            source_speakers = []

        if dialogue_count:
            with_samples += 1
            profile = {
                "canonical": character.get("canonical"),
                "status": "evidence_only",
                "source_commit": samples.get("source_commit"),
                "dialogue_count": dialogue_count,
                "source_speakers": source_speakers,
                "signals": signals,
                "translation_rules": evidence_rules(signals),
            }
        else:
            without_samples += 1
            profile = {
                "canonical": character.get("canonical"),
                "status": "identity_only_no_dialogue_evidence",
                "source_commit": samples.get("source_commit"),
                "dialogue_count": 0,
                "translation_rules": [
                    "Chưa có đủ mẫu thoại đã map cho nhân vật này. Chỉ dùng canonical identity; không áp giả định riêng về giọng, xưng hô, dialect hay tính cách.",
                    "Bám sát wording và scene context của source hiện tại cho tới khi có profile curated.",
                ],
            }
        profiles[key] = {k: v for k, v in profile.items() if v not in (None, "", [], {})}

    return {
        "schema_version": 1,
        "source_commit": samples.get("source_commit"),
        "policy": {
            "status": "evidence_only",
            "priority": "Curated speech_bible.json overrides this file. Source wording and scene context override both.",
            "safety": "Quantitative dialogue evidence may guide preservation of visible rhythm/punctuation only. It must not be treated as personality, relationship, hierarchy, dialect, or fixed-pronoun evidence.",
            "generation": "Profiles are regenerated from the pinned corpus and never overwrite manually curated speech_bible profiles.",
        },
        "summary": {
            "curated_profiles_excluded": len(curated),
            "evidence_profiles": len(profiles),
            "with_dialogue_samples": with_samples,
            "without_dialogue_samples": without_samples,
            "total_character_coverage": len(curated) + len(profiles),
        },
        "profiles": profiles,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build conservative evidence-only speech profiles for characters not yet curated.")
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

    result = build_evidence_profiles(characters, speech_bible, samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = result["summary"]
    print(
        f"curated={summary['curated_profiles_excluded']} evidence={summary['evidence_profiles']} "
        f"sampled={summary['with_dialogue_samples']} unsampled={summary['without_dialogue_samples']} "
        f"coverage={summary['total_character_coverage']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
