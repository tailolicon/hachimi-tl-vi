from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from scripts.sync_hachimi_source import SOURCE_LANGUAGE, SOURCE_REPO, kind_for_asset

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHARACTERS = ROOT / "glossary/characters.json"
DEFAULT_OUTPUT = ROOT / "glossary/speech_samples.json"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def iter_dialogue_nodes(
    node: Any, path: tuple[Any, ...] = ()
) -> Iterable[tuple[tuple[Any, ...], str, str]]:
    """Yield (json_path, speaker, text) from common Hachimi dialogue blocks."""
    if isinstance(node, dict):
        speaker = clean_text(node.get("name")) or clean_text(node.get("speaker"))
        text = clean_text(node.get("text")) or clean_text(node.get("message"))
        if speaker and text:
            yield path, speaker, text
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                yield from iter_dialogue_nodes(value, (*path, key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            if isinstance(value, (dict, list)):
                yield from iter_dialogue_nodes(value, (*path, index))


def character_alias_map(characters: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    aliases: dict[str, set[str]] = defaultdict(set)
    records = characters.get("characters", {})
    if not isinstance(records, dict):
        return {}, set()
    for key, record in records.items():
        if not isinstance(record, dict):
            continue
        values: list[str] = []
        canonical = clean_text(record.get("canonical"))
        if canonical:
            values.append(canonical)
        for field in ("ja", "zh_cn", "zh_tw", "aliases"):
            raw = record.get(field, [])
            if isinstance(raw, str):
                raw = [raw]
            if isinstance(raw, list):
                values.extend(clean_text(item) for item in raw if clean_text(item))
        for alias in values:
            aliases[alias].add(str(key))

    resolved: dict[str, str] = {}
    ambiguous: set[str] = set()
    for alias, keys in aliases.items():
        if len(keys) == 1:
            resolved[alias] = next(iter(keys))
        else:
            ambiguous.add(alias)
    return resolved, ambiguous


def stable_rank(*parts: str) -> int:
    payload = "\0".join(parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def add_bounded_sample(
    store: dict[str, list[tuple[int, dict[str, Any]]]],
    key: str,
    sample: dict[str, Any],
    *,
    candidate_limit: int,
) -> None:
    rank = stable_rank(
        str(sample.get("source_path", "")),
        json.dumps(sample.get("json_path", []), ensure_ascii=False),
        str(sample.get("text", "")),
    )
    bucket = store.setdefault(key, [])
    if len(bucket) < candidate_limit:
        bucket.append((rank, sample))
        return
    worst_index, worst = max(enumerate(bucket), key=lambda item: item[1][0])
    if rank < worst[0]:
        bucket[worst_index] = (rank, sample)


def build_samples(
    upstream_root: Path,
    characters: dict[str, Any],
    source_commit: str,
    *,
    max_samples: int = 12,
    max_unmatched: int = 200,
) -> dict[str, Any]:
    localized = upstream_root / "localized_data"
    if not localized.is_dir():
        raise ValueError(f"localized_data not found under {upstream_root}")

    alias_to_key, ambiguous_aliases = character_alias_map(characters)
    character_records = characters.get("characters", {})
    if not isinstance(character_records, dict):
        character_records = {}

    dialogue_count: Counter[str] = Counter()
    char_count: Counter[str] = Counter()
    exclamation_count: Counter[str] = Counter()
    question_count: Counter[str] = Counter()
    ellipsis_count: Counter[str] = Counter()
    source_speakers: dict[str, set[str]] = defaultdict(set)
    kinds: dict[str, set[str]] = defaultdict(set)
    samples: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    seen_sample_text: dict[str, set[str]] = defaultdict(set)

    unmatched_count: Counter[str] = Counter()
    unmatched_samples: dict[str, tuple[int, dict[str, Any]]] = {}

    files_scanned = 0
    dialogue_blocks = 0
    matched_blocks = 0
    invalid_json = 0
    candidate_limit = max(max_samples * 4, max_samples)

    assets = localized / "assets"
    if not assets.is_dir():
        return {
            "schema_version": 1,
            "source_repo": SOURCE_REPO,
            "source_commit": source_commit,
            "source_language": SOURCE_LANGUAGE,
            "policy": {
                "status": "evidence_only",
                "rule": "No asset directory was present; speech profiles remain curated separately.",
            },
            "stats": {
                "files_scanned": 0,
                "dialogue_blocks": 0,
                "matched_blocks": 0,
                "matched_characters": 0,
                "unmatched_speakers": 0,
                "ambiguous_aliases": len(ambiguous_aliases),
                "invalid_json": 0,
            },
            "characters": {},
            "unmatched_speakers": [],
        }

    for file in sorted(assets.rglob("*.json")):
        rel = file.relative_to(localized).as_posix()
        kind = kind_for_asset(rel)
        if kind not in {"story", "home", "race_story", "asset"}:
            continue
        files_scanned += 1
        try:
            doc = json.loads(file.read_text(encoding="utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            invalid_json += 1
            continue

        for json_path, speaker, text in iter_dialogue_nodes(doc):
            dialogue_blocks += 1
            key = alias_to_key.get(speaker)
            sample = {
                "speaker": speaker,
                "kind": kind,
                "source_path": rel,
                "json_path": list(json_path),
                "text": text,
            }
            if key is None:
                unmatched_count[speaker] += 1
                rank = stable_rank(rel, json.dumps(json_path, ensure_ascii=False), text)
                old = unmatched_samples.get(speaker)
                if old is None or rank < old[0]:
                    unmatched_samples[speaker] = (rank, sample)
                continue

            matched_blocks += 1
            dialogue_count[key] += 1
            char_count[key] += len(text)
            exclamation_count[key] += text.count("!") + text.count("！")
            question_count[key] += text.count("?") + text.count("？")
            ellipsis_count[key] += text.count("…") + text.count("...")
            source_speakers[key].add(speaker)
            kinds[key].add(kind)

            # Store only short, useful evidence lines and deduplicate exact text.
            if len(text) <= 240 and text not in seen_sample_text[key]:
                seen_sample_text[key].add(text)
                add_bounded_sample(
                    samples,
                    key,
                    sample,
                    candidate_limit=candidate_limit,
                )

    output_characters: dict[str, Any] = {}
    for key in sorted(dialogue_count, key=lambda value: (-dialogue_count[value], value)):
        record = character_records.get(key, {}) if isinstance(character_records, dict) else {}
        canonical = record.get("canonical") if isinstance(record, dict) else None
        count = dialogue_count[key]
        selected_samples = [
            sample for _, sample in sorted(samples.get(key, []), key=lambda item: item[0])[:max_samples]
        ]
        output_characters[key] = {
            "canonical": canonical,
            "source_speakers": sorted(source_speakers[key]),
            "kinds": sorted(kinds[key]),
            "dialogue_count": count,
            "source_char_count": char_count[key],
            "signals": {
                "avg_chars_per_line": round(char_count[key] / count, 2) if count else 0,
                "exclamation_per_100_lines": round(exclamation_count[key] * 100 / count, 2) if count else 0,
                "question_per_100_lines": round(question_count[key] * 100 / count, 2) if count else 0,
                "ellipsis_per_100_lines": round(ellipsis_count[key] * 100 / count, 2) if count else 0,
            },
            "samples": selected_samples,
        }

    unmatched_rows = []
    for speaker, count in unmatched_count.most_common(max_unmatched):
        row: dict[str, Any] = {"speaker": speaker, "dialogue_count": count}
        candidate = unmatched_samples.get(speaker)
        if candidate:
            row["sample"] = candidate[1]
        unmatched_rows.append(row)

    return {
        "schema_version": 1,
        "source_repo": SOURCE_REPO,
        "source_commit": source_commit,
        "source_language": SOURCE_LANGUAGE,
        "policy": {
            "status": "evidence_only",
            "rule": "Samples and punctuation statistics are evidence for review, not automatic personality claims.",
            "translation_source": "The sampled dialogue comes from the pinned zh-CN JP-server translation source and retains its source licensing/provenance.",
            "profile_rule": "Curated speech_bible.json remains the only profile guidance injected into translation prompts.",
        },
        "stats": {
            "files_scanned": files_scanned,
            "dialogue_blocks": dialogue_blocks,
            "matched_blocks": matched_blocks,
            "matched_characters": len(output_characters),
            "unmatched_speakers": len(unmatched_count),
            "ambiguous_aliases": len(ambiguous_aliases),
            "invalid_json": invalid_json,
        },
        "characters": output_characters,
        "unmatched_speakers": unmatched_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract bounded dialogue evidence per known character.")
    parser.add_argument("--upstream-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--characters", type=Path, default=DEFAULT_CHARACTERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-samples", type=int, default=12)
    parser.add_argument("--max-unmatched", type=int, default=200)
    args = parser.parse_args()
    if args.max_samples < 1:
        parser.error("--max-samples must be >= 1")
    if args.max_unmatched < 0:
        parser.error("--max-unmatched must be >= 0")

    characters = read_json(args.characters, {}) or {}
    if not isinstance(characters, dict):
        raise SystemExit("characters registry must be a JSON object")
    output = build_samples(
        args.upstream_root,
        characters,
        args.source_commit,
        max_samples=args.max_samples,
        max_unmatched=args.max_unmatched,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"matched_characters={output['stats']['matched_characters']} "
        f"matched_blocks={output['stats']['matched_blocks']} "
        f"unmatched_speakers={output['stats']['unmatched_speakers']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
