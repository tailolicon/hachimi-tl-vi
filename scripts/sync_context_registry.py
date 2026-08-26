from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROGRESS = ROOT / "work/translation_progress.json"
DEFAULT_OUTPUT = ROOT / "glossary/characters.json"
DEFAULT_UMA_URL = (
    "https://raw.githubusercontent.com/BrandonL00/UmaSim/main/"
    "src/data/generated/umapyoiCharacters.json"
)

DEFAULT_RULES = [
    "Tên Uma Musume là tên riêng; không dịch nghĩa tên tiếng Trung sang tiếng Việt.",
    "Ưu tiên canonical Roman-letter name khi mapping chắc chắn.",
    "Không áp một cặp đại từ tôi/bạn cho mọi nhân vật; xưng hô phải theo quan hệ và scene context.",
    "Nếu profile chưa có speech rule, dùng lời thoại tự nhiên nhưng không tự bịa mức độ thân mật/seniority.",
]


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str) -> Any:
    req = Request(url, headers={"User-Agent": "hachimi-tl-vi-context-sync/1"})
    with urlopen(req, timeout=60) as response:
        return json.load(response)


def merge_list(*values: Any) -> list[str]:
    out: list[str] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            continue
        for item in value:
            item = str(item).strip()
            if item and item not in out:
                out.append(item)
    return out


def existing_records(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("characters", {}) if isinstance(data, dict) else {}
    return [x for x in raw.values() if isinstance(x, dict)] if isinstance(raw, dict) else []


def find_existing(
    records: list[dict[str, Any]], game_id: int, canonical: str, name_jp: str, zh_name: str | None
) -> dict[str, Any]:
    gid = str(game_id)
    for record in records:
        if str(record.get("game_id", "")) == gid:
            return record
    for record in records:
        if canonical and str(record.get("canonical", "")).casefold() == canonical.casefold():
            return record
        if name_jp and name_jp in merge_list(record.get("ja")):
            return record
        if zh_name and zh_name in merge_list(record.get("zh_cn")):
            return record
    return {}


def build_registry(
    progress: dict[str, Any],
    uma_data: dict[str, Any],
    source_text_data: dict[str, Any],
    existing: dict[str, Any],
) -> dict[str, Any]:
    zh_names = source_text_data.get("6", {})
    if not isinstance(zh_names, dict):
        raise ValueError("source text_data category 6 (character names) is missing")

    old_records = existing_records(existing)
    generated: dict[str, dict[str, Any]] = {}
    matched_ids: set[str] = set()

    for source in uma_data.get("characters", []):
        if not isinstance(source, dict) or source.get("gameId") is None:
            continue
        game_id = int(source["gameId"])
        gid = str(game_id)
        canonical = str(source.get("nameEn") or "").strip()
        name_jp = str(source.get("nameJp") or "").strip()
        zh_name = str(zh_names.get(gid) or "").strip() or None
        previous = find_existing(old_records, game_id, canonical, name_jp, zh_name)

        record: dict[str, Any] = {
            "game_id": game_id,
            "canonical": canonical,
            "ja": merge_list([name_jp] if name_jp else [], previous.get("ja")),
            "zh_cn": merge_list([zh_name] if zh_name else [], previous.get("zh_cn")),
            "name_internal": source.get("nameInternal"),
            "preferred_url": source.get("preferredUrl"),
            "official_link": source.get("officialLink"),
            "role": previous.get("role", "umamusume"),
            "speech_rules": previous.get("speech_rules", []),
        }
        for manual_key in (
            "relationships",
            "vi_notes",
            "pronouns",
            "speech_traits",
            "aliases",
            "zh_tw",
        ):
            if manual_key in previous:
                record[manual_key] = previous[manual_key]
        generated[gid] = {k: v for k, v in record.items() if v not in (None, "", [], {})}
        if zh_name:
            matched_ids.add(gid)

    unresolved = {
        str(game_id): str(name)
        for game_id, name in sorted(zh_names.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else 10**12)
        if str(game_id) not in generated and str(name).strip()
    }

    return {
        "schema_version": 3,
        "generated": {
            "source_commit": progress.get("source_commit"),
            "source_repo": progress.get("source_repo"),
            "source_language": progress.get("source_language", "zh-CN"),
            "structured_character_source": DEFAULT_UMA_URL,
            "structured_generated_at": uma_data.get("generatedAt"),
            "structured_count": len(generated),
            "zh_alias_matches": len(matched_ids),
            "unresolved_source_count": len(unresolved),
            "policy": "Names/IDs only; long third-party profile prose is intentionally not copied into this registry.",
        },
        "default_rules": existing.get("default_rules", DEFAULT_RULES) if isinstance(existing, dict) else DEFAULT_RULES,
        "characters": generated,
        "unresolved_source_characters": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync canonical JP/Latin/zh-CN character aliases.")
    parser.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--uma-url", default=DEFAULT_UMA_URL)
    parser.add_argument("--source-json", type=Path)
    args = parser.parse_args()

    progress = read_json(args.progress)
    if not isinstance(progress, dict):
        raise SystemExit(f"Cannot read progress: {args.progress}")
    source_commit = progress.get("source_commit")
    source_repo = progress.get("source_repo")
    if not source_commit or not source_repo:
        raise SystemExit("progress must contain source_repo and source_commit")

    uma_data = fetch_json(args.uma_url)
    if args.source_json:
        source_text_data = read_json(args.source_json)
    else:
        source_url = (
            f"https://raw.githubusercontent.com/{source_repo}/{source_commit}/"
            "localized_data/text_data_dict.json"
        )
        source_text_data = fetch_json(source_url)

    existing = read_json(args.output, {}) or {}
    registry = build_registry(progress, uma_data, source_text_data, existing)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"characters={registry['generated']['structured_count']} "
        f"zh_alias_matches={registry['generated']['zh_alias_matches']} "
        f"unresolved={registry['generated']['unresolved_source_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
