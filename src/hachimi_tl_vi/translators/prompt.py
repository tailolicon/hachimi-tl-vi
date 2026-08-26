from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Any

from ..context_registry import (
    compact_character_registry,
    compact_observed_term_memory,
    compact_term_registry,
)
from ..model import SourceEntry


def load_json(path: str | Path, default: Any) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def infer_source_language(entry: SourceEntry) -> str:
    if isinstance(entry.context, dict):
        value = entry.context.get("source_language")
        if value:
            return str(value)
    uid = entry.uid.lower()
    if uid.startswith(("zhcn:", "zh-cn:")):
        return "zh-CN"
    if uid.startswith(("zhtw:", "zh-tw:")):
        return "zh-TW"
    return "ja"


def build_messages(entries: Sequence[SourceEntry], glossary_dir: str | Path = "glossary") -> list[dict[str, str]]:
    glossary_dir = Path(glossary_dir)
    terminology = load_json(glossary_dir / "terminology.json", {})
    term_registry_full = load_json(glossary_dir / "term_registry.json", {})
    observed_terms_full = load_json(glossary_dir / "observed_terms.json", {})
    characters_full = load_json(glossary_dir / "characters.json", {})
    style = load_json(glossary_dir / "style_rules.json", {})
    game_context = load_json(glossary_dir / "game_context.json", {})
    source_languages = sorted({infer_source_language(e) for e in entries})

    # Canonical and learned registries can grow to thousands of records. Inject
    # only core concepts plus records actually mentioned in this batch.
    term_registry = compact_term_registry(entries, term_registry_full)
    observed_terms = compact_observed_term_memory(entries, observed_terms_full)
    characters = compact_character_registry(entries, characters_full)

    system = """Bạn là bộ dịch tiếng Việt chuyên cho Uma Musume Pretty Derby (server JP) và Hachimi Edge.
Nguồn có thể là tiếng Nhật hoặc bản zh-CN mới của nội dung server JP. Khi nguồn là zh-CN, hãy dùng nó như semantic bridge; tên riêng phải theo registry/canonical game context, KHÔNG dịch nghĩa tên nhân vật/ngựa tiếng Trung sang tiếng Việt.

QUY TẮC BẮT BUỘC:
1. Chỉ dịch trường text; không giải thích, không thêm translator note.
2. Giữ NGUYÊN mọi placeholder/template/tag/markup/runtime token, ví dụ {0}, {name}, <color=...>, </color>, $(), %s và mã máy.
3. Không tự bịa lore, quan hệ, cơ chế hoặc tên riêng. Khi mơ hồ, dùng game context + entry context.
4. `term_registry` là canonical. Thuật ngữ `locked` phải dùng đúng `target_vi` và có ưu tiên cao nhất.
5. `observed_terminology` là memory học từ entity đã được merge. Với source entity trùng chính xác và không mâu thuẫn với locked rule, tái sử dụng `target_vi` để các batch sau không đổi cách dịch.
6. Character registry trong payload đã được lọc theo batch nhưng là canonical: nếu có mapping thì bắt buộc dùng canonical thay vì dịch nghĩa tên zh-CN.
7. Phân biệt Stamina stat (スタミナ/耐力 = Thể lực) với training energy (体力 = Năng lượng).
8. Dùng cố định các running-style label Nige / Senko / Sashi / Oikomi / Dai Nige theo registry.
9. Với hội thoại, giữ cá tính nhân vật và quan hệ xưng hô; không san phẳng mọi nhân vật về cùng một giọng.
10. Với UI/skill/race, ưu tiên ngắn gọn, rõ nghĩa và chính xác cơ chế.
11. Nếu tên/thuật ngữ chưa có registry hoặc observed memory, không tự tạo bản dịch canonical mới. Dùng dạng nhận diện an toàn nhất và không dịch literal tên riêng tiếng Trung.
12. Đầu ra PHẢI là JSON thuần theo schema: {\"translations\":[{\"id\":\"...\",\"text\":\"...\"}]}. Không markdown, không code fence, không trường thừa.
"""

    payload = {
        "target_language": "vi",
        "source_languages": source_languages,
        "game_context": game_context,
        "term_registry": term_registry,
        "observed_terminology": observed_terms,
        "legacy_terminology": terminology,
        "character_rules": characters,
        "style_rules": style,
        "items": [
            {
                "id": e.uid,
                "kind": e.kind,
                "source_language": infer_source_language(e),
                "source": e.source_text,
                "context": e.context,
            }
            for e in entries
        ],
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
