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


def test_aggregate_publish_tolerates_sustained_safe_main_churn() -> None:
    text = _workflow_text()

    assert "for attempt in $(seq 1 60); do" in text
    assert "git rebase origin/main && git push origin HEAD:main" in text
    assert "git push --force origin HEAD:main" not in text
    assert "sleep 0.2" in text
