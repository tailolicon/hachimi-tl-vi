from pathlib import Path


def _workflow_text() -> str:
    return Path(".github/workflows/merge-translation-review.yml").read_text(encoding="utf-8")


def test_review_merge_is_not_triggered_by_worker_checkpoint_or_completion_bursts() -> None:
    text = _workflow_text()
    assert 'work/translation_review/results/**' not in text
    assert 'work/translation_review/completions/**' not in text


def test_review_merge_has_bounded_watchdog_and_runtime() -> None:
    text = _workflow_text()
    assert 'cron: "*/5 * * * *"' in text
    assert "timeout-minutes: 10" in text
    assert "group: merge-translation-review" in text
    assert "cancel-in-progress: false" in text
