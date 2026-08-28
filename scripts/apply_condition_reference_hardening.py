from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/enforce_player_facing_canon.py"
text = PATH.read_text(encoding="utf-8")

helper_anchor = '''CONDITION_CONTEXT = {
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
}


def load_json'''
helper_replacement = '''CONDITION_CONTEXT = {
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
}


def quoted_condition_aliases(values: list[str]) -> list[str]:
    """Aliases safe outside the Condition-name table because the source explicitly quotes the name."""
    result: list[str] = []
    for value in values:
        for left, right in (("「", "」"), ("“", "”"), ("『", "』"), ('"', '"')):
            alias = f"{left}{value}{right}"
            if alias not in result:
                result.append(alias)
    return result


def load_json'''
if helper_anchor not in text:
    raise RuntimeError("condition helper anchor missing")
text = text.replace(helper_anchor, helper_replacement, 1)

community_anchor = '''            **CONDITION_CONTEXT,
        })
    for spec in MOOD_LEVELS:
        records.append({'''
community_replacement = '''            **CONDITION_CONTEXT,
        })
        records.append({
            "id": "common." + spec["id"] + ".reference",
            "category": "condition_reference",
            "source_aliases": quoted_condition_aliases(spec["zh_cn"]),
            "preferred": spec["target"],
            "compact": [],
            "accepted": [spec["target"]],
            "forbidden": spec["forbidden"],
            "require_accepted": True,
            "basis": spec["note"] + " Outside the Condition-name table, match only an explicitly quoted occurrence of the exact source alias.",
            "invalidation_scope": "item",
            "match_mode": "contains",
        })
    for spec in MOOD_LEVELS:
        records.append({'''
if community_anchor not in text:
    raise RuntimeError("community Condition anchor missing")
text = text.replace(community_anchor, community_replacement, 1)

bridge_anchor = '''            "note": spec["note"] + " The zh-CN semantic label is not authoritative outside this guarded Condition slot.",
        })
    for spec in MOOD_LEVELS:
        upsert_by_id(terms, {'''
bridge_replacement = '''            "note": spec["note"] + " The zh-CN semantic label is not authoritative outside this guarded Condition slot.",
        })
        upsert_by_id(terms, {
            "id": spec["id"] + ".reference",
            "ja": [],
            "zh_cn": quoted_condition_aliases(spec["zh_cn"]),
            "preferred": spec["target"],
            "accepted": [spec["target"]],
            "forbidden": spec["forbidden"],
            "require_accepted": True,
            "match_mode": "contains",
            "note": spec["note"] + " Explicitly quoted source aliases are safe named-Condition references outside category 142; unquoted prose remains outside this rule.",
        })
    for spec in MOOD_LEVELS:
        upsert_by_id(terms, {'''
if bridge_anchor not in text:
    raise RuntimeError("source-bridge Condition anchor missing")
text = text.replace(bridge_anchor, bridge_replacement, 1)

PATH.write_text(text, encoding="utf-8", newline="\n")
print("quoted Condition reference hardening applied")
