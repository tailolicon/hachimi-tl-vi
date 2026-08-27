from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Any

from ..context_registry import (
    compact_character_registry,
    compact_observed_term_memory,
    compact_speech_bible,
    compact_speech_evidence,
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
    player_facing_terms = load_json(glossary_dir / "ui_community_terms.json", {})
    observed_terms_full = load_json(glossary_dir / "observed_terms.json", {})
    characters_full = load_json(glossary_dir / "characters.json", {})
    speech_bible_full = load_json(glossary_dir / "speech_bible.json", {})
    speech_evidence_full = load_json(glossary_dir / "speech_evidence.json", {})
    style = load_json(glossary_dir / "style_rules.json", {})
    game_context = load_json(glossary_dir / "game_context.json", {})
    source_languages = sorted({infer_source_language(e) for e in entries})

    # Canonical and learned registries can grow to thousands of records. Inject
    # only core concepts plus records actually mentioned in this batch.
    term_registry = compact_term_registry(entries, term_registry_full)
    observed_terms = compact_observed_term_memory(entries, observed_terms_full)
    characters = compact_character_registry(entries, characters_full)
    selected_characters = characters.get("characters", {})
    speech_bible = compact_speech_bible(
        entries,
        speech_bible_full,
        selected_characters=selected_characters,
    )
    speech_evidence = compact_speech_evidence(
        entries,
        speech_evidence_full,
        selected_characters=selected_characters,
    )

    system = """Bạn là bộ dịch tiếng Việt chuyên cho Uma Musume Pretty Derby (server JP) và Hachimi Edge.
Nguồn có thể là tiếng Nhật hoặc bản zh-CN mới của nội dung server JP. Khi nguồn là zh-CN, hãy dùng nó như semantic bridge; tên riêng phải theo registry/canonical game context, KHÔNG dịch nghĩa tên nhân vật/ngựa tiếng Trung sang tiếng Việt.

QUY TẮC BẮT BUỘC:
1. Chỉ dịch trường text; không giải thích, không thêm translator note.
2. Giữ NGUYÊN mọi placeholder/template/tag/markup/runtime token, ví dụ {0}, {name}, <color=...>, </color>, $(), %s và mã máy.
3. Không tự bịa lore, quan hệ, cơ chế hoặc tên riêng. Khi mơ hồ, dùng game context + entry context.
4. `player_facing_terminology` là lớp ưu tiên CAO NHẤT cho common gameplay/UI terms và named mechanic/event được liệt kê. Khi nó xung đột với một mapping Việt hóa cũ trong `term_registry`, dùng accepted English/Romanized form trong `player_facing_terminology`.
5. Với các concept không bị rule 4 override, `term_registry` là canonical. Thuật ngữ `locked` phải dùng đúng `target_vi`.
6. `observed_terminology` là memory học từ entity đã được merge. Với source entity trùng chính xác và không mâu thuẫn với player-facing/locked rule, tái sử dụng `target_vi` để các batch sau không đổi cách dịch.
7. Character registry trong payload đã được lọc theo batch nhưng là canonical: nếu có mapping thì bắt buộc dùng canonical thay vì dịch nghĩa tên zh-CN.
8. Thứ tự ưu tiên giọng nhân vật là: source wording + scene context > `speech_bible` curated > `speech_evidence` > style rule chung. `speech_evidence` chỉ là thống kê corpus để bảo toàn nhịp/punctuation, KHÔNG phải bằng chứng personality, quan hệ, dialect hay đại từ cố định.
9. Không ép một cặp đại từ tiếng Việt cố định cho nhân vật. Xưng hô phải dựa trên quan hệ, tuổi/seniority, scene và self-reference thực sự có trong source. Nếu source tự xưng bằng tên riêng (ví dụ Rice/Turbo), đừng tự đổi thành 'tôi'.
10. Common EN-version gameplay terms phải giữ English/Romanized theo `player_facing_terminology`: ví dụ Trainer, Speed, Stamina, Power, Guts, Wit, Aptitude, Turf, Dirt, Sprint, Mile, Medium, Long, Style, Front Runner/Pace Chaser/Late Surger/End Closer và compact alias khi UI chật.
11. Phân biệt Stamina stat với training energy gauge. Không dịch Stamina thành 'Thể lực' chỉ vì term_registry cũ còn mapping đó; cũng không tự đổi energy gauge thành Stamina.
12. Generic category label dùng English: Skill, Unique Skill, Evolution Skill. Nhưng TÊN RIÊNG của từng skill phải Việt hóa như tên kỹ năng game: ưu tiên Hán-Việt nếu tự nhiên và có khí chất; nếu không thì dùng tên Việt ngắn, giàu hình ảnh, kiểu localization skill của game thương mại/LoL. Không biến tên skill thành câu mô tả dài.
13. Với hội thoại, giữ cá tính nhân vật và quan hệ xưng hô; không san phẳng mọi nhân vật về cùng một giọng.
14. Với UI/skill/race, ưu tiên ngắn gọn, rõ nghĩa, đúng player-facing terminology và chính xác cơ chế.
15. Nếu tên/thuật ngữ chưa có registry hoặc observed memory, không tự tạo bản dịch canonical mới. Dùng dạng nhận diện an toàn nhất; với named mechanic chưa rõ, giữ/verify thay vì semantic-calque từ zh-CN.
16. Đầu ra PHẢI là JSON thuần theo schema: {\"translations\":[{\"id\":\"...\",\"text\":\"...\"}]}. Không markdown, không code fence, không trường thừa.
"""

    payload = {
        "target_language": "vi",
        "source_languages": source_languages,
        "game_context": game_context,
        "player_facing_terminology": player_facing_terms,
        "term_registry": term_registry,
        "observed_terminology": observed_terms,
        "legacy_terminology": terminology,
        "character_rules": characters,
        "speech_bible": speech_bible,
        "speech_evidence": speech_evidence,
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
