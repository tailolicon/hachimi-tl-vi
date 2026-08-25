from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Any

from ..model import SourceEntry


def load_json(path: str | Path, default: Any) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def build_messages(entries: Sequence[SourceEntry], glossary_dir: str | Path = "glossary") -> list[dict[str, str]]:
    glossary_dir = Path(glossary_dir)
    terminology = load_json(glossary_dir / "terminology.json", {})
    characters = load_json(glossary_dir / "characters.json", {})
    style = load_json(glossary_dir / "style_rules.json", {})

    system = """Bạn là bộ dịch JP→VI cho một bản dịch game độc lập.
Mục tiêu: tiếng Việt tự nhiên, chính xác, nhất quán và vừa giao diện game.
QUY TẮC BẮT BUỘC:
1. Chỉ dịch trường text; không giải thích, không thêm ghi chú.
2. Giữ NGUYÊN mọi placeholder/template/tag/markup, ví dụ: {0}, {name}, <color=...>, </color>, $(), %s, \\n khi chúng là token kỹ thuật.
3. Không tự bịa thông tin. Nếu câu mơ hồ, dùng context được cung cấp.
4. Tôn trọng glossary. Tên riêng và thuật ngữ đã khóa phải dùng đúng dạng Việt đã chỉ định.
5. Với hội thoại, giữ cá tính nhân vật và quan hệ xưng hô; không san phẳng mọi nhân vật về cùng một giọng.
6. Với UI/skill/race, ưu tiên ngắn gọn và rõ nghĩa.
7. Đầu ra PHẢI là JSON thuần theo schema: {"translations":[{"id":"...","text":"..."}]}.
Không markdown, không code fence, không trường thừa.
"""

    payload = {
        "target_language": "vi",
        "terminology": terminology,
        "character_rules": characters,
        "style_rules": style,
        "items": [
            {
                "id": e.uid,
                "kind": e.kind,
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
