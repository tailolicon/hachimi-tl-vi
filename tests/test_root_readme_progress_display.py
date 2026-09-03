from scripts.update_root_readme_progress import build_block


def test_audit_progress_is_not_hidden_when_plan_regenerates_or_decisions_defer():
    progress = {
        "translation": {
            "source_total_entries": 1_158_825,
            "queued_entries": 131_560,
            "deferred_entries": 1_027_265,
            "translated_entries": 19_520,
            "remaining_queue_entries": 112_040,
        },
        "translation_review": {
            "candidates": 16_172,
            "scope_total_entries": 19_520,
            "total": 809,
            "completed": 0,
            "worker_percent": 0.0,
            "reviewed_items_current_plan": 0,
            "ledger_reviewed_entries": 4_100,
            "ledger_reviewed_percent": 21.0,
            "ledger_keep": 3_300,
            "ledger_revise": 48,
            "ledger_defer": 752,
            "resolved_entries": 3_348,
            "unresolved_entries": 16_172,
            "pending_merge": 0,
            "gate_enabled": True,
            "claims_allowed": True,
        },
        "ui_review": {"candidates": 6_455, "reviewed_items": 0},
        "curation": {
            "speech": {"merged_percent": 100.0},
            "terminology": {"merged_percent": 100.0},
        },
        "workers": {"active_total": 17},
    }
    state = {
        "phase": "retrospective_translation_review",
        "short_spawn_prompt": "Run tailolicon/hachimi-tl-vi/WORKER_START.md from main.",
        "canonical_parallelism": {"enabled": True},
        "active_task": {
            "title": "Retrospective translation Audit Round 1",
            "stage": "mass_review",
        },
        "roadmap": [],
    }

    block = build_block(progress, state)

    assert "4,100 / 19,520 entries reviewed at least once (21.00%)" in block
    assert "ledger keep/revise/defer **3,300/48/752**" in block
    assert "3,348 / 19,520 currently resolved (17.15%)" in block
    assert "current generation **0 / 809 batches (0.00%)**" in block
    assert "16,172 unresolved; gate **REVIEW ACTIVE / TRANSLATION OPEN**" in block
