import json
from pathlib import Path

from hachimi_tl_vi.translation_guard import TranslationQualityGuard


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "work/parallel/zhcn-67f8551f7780/results/b0007/batch-00765-s00.json"


def test_translation_quality_guard_batch_00765_s00() -> None:
    payload = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    assert payload["task_id"] == "batch-00765-s00"
    assert payload["translated_count"] == 20
    assert len(payload["entries"]) == 20

    guard = TranslationQualityGuard(REPO_ROOT / "glossary")
    failures: list[dict[str, object]] = []
    for entry in payload["entries"]:
        errors = guard.validate(
            entry["source_text"],
            entry["target_text"],
            uid=entry["uid"],
            source_path=entry["source_path"],
            json_path=entry["json_path"],
        )
        if errors:
            failures.append(
                {
                    "entry_index": entry["entry_index"],
                    "uid": entry["uid"],
                    "source_text": entry["source_text"],
                    "target_text": entry["target_text"],
                    "errors": errors,
                }
            )

    assert not failures, json.dumps(failures, ensure_ascii=False, indent=2)
