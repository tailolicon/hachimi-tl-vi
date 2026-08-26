from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Any

from ..context_registry import (
    compact_character_registry,
    compact_observed_term_memory,
    compact_speech_bible,
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
    speech_bible_full = load_json(glossary_dir / "speech_bible.json", {})
    style = load_json(glossary_dir / "style_rules.json", {})
    game_context = load_json(glossary_dir / "game_context.json", {})
    source_languages = sorted({infer_source_language(e) for e in entries})

    # Canonical and learned registries can grow to thousands of records. Inject
    # only core concepts plus records actually mentioned in this batch.
    term_registry = compact_term_registry(entries, term_registry_full)
    observed_terms = compact_observed_term_memory(entries, observed_terms_full)
    characters = compact_character_registry(entries, characters_full)
    speech_bible = compact_speech_bible(
        entries,
        speech_bible_full,
        selected_characters=characters.get("characters", {}),
    )

    system = """Bạn là bộ dịch tiếng Việt chuyên cho Uma Musume Pretty Derby (server JP) và Hachimi Edge.
Nguồn có thể là tiếng Nhật hoặc bản zh-CN mới của nội dung server JP. Khi nguồn là zh-CN, hãy dùng nó như semantic bridge; tên riêng phải theo registry/canonical game context, KHÔNG dịch nghĩa tên nhân vật/ngựa tiếng Trung sang tiếng Việt.

QUY TẮC BẮT BUỘC:
1. Chỉ dịch trường text; không giải thích, không thêm translator note.
2. Giữ NGUYÊN mọi placeholder/template/tag/markup/runtime token, ví dụ {0}, {name}, <color=...>, </color>, $(), %s và mã máy.
3. Không tự bịa lore, quan hệ, cơ chế hoặc tên riêng. Khi mơ hồ, dùng game context + entry context.
4. `term_registry` là canonical. Thuật ngữ `locked` phải dùng đúng `target_vi` và có ưu tiên cao nhất.
5. `observed_terminology` là memory học từ entity đã được merge. Với source entity trùng chính xác và không mâu thuẫn với locked rule, tái sử dụng `target_vi` để các batch sau không đổi cách dịch.
6. Character registry trong payload đã được lọc theo batch nhưng là canonical: nếu có mapping thì bắt buộc dùng canonical thay vì dịch nghĩa tên zh-CN.
7. `speech_bible` chỉ chứa profile liên quan đến batch. Dùng nó để giữ register, nhịp và cá tính; nhưng wording/source scene luôn có ưu tiên cao hơn profile tổng quát.
8. Không ép một cặp đại từ tiếng Việt cố định cho nhân vật. Xưng hô phải dựa trên quan hệ, tuổi/seniority, scene và self-reference thực sự có trong source. Nếu source tự xưng bằng tên riêng (ví dụ Rice/Turbo), đừng tự đổi thành 'tôi'.
9. Phân biệt Stamina stat (スタミナ/耐力 = Thể lực) với training energy (体力 = Năng lượng).
10. Dùng cố định các running-style label Nige / Senko / Sashi / Oikomi / Dai Nige theo registry.
11. Với hội thoại, giữ cá tính nhân vật và quan hệ xưng hô; không san phẳng mọi nhân vật về cùng một giọng.
12. Với UI/skill/race, ưu tiên ngắn gọn, rõ nghĩa và chính xác cơ chế.
13. Nếu tên/thuật ngữ chưa có registry hoặc observed memory, không tự tạo bản dịch canonical mới. Dùng dạng nhận diện an toàn nhất và không dịch literal tên riêng tiếng Trung.
14. Đầu ra PHẢI là JSON thuần theo schema: {\"translations\":[{\"id\":\"...\",\"text\":\"...\"}]}. Không markdown, không code fence, không trường thừa.
"""

    payload = {
        "target_language": "vi",
        "source_languages": source_languages,
        "game_context": game_context,
        "term_registry": term_registry,
        "observed_terminology": observed_terms,
        "legacy_terminology": terminology,
        "character_rules": characters,
        "speech_bible": speech_bible,
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
