from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_sync_context_persists_hardener_review_locks() -> None:
    workflow = (ROOT / ".github" / "workflows" / "sync-context.yml").read_text(encoding="utf-8")
    commit_section = workflow.split("- name: Commit generated context if changed", 1)[1]
    assert "glossary/terminology_reviews.json" in commit_section


def test_sync_context_auto_triggers_and_runs_all_finding_hardeners() -> None:
    workflow = (ROOT / ".github" / "workflows" / "sync-context.yml").read_text(encoding="utf-8")
    assert '"scripts/harden_*_finding.py"' in workflow
    assert '"tests/test_*_finding_hardening.py"' in workflow
    assert "for script in scripts/harden_*_finding.py; do" in workflow
    assert 'python "$script"' in workflow
