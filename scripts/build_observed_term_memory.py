from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from hachimi_tl_vi.context_categories import CATEGORY_KINDS

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROGRESS = ROOT / "work/translation_progress.json"
DEFAULT_TARGET = ROOT / "localized_data/text_data_dict.json"
DEFAULT_OUTPUT = ROOT / "glossary/observed_terms.json"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str) -> Any:
    req = Request(url, headers={"User-Agent": "hachimi-tl-vi-observed-terms/1"})
    with urlopen(req, timeout=60) as response:
        return json.load(response)


def build_memory(
    source_text_data: dict[str, Any], target_text_data: dict[str, Any]
) -> dict[str, Any]:
    observations: dict[str, list[dict[str, str]]] = defaultdict(list)

    for category, kind in CATEGORY_KINDS.items():
        source_rows = source_text_data.get(category, {})
        target_rows = target_text_data.get(category, {})
        if not isinstance(source_rows, dict) or not isinstance(target_rows, dict):
            continue
        for index, target in target_rows.items():
            source = source_rows.get(str(index))
            if not isinstance(source, str) or not isinstance(target, str):
                continue
            source = source.strip()
            target = target.strip()
            if not source or not target:
                continue
            observations[source].append(
                {
                    "kind": kind,
                    "category": str(category),
                    "index": str(index),
                    "target_vi": target,
                }
            )

    terms: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for source in sorted(observations):
        rows = observations[source]
        targets = sorted({row["target_vi"] for row in rows})
        kinds = sorted({row["kind"] for row in rows})
        locators = [
            {"category": row["category"], "index": row["index"]}
            for row in rows[:12]
        ]
        if len(targets) == 1:
            terms.append(
                {
                    "id": f"observed:{len(terms) + 1:06d}",
                    "status": "observed_merged",
                    "kinds": kinds,
                    "zh_cn": [source],
                    "target_vi": targets[0],
                    "locked": False,
                    "locators": locators,
                }
            )
        else:
            conflicts.append(
                {
                    "source_zh_cn": source,
                    "kinds": kinds,
                    "targets_vi": targets,
                    "locators": locators,
                }
            )

    return {
        "schema_version": 1,
        "policy": {
            "priority": "Reviewed locked term_registry entries override observed memory.",
            "use": "Reuse an observed target for an exact source entity when no locked rule conflicts. Conflicted observations are excluded from prompt memory.",
            "promotion": "Observed mappings are consistency memory, not reviewed canonical terminology. Promote reviewed concepts to term_registry.json.",
        },
        "observed_count": len(terms),
        "conflict_count": len(conflicts),
        "terms": terms,
        "conflicts": conflicts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build exact entity translation memory from merged localized_data.")
    parser.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
    parser.add_argument("--target-json", type=Path, default=DEFAULT_TARGET)
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
        source_text_data = read_json(args.source_json)
    else:
        source_url = (
            f"https://raw.githubusercontent.com/{source_repo}/{source_commit}/"
            "localized_data/text_data_dict.json"
        )
        source_text_data = fetch_json(source_url)
    target_text_data = read_json(args.target_json, {}) or {}
    if not isinstance(source_text_data, dict) or not isinstance(target_text_data, dict):
        raise SystemExit("source and target text_data must be JSON objects")

    memory = build_memory(source_text_data, target_text_data)
    memory["source_repo"] = source_repo
    memory["source_commit"] = source_commit
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"observed={memory['observed_count']} conflicts={memory['conflict_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
