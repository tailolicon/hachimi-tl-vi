from pathlib import Path

from hachimi_tl_vi.model import SourceEntry, Translation
from hachimi_tl_vi.store import Store


def test_translation_memory_reuses_unchanged_fingerprint(tmp_path: Path):
    with Store(tmp_path / "db.sqlite") as store:
        e = SourceEntry("x:1", "localize", "設定", {"id": "1"}, {"domain": "ui"})
        store.upsert_entries([e])
        store.save_translation(Translation(e.fingerprint, "Cài đặt", provider="test", model="test"))
        assert store.pending_entries() == []

        same = SourceEntry("x:1", "localize", "設定", {"id": "1"}, {"domain": "ui"})
        store.upsert_entries([same])
        assert store.pending_entries() == []

        changed = SourceEntry("x:1", "localize", "設定変更", {"id": "1"}, {"domain": "ui"})
        store.upsert_entries([changed])
        pending = store.pending_entries()
        assert len(pending) == 1
        assert pending[0].source_text == "設定変更"
