from scripts.aggregate_parallel_results import validate_result


def _valid_payloads(marker_count_field: str = "entry_count"):
    epoch = {
        "epoch": "zhcn-test",
        "source_commit": "source-sha",
        "source_queue_git_commit": "queue-sha",
        "task_size": 20,
    }
    source_entry = {
        "uid": "zhcn:test",
        "kind": "text_data",
        "source_text": "测试",
        "source_fingerprint": "fingerprint",
        "source_path": "text_data_dict.json",
        "json_path": ["1", "2"],
    }
    source_batch = {
        "batch": 1,
        "source_commit": "source-sha",
        "entries": [source_entry],
    }
    result_entry = {**source_entry, "entry_index": 0, "target_text": "Kiểm tra", "reviewed": True}
    result = {
        "status": "complete",
        "epoch": "zhcn-test",
        "task_id": "batch-00001-s00",
        "batch": 1,
        "shard": 0,
        "source_commit": "source-sha",
        "source_queue_git_commit": "queue-sha",
        "shard_start": 0,
        "shard_end_exclusive": 1,
        "translated_count": 1,
        "entries": [result_entry],
    }
    marker = {
        "epoch": "zhcn-test",
        "task_id": "batch-00001-s00",
        "source_commit": "source-sha",
        "source_queue_git_commit": "queue-sha",
        "qa_passed": True,
        marker_count_field: 1,
    }
    return epoch, marker, result, source_batch


def test_validator_accepts_canonical_completion_entry_count():
    epoch, marker, result, source_batch = _valid_payloads("entry_count")
    operations, errors = validate_result(
        epoch=epoch, marker=marker, result=result, source_batch=source_batch
    )
    assert len(operations) == 1
    assert errors == []


def test_validator_accepts_historical_translated_count_alias():
    epoch, marker, result, source_batch = _valid_payloads("translated_count")
    operations, errors = validate_result(
        epoch=epoch, marker=marker, result=result, source_batch=source_batch
    )
    assert len(operations) == 1
    assert errors == []


def test_validator_rejects_disagreeing_completion_count_fields():
    epoch, marker, result, source_batch = _valid_payloads("entry_count")
    marker["translated_count"] = 2
    _, errors = validate_result(
        epoch=epoch, marker=marker, result=result, source_batch=source_batch
    )
    assert "marker count fields disagree" in errors
