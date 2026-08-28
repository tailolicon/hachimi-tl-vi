from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any


# Do not use \w here: in Python it includes CJK letters, which made a value in
# strings such as 最多60个 disappear from the source-side comparison. We only
# suppress numbers embedded in ASCII identifiers/placeholders while allowing
# normal CJK-adjacent gameplay values.
_NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_{])\d+(?:\.\d+)?%?")


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def _contains_any(text: str, values: list[str]) -> bool:
    normalized = _normalize(text)
    return any(_normalize(value) in normalized for value in values if value)


def _alias_matches(source: str, alias: str) -> bool:
    if not alias:
        return False
    if source == alias:
        return True
    return len(alias) >= 2 and alias in source


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def _merge_bridge_config(manual: Any, generated: Any) -> dict[str, Any]:
    manual = manual if isinstance(manual, dict) else {}
    generated = generated if isinstance(generated, dict) else {}
    risks: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for payload in (manual, generated):
        for raw in payload.get("untrusted_sources", []):
            if not isinstance(raw, dict):
                continue
            aliases = tuple(sorted(v.strip() for v in _strings(raw.get("zh_cn_exact")) if v.strip()))
            if not aliases or aliases in seen:
                continue
            seen.add(aliases)
            risks.append(raw)
    return {
        "terms": [item for item in manual.get("terms", []) if isinstance(item, dict)],
        "untrusted_sources": risks,
    }


class TranslationQualityGuard:
    """Hard regression firewall for future translations.

    The prompt is still the first line of defense, but generated/manual translations
    are not trusted merely because they are fluent. This guard enforces only rules
    that are deterministic enough to block a merge:

    * reviewed player-facing/canonical terminology;
    * known zh-CN bridge calques and lossy exact source titles;
    * exact reviewed skill titles;
    * verified character-name mappings;
    * exact translations previously rejected by retrospective review;
    * numeric-token preservation.

    Heuristic voice/nuance checks stay in review instead of becoming hard failures.
    """

    def __init__(self, glossary_dir: str | Path = "glossary") -> None:
        root = Path(glossary_dir)
        self.term_registry = _load_json(root / "term_registry.json", {"terms": []})
        self.community = _load_json(root / "ui_community_terms.json", {"terms": []})
        self.skill_style = _load_json(root / "skill_name_style.json", {"canonical_examples": []})
        self.characters = _load_json(root / "characters.json", {"characters": {}})
        manual = _load_json(root / "source_bridge_terms.json", {"terms": [], "untrusted_sources": []})
        generated = _load_json(root / "source_bridge_risks.generated.json", {"untrusted_sources": []})
        self.bridge = _merge_bridge_config(manual, generated)
        self.regressions = _load_json(root / "translation_regressions.generated.json", {"entries": []})

    def _community_matches(self, source: str, key: str | None) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for term in self.community.get("terms", []):
            if not isinstance(term, dict):
                continue
            exclusions = _strings(term.get("exclude_source_contains"))
            if exclusions and any(value in source for value in exclusions):
                continue
            prefixes = _strings(term.get("key_prefixes"))
            if prefixes and (key is None or not any(key.startswith(prefix) for prefix in prefixes)):
                continue
            aliases = _strings(term.get("source_aliases"))
            matched = [alias for alias in aliases if _alias_matches(source, alias)]
            if matched:
                matches.append({"term": term, "aliases": matched})
        return matches

    def _exact_skill_target(self, source: str) -> str | None:
        stripped = source.strip()
        for item in self.skill_style.get("canonical_examples", []):
            if not isinstance(item, dict):
                continue
            if str(item.get("source_zh_cn", "")).strip() != stripped:
                continue
            target = str(item.get("target_vi", "")).strip()
            if target:
                return target
        return None

    def validate(
        self,
        source: str,
        target: str,
        *,
        uid: str | None = None,
        key: str | None = None,
    ) -> list[str]:
        errors: list[str] = []
        source = str(source)
        target = str(target)

        source_numbers = Counter(_NUMBER_RE.findall(source))
        target_numbers = Counter(_NUMBER_RE.findall(target))
        if source_numbers != target_numbers:
            errors.append("numeric_token_mismatch")

        community_matches = self._community_matches(source, key)
        community_aliases = {
            alias
            for match in community_matches
            for alias in match["aliases"]
        }
        for match in community_matches:
            term = match["term"]
            accepted = list(dict.fromkeys(_strings(term.get("accepted")) + _strings(term.get("compact"))))
            forbidden = _strings(term.get("forbidden"))
            term_id = str(term.get("id", "unknown"))
            if forbidden and _contains_any(target, forbidden):
                errors.append(f"community_forbidden:{term_id}")
            if bool(term.get("require_accepted", True)) and accepted and not _contains_any(target, accepted):
                errors.append(f"community_required:{term_id}")

        for term in self.term_registry.get("terms", []):
            if not isinstance(term, dict) or not bool(term.get("locked")):
                continue
            exclusions = _strings(term.get("exclude_source_contains"))
            if exclusions and any(value in source for value in exclusions):
                continue
            expected = str(term.get("target_vi", "")).strip()
            if not expected:
                continue
            aliases = _strings(term.get("zh_cn"))
            matched = [alias for alias in aliases if _alias_matches(source, alias)]
            if not matched:
                continue
            # Documented precedence: player-facing community rules override an
            # older locked mapping for the same source alias.
            if any(alias in community_aliases for alias in matched):
                continue
            if not _contains_any(target, [expected]):
                errors.append(f"locked_term_required:{term.get('id', 'unknown')}")

        bridge_term_matched = False
        for term in self.bridge.get("terms", []):
            aliases = _strings(term.get("zh_cn"))
            if not any(_alias_matches(source, alias) for alias in aliases):
                continue
            bridge_term_matched = True
            term_id = str(term.get("id", "unknown"))
            accepted = _strings(term.get("accepted"))
            forbidden = _strings(term.get("forbidden"))
            if forbidden and _contains_any(target, forbidden):
                errors.append(f"source_bridge_forbidden:{term_id}")
            if bool(term.get("require_accepted", True)) and accepted and not _contains_any(target, accepted):
                errors.append(f"source_bridge_required:{term_id}")

        exact_skill = self._exact_skill_target(source)
        if exact_skill is not None and _normalize(target) != _normalize(exact_skill):
            errors.append("canonical_skill_title_mismatch")

        stripped_source = source.strip()
        for risk in self.bridge.get("untrusted_sources", []):
            if not isinstance(risk, dict):
                continue
            aliases = {v.strip() for v in _strings(risk.get("zh_cn_exact")) if v.strip()}
            if stripped_source not in aliases:
                continue
            # A later exact canonical skill rule or explicit bridge term resolves
            # the ambiguity. Otherwise automatic translation must stop instead of
            # guessing from the known-lossy zh-CN title.
            if exact_skill is None and not bridge_term_matched:
                errors.append(f"source_bridge_untrusted:{risk.get('id', 'unknown')}")

        character_map = self.characters.get("characters", {})
        if isinstance(character_map, dict):
            for char_id, raw in character_map.items():
                if not isinstance(raw, dict) or raw.get("identity_status") != "verified_game_id":
                    continue
                canonical = str(raw.get("canonical", "")).strip()
                if not canonical:
                    continue
                aliases = _strings(raw.get("zh_cn"))
                if not any(_alias_matches(source, alias) for alias in aliases):
                    continue
                if not _contains_any(target, [canonical]):
                    errors.append(f"character_name_required:{char_id}")

        for raw in self.regressions.get("entries", []):
            if not isinstance(raw, dict):
                continue
            regression_source = str(raw.get("source_text", ""))
            regression_uid = str(raw.get("uid", ""))
            if regression_source != source:
                continue
            if regression_uid and uid and regression_uid != uid:
                # Source-level rejected forms are still useful across repeated UI
                # strings, but UID-specific memory gets exact identity matching.
                scope = str(raw.get("scope", "uid"))
                if scope != "source":
                    continue
            rejected = _strings(raw.get("rejected_targets"))
            if any(_normalize(target) == _normalize(value) for value in rejected if value):
                errors.append(f"known_bad_regression:{raw.get('id', regression_uid or 'unknown')}")

        return list(dict.fromkeys(errors))
