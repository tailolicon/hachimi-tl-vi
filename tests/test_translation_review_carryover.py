from __future__ import annotations

import scripts.build_translation_review_plan as builder


def _prior(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "policy_version": builder.TRANSLATION_REVIEW_POLICY_VERSION,
        "context_snapshot_sha256": "old-global-context",
        "source_fingerprint": "source-fp",
        "current_fingerprint": "current-fp",
        "action": "keep",
        "confidence": "high",
        "source_bridge_policy_sha256": "bridge-hash",
        "item_context_sha256": "item-context",
    }
    payload.update(overrides)
    return payload


def test_prior_review_survives_unrelated_global_context_change_when_item_context_is_unchanged() -> None:
    assert builder._prior_is_resolved(
        _prior(),
        context_hash="new-global-context",
        source_fp="source-fp",
        current_fp="current-fp",
        bridge_sensitive=False,
        bridge_hash="bridge-hash",
        item_context_hash="item-context",
    )


def test_prior_review_reopens_when_item_context_changes() -> None:
    assert not builder._prior_is_resolved(
        _prior(),
        context_hash="new-global-context",
        source_fp="source-fp",
        current_fp="current-fp",
        bridge_sensitive=False,
        bridge_hash="bridge-hash",
        item_context_hash="changed-item-context",
    )


def test_prior_review_without_item_context_still_requires_same_global_context() -> None:
    assert not builder._prior_is_resolved(
        _prior(item_context_sha256=None),
        context_hash="new-global-context",
        source_fp="source-fp",
        current_fp="current-fp",
        bridge_sensitive=False,
        bridge_hash="bridge-hash",
        item_context_hash=None,
    )


def test_bridge_sensitive_prior_reopens_when_bridge_policy_changes() -> None:
    assert not builder._prior_is_resolved(
        _prior(),
        context_hash="new-global-context",
        source_fp="source-fp",
        current_fp="current-fp",
        bridge_sensitive=True,
        bridge_hash="new-bridge-hash",
        item_context_hash="item-context",
    )
