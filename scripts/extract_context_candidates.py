from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROGRESS = ROOT / "work/translation_progress.json"
DEFAULT_OUTPUT = ROOT / "glossary/generated_candidates.json"

# text_data categories confirmed by current JP data tooling / Hachimi-shaped corpus.
CATEGORY_KINDS = {
    "4": "trainee_card_full_name",
    "5": "trainee_card_title",
    "6": "character_name",
    "32": "race_name",
    "33": "race_display_name",
    "47": "skill_name",
    "75": "support_card_full_name",
    "76": "support_card_title",
    "77": "support_character_name",
    "78": "support_display_name",
    "150": "support_unique_effect_name",
    "170": "character_display_name",
    "182": "character_name_alias",
}
SCENARIO_PATTERNS = (
    re.compile(r"育成剧本[「『\"]?([^」』\"\\n]{2,80})"),
    re.compile(r"(?:剧本|シナリオ)[「『\"]([^」』\"]{2,80})[」』\"]"),
)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str) -> Any:
    req = Request(url, headers={"User-Agent": "hachimi-tl-vi-context-candidates/1"})
    with urlopen(req, timeout=60) as response:
        return json.load(response)


def candidate_id(kind: str, source_category: str, source_index: str, text: str) -> str:
    payload = f"{kind}\0{source_category}\0{source_index}\0{text}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:24]


def add_candidate(
    out: list[dict[str, Any]],
    seen: set[tuple[str, str]],
    *,
    kind: str,
    category: str,
    index: str,
    text: str,
) -> None:
    clean = text.strip()
    if not clean:
        return
    dedupe = (kind, clean)
    if dedupe in seen:
        return
    seen.add(dedupe)
    out.append(
        {
            "id": candidate_id(kind, category, index, clean),
            "kind": kind,
            "source_language": "zh-CN",
            "source_category": category,
            "source_index": index,
            "source_text": clean,
            "status": "candidate",
        }
    )


def extract(text_data: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    counts: dict[str, int] = {}

    for category, kind in CATEGORY_KINDS.items():
        rows = text_data.get(category, {})
        if not isinstance(rows, dict):
            continue
        for index, value in rows.items():
            if not isinstance(value, str):
                continue
            add_candidate(
                candidates,
                seen,
                kind=kind,
                category=category,
                index=str(index),
                text=value,
            )
        counts[kind] = sum(1 for item in candidates if item["kind"] == kind)

    # Scenario names are scattered across descriptive strings, so collect them
    # conservatively as review candidates instead of locking them automatically.
    for category, rows in text_data.items():
        if not isinstance(rows, dict):
            continue
        for index, value in rows.items():
            if not isinstance(value, str) or not any(x in value for x in ("育成剧本", "剧本", "シナリオ")):
                continue
            for pattern in SCENARIO_PATTERNS:
                for match in pattern.finditer(value):
                    add_candidate(
                        candidates,
                        seen,
                        kind="scenario_name",
                        category=str(category),
                        index=str(index),
                        text=match.group(1),
                    )
    counts["scenario_name"] = sum(1 for item in candidates if item["kind"] == "scenario_name")

    candidates.sort(key=lambda item: (item["kind"], int(item["source_category"]) if item["source_category"].isdigit() else 10**9, item["source_index"]))
    return candidates, counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract reviewable terminology candidates from pinned zh-CN text_data.")
    parser.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
    parser.add_argument("--source-json", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    progress = read_json(args.progress)
    if not isinstance(progress, dict):
        raise SystemExit(f"Cannot read progress: {args.progress}")
    source_repo = progress.get("source_repo")
    source_commit = progress.get("source_commit")
    if not source_repo or not source_commit:
        raise SystemExit("progress must contain source_repo and source_commit")

    if args.source_json:
        text_data = read_json(args.source_json)
    else:
        url = (
            f"https://raw.githubusercontent.com/{source_repo}/{source_commit}/"
            "localized_data/text_data_dict.json"
        )
        text_data = fetch_json(url)
    if not isinstance(text_data, dict):
        raise SystemExit("source text_data is not a JSON object")

    candidates, counts = extract(text_data)
    output = {
        "schema_version": 1,
        "source_repo": source_repo,
        "source_commit": source_commit,
        "source_language": progress.get("source_language", "zh-CN"),
        "policy": {
            "status": "review_only",
            "rule": "Candidates are discovery data, not locked Vietnamese translations. Workers must not treat this file as canonical terminology.",
        },
        "counts": counts,
        "total": len(candidates),
        "candidates": candidates,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("total=" + str(len(candidates)) + " " + " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
