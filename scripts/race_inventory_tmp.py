from __future__ import annotations

import json
import subprocess
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RACE_NAME_CATEGORIES = {"32", "33"}
COURSE_NAMES = {
    "东京": "Tokyo", "中山": "Nakayama", "京都": "Kyoto", "阪神": "Hanshin",
    "中京": "Chukyo", "札幌": "Sapporo", "函馆": "Hakodate", "新潟": "Niigata",
    "福岛": "Fukushima", "小仓": "Kokura", "大井": "Ohi", "川崎": "Kawasaki",
    "船桥": "Funabashi", "盛冈": "Morioka", "浦和": "Urawa", "门别": "Mombetsu",
    "佐贺": "Saga",
}
CLASS_GRADE_TOKENS = (
    "新马级", "经典级", "古马级", "ジュニア級", "クラシック級", "シニア級",
    "GⅠ", "GⅡ", "GⅢ", "G1", "G2", "G3", "Pre-OP", "OP", "L", "开放级",
    "未胜利", "未勝利", "出道战", "デビュー", "目标比赛", "目标竞赛",
)
RACE_UI_TOKENS = (
    "草地", "泥地", "短距离", "英里", "中距离", "长距离", "跑法",
    "领跑", "先行", "差行", "追赶", "追马", "大逃", "爆领",
    "马场状态", "场地状态", "良", "稍重", "重", "不良", "顺时针", "逆时针",
    "内圈", "外圈", "名次", "排名", "胜利", "败北", "粉丝数",
)


def load(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write(name: str, value: Any) -> None:
    path = ROOT / "work" / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_path(document: Any, path: list[Any]) -> Any:
    node = document
    for part in path:
        if isinstance(node, list):
            node = node[int(part)]
        else:
            node = node[str(part)]
    return node


def git_show_json(ref: str, path: str) -> Any:
    raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{ref}:{path}"],
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def fetch_pinned() -> dict[str, Any]:
    progress = load(ROOT / "work/translation_progress.json", {})
    repo = progress["source_repo"]
    commit = progress["source_commit"]
    url = f"https://raw.githubusercontent.com/{repo}/{commit}/localized_data/text_data_dict.json"
    req = urllib.request.Request(url, headers={"User-Agent": "hachimi-tl-vi-race-inventory/1"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response)


def aliases(term: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for field in ("zh_cn", "ja", "source_aliases"):
        values = term.get(field, [])
        if isinstance(values, list):
            result.update(str(value).strip() for value in values if str(value).strip())
    return result


def is_proper_race_term(term: dict[str, Any]) -> bool:
    tid = str(term.get("id", ""))
    category = str(term.get("category", ""))
    if category == "race_name":
        return True
    if not tid.startswith("race."):
        return False
    return tid not in {"race.generic"}


def main() -> int:
    pinned = fetch_pinned()
    registry = load(ROOT / "glossary/term_registry.json", {"terms": []})
    community = load(ROOT / "glossary/ui_community_terms.json", {"terms": []})
    bridge = load(ROOT / "glossary/source_bridge_terms.json", {"terms": []})

    race_terms = [
        term for term in registry.get("terms", [])
        if isinstance(term, dict) and bool(term.get("locked")) and is_proper_race_term(term)
    ]
    alias_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for term in race_terms:
        for alias in aliases(term):
            alias_map[alias].append(term)

    alias_conflicts = []
    for alias, terms in sorted(alias_map.items()):
        targets = sorted({str(term.get("target_vi", "")) for term in terms})
        if len(targets) > 1:
            alias_conflicts.append({
                "alias": alias,
                "targets": targets,
                "ids": sorted(str(term.get("id", "")) for term in terms),
            })

    pinned_race_sources: dict[str, list[dict[str, str]]] = defaultdict(list)
    for category in sorted(RACE_NAME_CATEGORIES):
        rows = pinned.get(category, {})
        if not isinstance(rows, dict):
            continue
        for index, value in rows.items():
            if isinstance(value, str) and value.strip():
                pinned_race_sources[value.strip()].append({"category": category, "index": str(index)})

    course_hits: dict[str, list[dict[str, str]]] = defaultdict(list)
    for category, rows in pinned.items():
        if not isinstance(rows, dict):
            continue
        for index, value in rows.items():
            if isinstance(value, str) and value.strip() in COURSE_NAMES:
                course_hits[value.strip()].append({"category": str(category), "index": str(index)})

    localized_docs: dict[str, Any] = {}
    corpus_rows: list[dict[str, Any]] = []
    token_hits: dict[str, list[dict[str, Any]]] = defaultdict(list)
    exact_race_rows: list[dict[str, Any]] = []
    merged_markers = sorted((ROOT / "work/merged").glob("batch-*.json"))
    merged_count = 0

    for marker_path in merged_markers:
        marker = load(marker_path, {})
        if marker.get("status") != "merged" or not marker.get("source_batch_ref"):
            continue
        batch_no = int(marker["batch"])
        source_ref = str(marker["source_batch_ref"])
        source_batch = git_show_json(source_ref, f"work/source_batches/batch-{batch_no:05d}.json")
        for entry_index, entry in enumerate(source_batch.get("entries", [])):
            if not isinstance(entry, dict):
                continue
            merged_count += 1
            source_path = str(entry.get("source_path", ""))
            json_path = entry.get("json_path")
            source = str(entry.get("source_text", ""))
            if not source_path or not isinstance(json_path, list):
                continue
            if source_path not in localized_docs:
                localized_docs[source_path] = load(ROOT / "localized_data" / source_path)
            try:
                current = get_path(localized_docs[source_path], json_path)
            except Exception:
                current = None
            row = {
                "uid": entry.get("uid"),
                "source_batch": batch_no,
                "entry_index": entry_index,
                "source_path": source_path,
                "json_path": json_path,
                "source": source,
                "current": current if isinstance(current, str) else None,
            }
            corpus_rows.append(row)
            stripped = source.strip()
            if stripped in pinned_race_sources:
                matched = alias_map.get(stripped, [])
                exact_race_rows.append({
                    **row,
                    "pinned_identities": pinned_race_sources[stripped],
                    "canonical_ids": sorted(str(term.get("id", "")) for term in matched),
                    "canonical_targets": sorted({str(term.get("target_vi", "")) for term in matched}),
                    "canonical_scopes": sorted({str(term.get("invalidation_scope", "global")) for term in matched}),
                    "canonical_modes": sorted({str(term.get("match_mode", "contains")) for term in matched}),
                })
            for token in (*CLASS_GRADE_TOKENS, *RACE_UI_TOKENS):
                if token in source:
                    token_hits[token].append(row)

    exact_collapsed: dict[str, dict[str, Any]] = {}
    for row in exact_race_rows:
        src = row["source"].strip()
        item = exact_collapsed.setdefault(src, {
            "source": src,
            "pinned_identities": row["pinned_identities"],
            "currents": set(),
            "canonical_ids": set(),
            "canonical_targets": set(),
            "canonical_scopes": set(),
            "canonical_modes": set(),
            "locators": [],
        })
        if row["current"] is not None:
            item["currents"].add(row["current"])
        for field in ("canonical_ids", "canonical_targets", "canonical_scopes", "canonical_modes"):
            item[field].update(row[field])
        item["locators"].append({
            "source_batch": row["source_batch"], "entry_index": row["entry_index"],
            "source_path": row["source_path"], "json_path": row["json_path"],
        })

    exact_summary = []
    for item in exact_collapsed.values():
        exact_summary.append({
            "source": item["source"],
            "pinned_identities": item["pinned_identities"],
            "currents": sorted(item["currents"]),
            "canonical_ids": sorted(item["canonical_ids"]),
            "canonical_targets": sorted(item["canonical_targets"]),
            "canonical_scopes": sorted(item["canonical_scopes"]),
            "canonical_modes": sorted(item["canonical_modes"]),
            "locators": item["locators"],
        })
    exact_summary.sort(key=lambda item: item["source"])

    gaps = [item for item in exact_summary if not item["canonical_ids"]]
    mismatches = [
        item for item in exact_summary
        if item["canonical_targets"] and any(cur not in item["canonical_targets"] for cur in item["currents"])
    ]
    global_proper = [
        {"id": str(term.get("id", "")), "target": term.get("target_vi"),
         "scope": str(term.get("invalidation_scope", "global")),
         "mode": str(term.get("match_mode", "contains")),
         "zh_cn": term.get("zh_cn", []), "ja": term.get("ja", [])}
        for term in race_terms if str(term.get("invalidation_scope", "global")) != "item"
    ]

    token_summary = {
        token: {
            "count": len(rows),
            "samples": rows[:12],
        }
        for token, rows in sorted(token_hits.items())
    }
    community_race = [term for term in community.get("terms", []) if isinstance(term, dict) and (
        str(term.get("category", "")) in {"race", "race_surface", "distance", "running_style"}
        or str(term.get("id", "")).startswith("common.race")
    )]
    bridge_race = [term for term in bridge.get("terms", []) if isinstance(term, dict) and (
        str(term.get("category", "")) in {"race", "race_name", "racecourse"}
        or str(term.get("id", "")).startswith("race.")
    )]

    write("tmp_race_inventory_summary.json", {
        "source_commit": load(ROOT / "work/translation_progress.json", {}).get("source_commit"),
        "merged_entry_count": merged_count,
        "pinned_unique_race_source_count": len(pinned_race_sources),
        "pinned_race_rows": sum(len(v) for v in pinned_race_sources.values()),
        "canonical_proper_race_term_count": len(race_terms),
        "global_proper_race_term_count": len(global_proper),
        "alias_conflict_count": len(alias_conflicts),
        "corpus_exact_race_source_count": len(exact_summary),
        "corpus_exact_race_gap_count": len(gaps),
        "corpus_exact_race_mismatch_count": len(mismatches),
        "race_community_term_count": len(community_race),
        "race_bridge_term_count": len(bridge_race),
        "racecourse_aliases_found": {alias: hits for alias, hits in sorted(course_hits.items())},
    })
    write("tmp_race_alias_conflicts.json", alias_conflicts)
    write("tmp_race_global_proper_terms.json", global_proper)
    write("tmp_race_exact_corpus.json", exact_summary)
    write("tmp_race_exact_gaps.json", gaps)
    write("tmp_race_exact_mismatches.json", mismatches)
    write("tmp_race_token_hits.json", token_summary)
    write("tmp_race_community_terms.json", community_race)
    write("tmp_race_bridge_terms.json", bridge_race)
    print(json.dumps(load(ROOT / "work/tmp_race_inventory_summary.json", {}), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
