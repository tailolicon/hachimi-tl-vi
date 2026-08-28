from __future__ import annotations

from copy import deepcopy
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


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def apply_skill_name_style_overrides(
    term_registry_full: dict[str, Any], skill_name_style: dict[str, Any]
) -> dict[str, Any]:
    """Return a prompt-only registry view with reviewed skill-title overrides applied."""
    registry = deepcopy(term_registry_full)
    terms = registry.get("terms")
    examples = skill_name_style.get("canonical_examples")
    if not isinstance(terms, list) or not isinstance(examples, list):
        return registry

    alias_to_example: dict[str, dict[str, Any]] = {}
    for raw_example in examples:
        if not isinstance(raw_example, dict):
            continue
        target = raw_example.get("target_vi")
        if not isinstance(target, str) or not target.strip():
            continue
        aliases: list[str] = []
        source_zh_cn = raw_example.get("source_zh_cn")
        if isinstance(source_zh_cn, str) and source_zh_cn:
            aliases.append(source_zh_cn)
        for field in ("ja", "zh_tw", "source_aliases"):
            aliases.extend(_strings(raw_example.get(field)))
        for alias in aliases:
            alias_to_example[alias] = raw_example

    policy_version = int(skill_name_style.get("policy_version", 0))
    for term in terms:
        if not isinstance(term, dict):
            continue
        aliases: list[str] = []
        for field in ("zh_cn", "ja", "zh_tw", "source_aliases"):
            aliases.extend(_strings(term.get(field)))
        matched_alias = next((alias for alias in aliases if alias in alias_to_example), None)
        if matched_alias is None:
            continue
        example = alias_to_example[matched_alias]
        term["target_vi"] = str(example["target_vi"])
        term["skill_name_style_override"] = {
            "source": "glossary/skill_name_style.json",
            "policy_version": policy_version,
            "matched_alias": matched_alias,
        }
    return registry


def merge_source_bridge_configs(manual: dict[str, Any], generated: dict[str, Any]) -> dict[str, Any]:
    """Merge hand-authored bridge terms with conservative curation-mined risks."""
    manual = manual if isinstance(manual, dict) else {}
    generated = generated if isinstance(generated, dict) else {}
    result = deepcopy(manual)
    result["terms"] = [item for item in manual.get("terms", []) if isinstance(item, dict)]

    risks: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for payload in (manual, generated):
        for risk in payload.get("untrusted_sources", []):
            if not isinstance(risk, dict):
                continue
            aliases = tuple(sorted(value.strip() for value in _strings(risk.get("zh_cn_exact")) if value.strip()))
            if not aliases or aliases in seen:
                continue
            seen.add(aliases)
            risks.append(risk)
    result["untrusted_sources"] = risks
    result["generated_summary"] = generated.get("summary", {})
    return result


def compact_source_bridge_rules(
    entries: Sequence[SourceEntry], source_bridge_full: dict[str, Any]
) -> dict[str, Any]:
    """Inject only source-bridge rules relevant to the current zh-CN batch."""
    zh_sources = [
        entry.source_text
        for entry in entries
        if infer_source_language(entry) == "zh-CN"
    ]
    if not zh_sources or not isinstance(source_bridge_full, dict):
        return {
            "policy": source_bridge_full.get("policy", {}) if isinstance(source_bridge_full, dict) else {},
            "terms": [],
            "untrusted_sources": [],
        }

    selected_terms: list[dict[str, Any]] = []
    for term in source_bridge_full.get("terms", []):
        if not isinstance(term, dict):
            continue
        aliases = _strings(term.get("zh_cn"))
        if any(
            alias and (source == alias or (len(alias) >= 2 and alias in source))
            for source in zh_sources
            for alias in aliases
        ):
            selected_terms.append(term)

    selected_untrusted: list[dict[str, Any]] = []
    stripped_sources = {source.strip() for source in zh_sources}
    for risk in source_bridge_full.get("untrusted_sources", []):
        if not isinstance(risk, dict):
            continue
        aliases = {alias.strip() for alias in _strings(risk.get("zh_cn_exact")) if alias.strip()}
        if stripped_sources.intersection(aliases):
            selected_untrusted.append(risk)

    return {
        "policy": source_bridge_full.get("policy", {}),
        "terms": selected_terms,
        "untrusted_sources": selected_untrusted,
    }


def compact_translation_regressions(
    entries: Sequence[SourceEntry], regression_full: dict[str, Any]
) -> dict[str, Any]:
    """Inject only previously rejected translations relevant to this batch.

    Regression memory is identity-first so a corrected story line does not become
    a global wording rule for every coincidentally identical sentence. Exact source
    matches are still included as evidence, while the hard merge guard decides the
    final blocking scope recorded in each regression entry.
    """
    if not isinstance(regression_full, dict):
        return {"policy": {}, "entries": []}
    uids = {entry.uid for entry in entries}
    sources = {entry.source_text for entry in entries}
    selected: list[dict[str, Any]] = []
    for item in regression_full.get("entries", []):
        if not isinstance(item, dict):
            continue
        uid = str(item.get("uid", ""))
        source = str(item.get("source_text", ""))
        if uid in uids or (source and source in sources):
            selected.append(item)
    return {
        "policy": regression_full.get("policy", {}),
        "entries": selected,
    }


def build_messages(entries: Sequence[SourceEntry], glossary_dir: str | Path = "glossary") -> list[dict[str, str]]:
    glossary_dir = Path(glossary_dir)
    terminology = load_json(glossary_dir / "terminology.json", {})
    term_registry_full = load_json(glossary_dir / "term_registry.json", {})
    player_facing_terms = load_json(glossary_dir / "ui_community_terms.json", {})
    source_bridge_manual = load_json(glossary_dir / "source_bridge_terms.json", {})
    source_bridge_generated = load_json(glossary_dir / "source_bridge_risks.generated.json", {})
    source_bridge_full = merge_source_bridge_configs(source_bridge_manual, source_bridge_generated)
    regression_full = load_json(glossary_dir / "translation_regressions.generated.json", {})
    skill_name_style = load_json(glossary_dir / "skill_name_style.json", {})
    observed_terms_full = load_json(glossary_dir / "observed_terms.json", {})
    characters_full = load_json(glossary_dir / "characters.json", {})
    speech_bible_full = load_json(glossary_dir / "speech_bible.json", {})
    speech_evidence_full = load_json(glossary_dir / "speech_evidence.json", {})
    style = load_json(glossary_dir / "style_rules.json", {})
    game_context = load_json(glossary_dir / "game_context.json", {})
    source_languages = sorted({infer_source_language(e) for e in entries})

    effective_term_registry = apply_skill_name_style_overrides(term_registry_full, skill_name_style)
    term_registry = compact_term_registry(entries, effective_term_registry)
    source_bridge = compact_source_bridge_rules(entries, source_bridge_full)
    regressions = compact_translation_regressions(entries, regression_full)
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
5. Khi source là zh-CN, `source_bridge_terminology` là lớp bảo vệ bắt buộc chống dịch literal từ bản Trung. Nếu entry khớp `terms`, phải dùng một `accepted` player-facing form và tuyệt đối tránh `forbidden` calque (ví dụ 金币 -> Monies, 蹄铁 -> Cleat/Cleats, không phải xu/móng ngựa). Nếu entry khớp `untrusted_sources`, zh-CN đã biết là làm mất hoặc đổi nghĩa/hình tượng của JP: không được dịch nguyên chữ Trung; phải dùng bằng chứng JP/canonical context, và nếu chưa đủ bằng chứng thì giữ/defer an toàn thay vì đoán.
6. `translation_regressions` là bộ nhớ lỗi đã được retrospective review xác nhận từ các bản dịch trước. Với entry khớp, TUYỆT ĐỐI không tái sử dụng bất kỳ `rejected_targets` nào. `approved_target` là bản sửa đã review để tham khảo/tái sử dụng khi source identity và context còn tương thích; canonical/player-facing/source-bridge rules vẫn có ưu tiên cao hơn nếu về sau được cập nhật.
7. Với TÊN RIÊNG của skill, áp dụng `skill_name_style`. Exact `canonical_examples` được ưu tiên hơn skill-name target cũ xung đột trong `term_registry`. Với skill chưa có exact example, dùng JP/registry để bảo toàn hình tượng, wordplay, proper noun và phân biệt nghĩa.
8. Với các concept không bị rule 4-7 override, `term_registry` là canonical. Thuật ngữ `locked` phải dùng đúng `target_vi`.
9. `observed_terminology` là memory học từ entity đã được merge. Với source entity trùng chính xác và không mâu thuẫn với các lớp ưu tiên cao hơn, tái sử dụng `target_vi` để các batch sau không đổi cách dịch.
10. Character registry trong payload là canonical: nếu có mapping thì bắt buộc dùng canonical thay vì dịch nghĩa tên zh-CN.
11. Thứ tự ưu tiên giọng nhân vật là: source wording + scene context > `speech_bible` curated > `speech_evidence` > style rule chung. `speech_evidence` chỉ là thống kê corpus để bảo toàn nhịp/punctuation, KHÔNG phải bằng chứng personality, quan hệ, dialect hay đại từ cố định.
12. Không ép một cặp đại từ tiếng Việt cố định cho nhân vật. Xưng hô phải dựa trên quan hệ, tuổi/seniority, scene và self-reference thực sự có trong source. Nếu source tự xưng bằng tên riêng (ví dụ Rice/Turbo), đừng tự đổi thành 'tôi'.
13. Common EN-version gameplay terms phải giữ English/Romanized theo `player_facing_terminology`: ví dụ Trainer, Speed, Stamina, Power, Guts, Wit, Aptitude, Turf, Dirt, Sprint, Mile, Medium, Long, Style, Front Runner/Pace Chaser/Late Surger/End Closer và compact alias khi UI chật.
14. Phân biệt Stamina stat với training energy gauge. Không dịch Stamina thành 'Thể lực'; cũng không tự đổi energy gauge thành Stamina.
15. Generic category label dùng English: Skill, Unique Skill, Evolution Skill. TÊN RIÊNG của từng skill thì Việt hóa theo `skill_name_style`: thường nhắm 2-4 đơn vị/từ trọng tâm khi nguồn ngắn, ưu tiên Hán-Việt nếu tự nhiên, giữ gimmick của tên gốc và không biến tên thành câu mô tả. Ví dụ exact policy: 弧线教授 -> Giáo Sư Cung Tuyến, 强攻策 -> Cường Công Kế.
16. Khi dịch tên skill từ zh-CN, học cấu trúc cô đọng của bản Trung thay vì kéo dài giải nghĩa; nhưng nếu zh-CN che mất reference/wordplay/proper noun thì phải dùng JP/registry để sửa. Không dùng UmaTL English translation text làm input.
17. Với hội thoại, giữ cá tính nhân vật và quan hệ xưng hô; không san phẳng mọi nhân vật về cùng một giọng.
18. Với UI/skill/race, ưu tiên ngắn gọn, rõ nghĩa, đúng player-facing terminology và chính xác cơ chế.
19. Nếu tên/thuật ngữ chưa có registry hoặc observed memory, không tự tạo bản dịch canonical mới. Với named mechanic hoặc skill-name nuance chưa rõ, verify/defer thay vì semantic-calque bừa từ zh-CN.
20. Trước khi trả kết quả, tự kiểm tra một vòng regression: số liệu, phủ định/điều kiện, tên riêng, canonical terminology, bridge risk, placeholder/tag/newline và mọi `rejected_targets` liên quan.
21. Đầu ra PHẢI là JSON thuần theo schema: {\"translations\":[{\"id\":\"...\",\"text\":\"...\"}]}. Không markdown, không code fence, không trường thừa.
"""

    payload = {
        "target_language": "vi",
        "source_languages": source_languages,
        "game_context": game_context,
        "player_facing_terminology": player_facing_terms,
        "source_bridge_terminology": source_bridge,
        "translation_regressions": regressions,
        "skill_name_style": skill_name_style,
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
