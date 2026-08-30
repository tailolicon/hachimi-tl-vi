from scripts.update_root_readme_progress import build_block


def test_audit_progress_is_not_hidden_when_all_merged_decisions_are_deferred():
    progress = {
        "translation": {
            "source_total_entries": 1_158_825,
            "queued_entries": 131_560,
            "deferred_entries": 1_027_265,
            "translated_entries": 19_520,
            "remaining_queue_entries": 112_040,
        },
        "translation_review": {
            "candidates": 19_520,
            "total": 976,
            "completed": 12,
            "worker_percent": 1.23,
            "reviewed_items_current_plan": 140,
            "resolved_entries": 0,
            "unresolved_entries": 19_520,
            "pending_merge": 5,
            "gate_enabled": True,
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

    assert "12 / 976 review batches completed (1.23%)" in block
    assert "140 merged item decisions in current plan" in block
    assert "0 / 19,520 entries resolved (0.00%)" in block
    assert "19,520 unresolved; gate **LOCKED**" in block
