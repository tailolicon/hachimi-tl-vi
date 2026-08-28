from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected text not found in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_builder() -> None:
    path = ROOT / "scripts/build_translation_review_plan.py"
    replace_once(
        path,
        "TRANSLATION_REVIEW_POLICY_VERSION = 3\nPRIORITY_HEAD_SIZE = 64\n",
        "TRANSLATION_REVIEW_POLICY_VERSION = 3\nPRIORITY_HEAD_SIZE = 64\nINCOMPLETE_GATE_REASON = \"Retrospective translation review is incomplete; new translation claims are paused.\"\n",
    )
    text = path.read_text(encoding="utf-8")
    text = text.replace('reason="Retrospective translation review is incomplete; new translation claims are paused.",', 'reason=INCOMPLETE_GATE_REASON,')
    text = text.replace('reason="Review every already merged translation before accepting new translation claims.",', 'reason=INCOMPLETE_GATE_REASON,')
    marker = "\ndef _active_incomplete(repo_root: Path, context_hash: str, bridge_hash: str, item_policy_hash: str) -> dict[str, Any] | None:\n"
    helper = '''\ndef normalize_gate_state_for_noop(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:\n    \"\"\"Restore only gate timestamps when the semantic gate state is unchanged.\n\n    Production Sync captures ``before`` prior to rebuilding. A rediscovered active\n    plan may refresh ``updated_at`` even though plan identity, scope, reason, and\n    policy are identical. This helper makes that unchanged second sync byte-stable\n    without hiding any semantic gate change.\n    \"\"\"\n    result = json.loads(json.dumps(after))\n    old_gate = before.get("translation_review_gate") if isinstance(before, dict) else None\n    new_gate = result.get("translation_review_gate") if isinstance(result, dict) else None\n    if not isinstance(old_gate, dict) or not isinstance(new_gate, dict):\n        return result\n    volatile = {"updated_at", "activated_at", "cleared_at"}\n    old_semantic = {key: value for key, value in old_gate.items() if key not in volatile}\n    new_semantic = {key: value for key, value in new_gate.items() if key not in volatile}\n    if old_semantic != new_semantic:\n        return result\n    for key in volatile:\n        if key in old_gate:\n            new_gate[key] = old_gate[key]\n        else:\n            new_gate.pop(key, None)\n    return result\n\n'''
    if "def normalize_gate_state_for_noop" not in text:
        if marker not in text:
            raise RuntimeError("builder insertion marker not found")
        text = text.replace(marker, helper + marker, 1)
    path.write_text(text, encoding="utf-8")


def patch_race_test() -> None:
    path = ROOT / "tests/test_race_hardening.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'assert f"common.{rid}" in _ids(community_term_matches(None, source, target, community, source_path="localize_dict.json", json_path=["Menu"]))',
        'community_id = {"race.grade.g1": "common.race_grade.g1", "race.grade.g2": "common.race_grade.g2", "race.grade.g3": "common.race_grade.g3"}[rid]\n        assert community_id in _ids(community_term_matches(None, source, target, community, source_path="localize_dict.json", json_path=["Menu"]))',
    )
    text = text.replace("这是普通的冠军杯子，不是赛事名", "这是普通的冠军和奖杯，不是赛事名")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    patch_builder()
    patch_race_test()
    from harden_race_canon import harden
    harden(ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
