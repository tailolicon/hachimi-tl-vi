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
    """Return a prompt-only registry view with reviewed skill-title overrides applied.

    Canonical registry migration is owned by the curation/maintenance pipeline, but
    translation workers must not receive an obsolete locked skill title alongside
    an exact approved replacement from skill_name_style.json. This overlay keeps
    the checked-out canonical file untouched while making prompt precedence
    deterministic for exact reviewed examples.
    """
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
    """Inject only source-bridge rules relevant to the current zh-CN batch.

    These rules protect against literalizing a localization bridge (e.g. 金币 ->
    coins instead of the game's Monies) and against known zh-CN titles that lose
    JP imagery/meaning. Keeping the selection item-scoped avoids prompt bloat.
    """
    zh_sources = [
        entry.source_text
        for entry in entries
        if infer_source_language(entry) == "zh-CN"
    ]
    if not zh_sources or not isinstance(source_bridge_full, dict):
        return {"policy": source_bridge_full.get("policy", {}) if isinstance(source_bridge_full, dict) else {}, "terms": [], "untrusted_sources": []}

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


def build_messages(entries: Sequence[SourceEntry], glossary_dir: str | Path = "glossary") -> list[dict[str, str]]:
    glossary_dir = Path(glossary_dir)
    terminology = load_json(glossary_dir / "terminology.json", {})
    term_registry_full = load_json(glossary_dir / "term_registry.json", {})
    player_facing_terms = load_json(glossary_dir / "ui_community_terms.json", {})
    source_bridge_manual = load_json(glossary_dir / "source_bridge_terms.json", {})
    source_bridge_generated = load_json(glossary_dir / "source_bridge_risks.generated.json", {})
    source_bridge_full = merge_source_bridge_configs(source_bridge_manual, source_bridge_generated)
    skill_name_style = load_json(glossary_dir / "skill_name_style.json", {})
    observed_terms_full = load_json(glossary_dir / "observed_terms.json", {})
    characters_full = load_json(glossary_dir / "characters.json", {})
    speech_bible_full = load_json(glossary_dir / "speech_bible.json", {})
    speech_evidence_full = load_json(glossary_dir / "speech_evidence.json", {})
    style = load_json(glossary_dir / "style_rules.json", {})
    game_context = load_json(glossary_dir / "game_context.json", {})
    source_languages = sorted({infer_source_language(e) for e in entries})

    # Canonical and learned registries can grow to thousands of records. Inject
    # only core concepts plus records actually mentioned in this batch. Exact
    # reviewed skill-title examples are overlaid before compaction so workers do
    # not receive an obsolete locked title that conflicts with the new policy.
    effective_term_registry = apply_skill_name_style_overrides(term_registry_full, skill_name_style)
    term_registry = compact_term_registry(entries, effective_term_registry)
    source_bridge = compact_source_bridge_rules(entries, source_bridge_full)
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
5. Khi source là zh-CN, `source_bridge_terminology` là lớp bảo vệ bắt buộc chống dịch literal từ bản Trung. Nếu entry khớp `terms`, phải dùng một `accepted` player-facing form và tuyệt đối tránh `forbidden` calque (ví dụ 金币 -> Monies, 蹄铁 -> Cleat/Cleats, không phải xu/móng ngựa). Nếu entry khớp `untrusted_sources`, zh-CN đã biết là làm mất hoặc đổi nghĩa/hình tượng của JP: không được dịch nguyên chữ Trung; phải dùng bằng chứng JP/canonical context, và nếu chưa đủ bằng chứng thì giữ/defer an toàn thay vì đoán. Các risk tự sinh chỉ được promote từ curation evidence đã ghi rõ source zh-CN là lossy/interpretive; hãy coi `evidence` đi kèm là lý do bắt buộc phải kiểm tra JP.
6. Với TÊN RIÊNG của skill, áp dụng `skill_name_style`. Exact `canonical_examples` trong file này được ưu tiên hơn một skill-name target cũ xung đột trong `term_registry`. Bản `term_registry` trong payload đã được overlay các exact example này để không còn đưa cho bạn target cũ mâu thuẫn. Với skill chưa có exact example, dùng nhịp cô đọng của tên zh-CN làm naming-style reference và dùng JP/registry để bảo toàn hình tượng, wordplay, proper noun và phân biệt nghĩa.
7. Với các concept không bị rule 4-6 override, `term_registry` là canonical. Thuật ngữ `locked` phải dùng đúng `target_vi`.
8. `observed_terminology` là memory học từ entity đã được merge. Với source entity trùng chính xác và không mâu thuẫn với player-facing/source-bridge/skill-name/locked rule, tái sử dụng `target_vi` để các batch sau không đổi cách dịch.
9. Character registry trong payload đã được lọc theo batch nhưng là canonical: nếu có mapping thì bắt buộc dùng canonical thay vì dịch nghĩa tên zh-CN.
10. Thứ tự ưu tiên giọng nhân vật là: source wording + scene context > `speech_bible` curated > `speech_evidence` > style rule chung. `speech_evidence` chỉ là thống kê corpus để bảo toàn nhịp/punctuation, KHÔNG phải bằng chứng personality, quan hệ, dialect hay đại từ cố định.
11. Không ép một cặp đại từ tiếng Việt cố định cho nhân vật. Xưng hô phải dựa trên quan hệ, tuổi/seniority, scene và self-reference thực sự có trong source. Nếu source tự xưng bằng tên riêng (ví dụ Rice/Turbo), đừng tự đổi thành 'tôi'.
12. Common EN-version gameplay terms phải giữ English/Romanized theo `player_facing_terminology`: ví dụ Trainer, Speed, Stamina, Power, Guts, Wit, Aptitude, Turf, Dirt, Sprint, Mile, Medium, Long, Style, Front Runner/Pace Chaser/Late Surger/End Closer và compact alias khi UI chật.
13. Phân biệt Stamina stat với training energy gauge. Không dịch Stamina thành 'Thể lực' chỉ vì term_registry cũ còn mapping đó; cũng không tự đổi energy gauge thành Stamina.
14. Generic category label dùng English: Skill, Unique Skill, Evolution Skill. TÊN RIÊNG của từng skill thì Việt hóa theo `skill_name_style`: thường nhắm 2-4 đơn vị/từ trọng tâm khi nguồn ngắn, ưu tiên Hán-Việt nếu tự nhiên, giữ gimmick của tên gốc và không biến tên thành câu mô tả. Ví dụ exact policy: 弧线教授 -> Giáo Sư Cung Tuyến, 强攻策 -> Cường Công Kế.
15. Khi dịch tên skill từ zh-CN, học cấu trúc cô đọng của bản Trung (ví dụ 弯道加速○) thay vì kéo dài giải nghĩa; nhưng nếu zh-CN che mất reference/wordplay/proper noun thì phải dùng JP/registry để sửa. Không dùng UmaTL English translation text làm input.
16. Với hội thoại, giữ cá tính nhân vật và quan hệ xưng hô; không san phẳng mọi nhân vật về cùng một giọng.
17. Với UI/skill/race, ưu tiên ngắn gọn, rõ nghĩa, đúng player-facing terminology và chính xác cơ chế.
18. Nếu tên/thuật ngữ chưa có registry hoặc observed memory, không tự tạo bản dịch canonical mới. Dùng dạng nhận diện an toàn nhất; với named mechanic hoặc skill-name nuance chưa rõ, giữ/verify/defer thay vì semantic-calque bừa từ zh-CN.
19. Đầu ra PHẢI là JSON thuần theo schema: {\"translations\":[{\"id\":\"...\",\"text\":\"...\"}]}. Không markdown, không code fence, không trường thừa.
"""

    payload = {
        "target_language": "vi",
        "source_languages": source_languages,
        "game_context": game_context,
        "player_facing_terminology": player_facing_terms,
        "source_bridge_terminology": source_bridge,
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
