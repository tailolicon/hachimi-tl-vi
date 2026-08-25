from scripts.merge_parallel_results import _set_path, _validate_and_complete


SOURCE_REF = "snapshot-sha"
SOURCE = {
    "source_commit": "upstream-sha",
    "entries": [
        {
            "uid": "u1",
            "source_text": "你好 {0}",
            "source_fingerprint": "f1",
            "source_path": "localize_dict.json",
            "json_path": ["A"],
        },
        {
            "uid": "u2",
            "source_text": "重新启动",
            "source_fingerprint": "f2",
            "source_path": "localize_dict.json",
            "json_path": ["B"],
        },
    ],
}


def payload(claim, translations, *, source_commit="upstream-sha", source_ref=SOURCE_REF):
    return {
        "claim_id": claim,
        "source_commit": source_commit,
        "source_batch_ref": source_ref,
        "translations": translations,
        "_result_path": f"work/results/{claim}.json",
    }


def tr(uid, fingerprint, target):
    return {"uid": uid, "source_fingerprint": fingerprint, "target_text": target}


def test_set_path_builds_nested_dicts():
    doc = {}
    _set_path(doc, ["1", "2"], "Xin chào")
    assert doc == {"1": {"2": "Xin chào"}}


def test_complete_batch_accepts_valid_parts_and_ignores_stale_attempt():
    stale = payload(
        "old",
        [tr("u1", "f1", "Sai {0}")],
        source_commit="old-upstream",
        source_ref="old-snapshot",
    )
    good = payload(
        "new",
        [
            tr("u1", "f1", "Xin chào {0}"),
            tr("u2", "f2", "Khởi động lại"),
        ],
    )
    resolved, diagnostics, claims = _validate_and_complete(
        SOURCE, SOURCE_REF, [stale, good]
    )
    assert resolved == {"u1": "Xin chào {0}", "u2": "Khởi động lại"}
    assert claims == {"new"}
    assert any("ignored_source_commit_mismatch" in item for item in diagnostics)


def test_conflicting_valid_translations_block_merge():
    first = payload(
        "a",
        [tr("u1", "f1", "Xin chào {0}"), tr("u2", "f2", "Khởi động lại")],
    )
    second = payload("b", [tr("u1", "f1", "Chào bạn {0}")])
    resolved, diagnostics, _ = _validate_and_complete(
        SOURCE, SOURCE_REF, [first, second]
    )
    assert resolved is None
    assert "translation_conflict:u1" in diagnostics
