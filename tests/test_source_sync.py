import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "sync_hachimi_source.py"
spec = importlib.util.spec_from_file_location("sync_source", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_collect_and_batch(tmp_path):
    upstream = tmp_path / "upstream"
    ld = upstream / "localized_data"
    (ld / "assets/story/04").mkdir(parents=True)
    (ld / "localize_dict.json").write_text(json.dumps({"1": "开始", "2": "退出"}, ensure_ascii=False), encoding="utf-8")
    (ld / "assets/story/04/a.json").write_text(
        json.dumps({"text_block_list": [{"name": "特别周", "text": "一起加油吧！", "voice_id": "x"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    records, counts = mod.collect(upstream, "abc123")
    assert len(records) == 4
    assert records[0]["kind"] == "localize"
    assert sum(r["kind"] == "story" for r in records) == 2
    manifest = mod.write_batches(records, out, 2, "abc123", counts)
    assert manifest["total_batches"] == 1
    assert manifest["total_entries"] == 4
    assert manifest["queued_entries"] == 2
    assert manifest["deferred_entries"] == 2
    b1 = json.loads((out / "batch-00001.json").read_text(encoding="utf-8"))
    assert len(b1["entries"]) == 2
    assert b1["source_commit"] == "abc123"
    assert (out / "progress.template.json").exists()


def test_uid_stable_when_text_changes():
    a = mod.make_record(rel="localize_dict.json", path=["1"], source_text="开始", kind="localize", source_commit="a")
    b = mod.make_record(rel="localize_dict.json", path=["1"], source_text="开始游戏", kind="localize", source_commit="b")
    assert a["uid"] == b["uid"]
    assert a["source_fingerprint"] != b["source_fingerprint"]
