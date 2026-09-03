from pathlib import Path


def _workflow_text() -> str:
    return Path(".github/workflows/aggregate-results.yml").read_text(encoding="utf-8")


def test_aggregate_workflow_discards_ephemeral_report_before_clean_tree_guard() -> None:
    text = _workflow_text()
    cleanup = "rm -f work/aggregation_report.json"
    stage = "git add localized_data index.json work/parallel"
    clean_guard = 'git status --porcelain'

    assert cleanup in text
    assert text.index(cleanup) < text.index(stage) < text.index(clean_guard)
