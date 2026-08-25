from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from hachimi_tl_vi.compiler import compile_localized_data
from hachimi_tl_vi.extractors.assets import import_asset_directory
from hachimi_tl_vi.extractors.localize import import_localize_dump
from hachimi_tl_vi.extractors.mdb import import_master_mdb
from hachimi_tl_vi.indexer import generate_index
from hachimi_tl_vi.model import Translation
from hachimi_tl_vi.qa import qa_pair
from hachimi_tl_vi.store import Store


def make_mdb(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE text_data(category INTEGER, `index` INTEGER, text TEXT);
        CREATE TABLE character_system_text(character_id INTEGER, voice_id INTEGER, text TEXT);
        CREATE TABLE race_jikkyo_comment(id INTEGER, text TEXT);
        CREATE TABLE race_jikkyo_message(id INTEGER, message TEXT);
        INSERT INTO text_data VALUES(1, 10, 'スピード');
        INSERT INTO character_system_text VALUES(1001, 7, 'おはよう！');
        INSERT INTO race_jikkyo_comment VALUES(2, '先頭です！');
        INSERT INTO race_jikkyo_message VALUES(3, 'ゴール！');
        """
    )
    conn.commit()
    conn.close()


def test_import_compile_and_index(tmp_path: Path):
    db = tmp_path / "tlvi.db"
    mdb = tmp_path / "master.mdb"
    make_mdb(mdb)
    localize_dump = tmp_path / "localize_dump.json"
    localize_dump.write_text(json.dumps({"100": "設定"}, ensure_ascii=False), encoding="utf-8")

    assets = tmp_path / "jp_assets"
    story = assets / "story/data/04/1001/storytimeline_test.json"
    story.parent.mkdir(parents=True)
    story.write_text(json.dumps({
        "title": "テスト物語",
        "text_block_list": [
            {"name": "少女", "text": "こんにちは"},
            {"name": "少女", "text": "行こう！", "choice_data_list": ["はい", "いいえ"]},
        ],
    }, ensure_ascii=False), encoding="utf-8")
    lyrics = assets / "lyrics/m9999_lyrics.json"
    lyrics.parent.mkdir(parents=True)
    lyrics.write_text(json.dumps({"1000": "走れ！"}, ensure_ascii=False), encoding="utf-8")

    out = tmp_path / "localized_data"
    out.mkdir()
    for name in ["config.json", "info.json"]:
        (out / name).write_text("{}", encoding="utf-8")

    with Store(db) as store:
        counts = import_master_mdb(mdb, store)
        assert counts["text_data"] == 1
        assert counts["character_system_text"] == 1
        assert counts["race_jikkyo_comment"] == 1
        assert counts["race_jikkyo_message"] == 1
        assert import_localize_dump(localize_dump, store) == 1
        asset_counts = import_asset_directory(assets, store)
        assert asset_counts["story"] >= 5
        assert asset_counts["lyrics"] == 1

        for entry in store.pending_entries():
            target = f"VI:{entry.source_text}"
            store.save_translation(Translation(entry.fingerprint, target, provider="test", model="test"))

        compiled = compile_localized_data(store, out)
        assert compiled["text_data"] == 1
        assert json.loads((out / "localize_dict.json").read_text(encoding="utf-8"))["100"] == "VI:設定"
        td = json.loads((out / "text_data_dict.json").read_text(encoding="utf-8"))
        assert td["1"]["10"] == "VI:スピード"
        compiled_story = json.loads((out / "assets/story/data/04/1001/storytimeline_test.json").read_text(encoding="utf-8"))
        assert compiled_story["title"] == "VI:テスト物語"
        assert compiled_story["text_block_list"][1]["choice_data_list"][0] == "VI:はい"
        compiled_lyrics = json.loads((out / "assets/lyrics/m9999_lyrics.json").read_text(encoding="utf-8"))
        assert compiled_lyrics["1000"] == "VI:走れ！"

    base = tmp_path / "index_base.json"
    base.write_text(json.dumps({"base_url": "x", "zip_url": "y", "zip_dir": "z"}), encoding="utf-8")
    idx_path = tmp_path / "index.json"
    index = generate_index(out, base, idx_path)
    assert index["files"]
    assert all(len(f["hash"]) == 64 for f in index["files"])


def test_placeholder_qa():
    assert qa_pair("速度{0}<color=red>X</color>", "Tốc độ {0}<color=red>X</color>")["ok"]
    result = qa_pair("速度{0}", "Tốc độ")
    assert not result["ok"]
    assert "placeholder_mismatch" in result["problems"]
