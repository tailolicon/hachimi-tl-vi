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


def test_transcend_review_compatibility_runs_before_review_apply() -> None:
    workflow = (ROOT / ".github" / "workflows" / "sync-context.yml").read_text(encoding="utf-8")
    hardener_index = workflow.index("python scripts/harden_transcend_overdrive_finding.py")
    apply_index = workflow.index("python scripts/apply_terminology_reviews.py")
    assert hardener_index < apply_index


def test_uma_plan_review_compatibility_runs_before_review_apply() -> None:
    workflow = (ROOT / ".github" / "workflows" / "sync-context.yml").read_text(encoding="utf-8")
    hardener_index = workflow.index("python scripts/harden_uma_plan_finding.py")
    apply_index = workflow.index("python scripts/apply_terminology_reviews.py")
    assert hardener_index < apply_index


def test_translation_review_plan_sync_cannot_drop_finding_hardeners() -> None:
    workflow = (ROOT / ".github" / "workflows" / "sync-translation-review-plan.yml").read_text(encoding="utf-8")
    assert '"scripts/harden_*_finding.py"' in workflow
    assert '"tests/test_*_finding_hardening.py"' in workflow
    assert '"tests/test_*_context_guard_resolution.py"' in workflow
    refresh_index = workflow.index("python scripts/canonical_findings.py --repo-root . --refresh")
    hardener_index = workflow.index("for script in scripts/harden_*_finding.py; do")
    guard_index = workflow.index("python scripts/resolve_context_guard_findings.py")
    assert hardener_index < refresh_index < guard_index


def test_translation_review_plan_restores_all_post_refresh_context_resolvers() -> None:
    workflow = (ROOT / ".github" / "workflows" / "sync-translation-review-plan.yml").read_text(encoding="utf-8")
    resolver_commands = [
        "python scripts/resolve_scoped_canonical_overrides.py --repo-root .",
        "python scripts/resolve_context_guard_findings.py",
        "python scripts/resolve_running_style_narrative_finding.py",
        "python scripts/resolve_regenerated_super_long_distance_context_finding.py",
        "python scripts/resolve_regenerated_aoharu_ignition_finding.py",
        "python scripts/resolve_regenerated_initial_friendship_finding.py",
        "python scripts/resolve_regenerated_grand_live_performance_stats_findings.py",
    ]
    for command in resolver_commands:
        assert command in workflow
        script_path = command.split("python ", 1)[1].split(" --repo-root", 1)[0]
        assert f'"{script_path}"' in workflow

    refresh_index = workflow.index("python scripts/canonical_findings.py --repo-root . --refresh")
    batch_refresh_index = workflow.index(
        "python scripts/refresh_translation_review_batch_findings.py --repo-root ."
    )
    resolver_indexes = [workflow.index(command) for command in resolver_commands]
    assert refresh_index < min(resolver_indexes)
    assert max(resolver_indexes) < batch_refresh_index
