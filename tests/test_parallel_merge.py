from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_SPEC = spec_from_file_location(
    "merge_parallel_results",
    Path(__file__).resolve().parents[1] / "scripts" / "merge_parallel_results.py",
)
assert _SPEC is not None and _SPEC.loader is not None
_MOD = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

_set_path = _MOD._set_path
_validate_and_complete = _MOD._validate_and_complete
_recover_runtime_newlines = _MOD._recover_runtime_newlines


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


def test_recover_runtime_newline_only_for_exact_legacy_decode():
    source = "第一行\\n第二行"
    target = "Dòng một\nDòng hai"
    assert _recover_runtime_newlines(source, target) == "Dòng một\\nDòng hai"

    # Do not touch genuine source newlines or ambiguous newline-count changes.
    assert _recover_runtime_newlines("第一行\n第二行", target) is None
    assert _recover_runtime_newlines(source, "Một\nHai\nBa") is None


def test_complete_batch_recovers_decoded_runtime_newline_without_retranslation():
    source = {
        "source_commit": "upstream-sha",
        "entries": [
            {
                "uid": "runtime-newline",
                "source_text": "佩服！　两人的关系\\n是多么的理想啊……！！",
                "source_fingerprint": "runtime-fp",
                "source_path": "text_data_dict.json",
                "json_path": ["139", "1"],
            }
        ],
    }
    result = payload(
        "legacy",
        [
            tr(
                "runtime-newline",
                "runtime-fp",
                "Khâm phục quá!　Mối quan hệ của hai người\nthật lý tưởng biết bao……!!",
            )
        ],
    )

    resolved, diagnostics, claims = _validate_and_complete(
        source, SOURCE_REF, [result]
    )

    assert resolved == {
        "runtime-newline": "Khâm phục quá!　Mối quan hệ của hai người\\nthật lý tưởng biết bao……!!"
    }
    assert claims == {"legacy"}
    assert any("recovered_runtime_newline:runtime-newline" in item for item in diagnostics)
