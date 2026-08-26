from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from typing import Any

from .model import SourceEntry

# Small concepts that are cheap and important enough to include in every batch.
CORE_TERM_IDS = {
    "world.umamusume",
    "world.tracen",
    "role.trainer",
    "system.training",
    "system.support_card",
    "stat.speed",
    "stat.stamina",
    "stat.power",
    "stat.guts",
    "stat.wisdom",
    "resource.energy",
    "state.motivation",
    "style.nige",
    "style.senko",
    "style.sashi",
    "style.oikomi",
    "style.dai_nige",
    "surface.turf",
    "surface.dirt",
}


def _flatten_text(value: Any) -> Iterable[str]:
    if value is None:
        return
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _flatten_text(item)
        return
    if isinstance(value, (list, tuple, set)):
        for item in value:
            yield from _flatten_text(item)
        return
    yield str(value)


def batch_haystack(entries: Sequence[SourceEntry]) -> str:
    parts: list[str] = []
    for entry in entries:
        parts.append(entry.source_text)
        parts.extend(_flatten_text(entry.context))
    return "\n".join(parts)


def _aliases(record: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for field in fields:
        value = record.get(field)
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            out.extend(str(x) for x in value if x)
    return out


def _mentioned(haystack: str, aliases: Iterable[str]) -> bool:
    for alias in aliases:
        alias = alias.strip()
        if alias and alias in haystack:
            return True
    return False


def select_relevant_terms(
    entries: Sequence[SourceEntry],
    registry: dict[str, Any],
    *,
    include_core: bool = True,
) -> list[dict[str, Any]]:
    haystack = batch_haystack(entries)
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for term in registry.get("terms", []):
        if not isinstance(term, dict):
            continue
        term_id = str(term.get("id", ""))
        aliases = _aliases(term, ("ja", "zh_cn", "zh_tw", "source_aliases"))
        if (include_core and term_id in CORE_TERM_IDS) or _mentioned(haystack, aliases):
            marker = term_id or json.dumps(term, ensure_ascii=False, sort_keys=True)
            if marker not in seen:
                selected.append(term)
                seen.add(marker)
    return selected


def _character_records(characters: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    raw = characters.get("characters", {})
    if not isinstance(raw, dict):
        return
    for key, record in raw.items():
        if isinstance(record, dict):
            yield str(key), record


def select_relevant_characters(
    entries: Sequence[SourceEntry], characters: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    haystack = batch_haystack(entries)
    selected: dict[str, dict[str, Any]] = {}
    for key, record in _character_records(characters):
        aliases = _aliases(record, ("ja", "zh_cn", "zh_tw", "aliases"))
        canonical = record.get("canonical")
        if canonical:
            aliases.append(str(canonical))
        if _mentioned(haystack, aliases):
            selected[key] = record
    return selected


def select_relevant_speech_profiles(
    entries: Sequence[SourceEntry],
    speech_data: dict[str, Any],
    selected_characters: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Select speech guidance relevant to a batch.

    Character IDs are the primary join key. A canonical-name fallback is kept so
    curated or evidence-only guidance can still be used if the character registry
    temporarily trails a newly added profile.
    """
    haystack = batch_haystack(entries)
    selected_ids = set(selected_characters or {})
    raw = speech_data.get("profiles", {})
    if not isinstance(raw, dict):
        return {}
    selected: dict[str, dict[str, Any]] = {}
    for key, profile in raw.items():
        if not isinstance(profile, dict):
            continue
        canonical = str(profile.get("canonical") or "").strip()
        if str(key) in selected_ids or (canonical and canonical in haystack):
            selected[str(key)] = profile
    return selected


def compact_term_registry(
    entries: Sequence[SourceEntry], registry: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": registry.get("schema_version"),
        "policy": registry.get("policy", {}),
        "terms": select_relevant_terms(entries, registry),
    }


def compact_observed_term_memory(
    entries: Sequence[SourceEntry], observed: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": observed.get("schema_version"),
        "policy": observed.get("policy", {}),
        "terms": select_relevant_terms(entries, observed, include_core=False),
    }


def compact_character_registry(
    entries: Sequence[SourceEntry], characters: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": characters.get("schema_version"),
        "default_rules": characters.get("default_rules", []),
        "characters": select_relevant_characters(entries, characters),
    }


def _compact_speech_data(
    entries: Sequence[SourceEntry],
    speech_data: dict[str, Any],
    selected_characters: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": speech_data.get("schema_version"),
        "policy": speech_data.get("policy", {}),
        "profiles": select_relevant_speech_profiles(
            entries, speech_data, selected_characters=selected_characters
        ),
    }


def compact_speech_bible(
    entries: Sequence[SourceEntry],
    speech_bible: dict[str, Any],
    selected_characters: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return _compact_speech_data(entries, speech_bible, selected_characters)


def compact_speech_evidence(
    entries: Sequence[SourceEntry],
    speech_evidence: dict[str, Any],
    selected_characters: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return _compact_speech_data(entries, speech_evidence, selected_characters)
