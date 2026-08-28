from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
stager = ROOT / "scripts/apply_condition_mood_hardening.py"
text = stager.read_text(encoding="utf-8")

old = "updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)"
new = "updated, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.S)"
if old not in text:
    raise RuntimeError("regex_once staging anchor missing")
text = text.replace(old, new, 1)

pattern = r'text = read\("tests/test_translation_guard.py"\).*?(?=# Remove the temporary workflow hook)'
replacement = r'''text = read("tests/test_translation_guard.py")
append = r'''


def test_guard_named_condition_is_path_scoped(tmp_path: Path) -> None:
    guard = _guard(tmp_path)
    guard.term_registry.setdefault("terms", []).append({
        "id": "condition.night_owl",
        "locked": True,
        "zh_cn": ["熬夜"],
        "target_vi": "Night Owl",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
    })
    guard.community.setdefault("terms", []).append({
        "id": "common.condition.night_owl",
        "source_aliases": ["熬夜"],
        "accepted": ["Night Owl"],
        "compact": [],
        "forbidden": ["Thức khuya"],
        "require_accepted": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
    })
    errors = guard.validate(
        "熬夜",
        "Thức khuya",
        source_path="text_data_dict.json",
        json_path=["142", "1"],
    )
    assert "community_forbidden:common.condition.night_owl" in errors
    assert "community_required:common.condition.night_owl" in errors
    assert guard.validate(
        "熬夜",
        "Night Owl",
        source_path="text_data_dict.json",
        json_path=["142", "1"],
    ) == []
    assert guard.validate(
        "今天熬夜了",
        "Hôm nay đã thức khuya",
        source_path="text_data_dict.json",
        json_path=["143", "1"],
    ) == []
'''
if "test_guard_named_condition_is_path_scoped" not in text:
    text = text.rstrip() + append + "\n"
write("tests/test_translation_guard.py", text)

'''
updated, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.S)
if count != 1:
    raise RuntimeError(f"guard-test staging replacement count={count}")
stager.write_text(updated, encoding="utf-8", newline="\n")

workflow_path = ROOT / ".github/workflows/sync-translation-review-plan.yml"
workflow = workflow_path.read_text(encoding="utf-8")
workflow = workflow.replace("            python scripts/fix_condition_hardening_stager.py\n", "")
workflow_path.write_text(workflow, encoding="utf-8", newline="\n")
Path(__file__).unlink()
print("condition hardening stager fixed")
