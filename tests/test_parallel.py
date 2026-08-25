from hachimi_tl_vi.parallel import set_json_path, structural_qa, task_group, task_id, task_slice


def test_structural_qa_preserves_runtime_tokens() -> None:
    source = "绑定{0}\n<color=#ff911c>1个</color>"
    target = "Liên kết {0}\n<color=#ff911c>1 mục</color>"
    assert structural_qa(source, target)["passed"] is True


def test_structural_qa_detects_missing_placeholder() -> None:
    source = "ID {0}: %s"
    target = "ID: %s"
    qa = structural_qa(source, target)
    assert qa["passed"] is False
    assert "brace_placeholders differ" in qa["errors"]


def test_set_json_path_builds_nested_containers() -> None:
    doc: dict[str, object] = {}
    set_json_path(doc, ["a", "b", 0, "text"], "Xin chào")
    assert doc == {"a": {"b": [{"text": "Xin chào"}]}}


def test_task_helpers() -> None:
    assert task_id(2, 3) == "batch-00002-s03"
    assert task_group(2) == "b0000"
    assert task_group(237) == "b0002"
    assert task_slice(80, 0, 20) == (0, 20)
    assert task_slice(80, 3, 20) == (60, 80)
    assert task_slice(40, 1, 20) == (20, 40)
