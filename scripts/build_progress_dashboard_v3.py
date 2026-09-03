#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    import build_progress_dashboard as legacy
    import build_progress_dashboard_v2 as v2
except ModuleNotFoundError:
    from scripts import build_progress_dashboard as legacy
    from scripts import build_progress_dashboard_v2 as v2


def translation_review(root: Path, now: datetime, canonical_entries: int):
    active = legacy.load(root / "work/translation_review/active_plan.json")
    state = legacy.load(root / "work/parallel_state.json")
    gate = state.get("translation_review_gate") or {}
    scope_entries = int(gate.get("review_scope_entries") or canonical_entries)
    plan_id = active.get("plan_id")
    total = int(active.get("batch_count") or 0)
    candidate_count = int(active.get("candidate_count") or 0)
    plan_path = active.get("plan_path")
    plan = legacy.load(root / plan_path) if plan_path else {}
    plan_ids = {
        b.get("batch_id")
        for b in (plan.get("batches") or [])
        if isinstance(b, dict) and b.get("batch_id")
    }

    closed_ids: set[str] = set()
    applied_ids: set[str] = set()
    actions = Counter()
    merged_root = root / "work/translation_review/merged"
    for path in merged_root.glob("*.json") if merged_root.exists() else []:
        marker = legacy.load(path)
        if plan_id and marker.get("plan_id") != plan_id:
            continue
        bid = marker.get("batch_id")
        if bid:
            closed_ids.add(bid)
        if marker.get("status") == "merged":
            if bid:
                applied_ids.add(bid)
            for key, value in (marker.get("counts") or {}).items():
                if isinstance(value, int):
                    actions[key] += value

    completed = legacy.completion_ids(
        root / "work/translation_review/completions",
        plan_id=plan_id,
        allowed=plan_ids or None,
    )
    completed_ids = closed_ids | completed
    resolved_in_active_plan = actions["keep"] + actions["revise"]
    if bool(gate.get("enabled", False)):
        unresolved_entries = max(candidate_count - resolved_in_active_plan, 0)
    else:
        unresolved_entries = 0
    resolved_entries = max(min(scope_entries - unresolved_entries, scope_entries), 0)

    # reviewed_index is the durable cross-generation audit ledger. It intentionally
    # includes defer: defer means the item was reviewed but is not semantically
    # resolved. Keeping this metric separate prevents a regenerated active plan
    # from making completed human/worker review work appear to fall back to 0%.
    reviewed = legacy.load(root / "work/translation_review/reviewed_index.json")
    reviewed_entries = reviewed.get("entries") or {}
    ledger_actions = Counter()
    ledger_reviewed_entries = 0
    if isinstance(reviewed_entries, dict):
        for row in reviewed_entries.values():
            if not isinstance(row, dict):
                continue
            if int(row.get("policy_version") or 0) != int(active.get("policy_version") or gate.get("policy_version") or 0):
                continue
            action = str(row.get("action") or "")
            if action not in {"keep", "revise", "defer"}:
                continue
            ledger_reviewed_entries += 1
            ledger_actions[action] += 1
    ledger_reviewed_entries = min(ledger_reviewed_entries, scope_entries) if scope_entries > 0 else ledger_reviewed_entries

    return {
        "status": active.get("status") or ("active" if gate.get("enabled") else "idle"),
        "policy_version": int(active.get("policy_version") or gate.get("policy_version") or 0),
        "plan_id": plan_id,
        "candidates": candidate_count,
        "scope_total_entries": scope_entries,
        "total": total,
        "completed": len(completed_ids),
        "merged": len(applied_ids),
        "pending_merge": len(completed_ids - closed_ids),
        "worker_percent": legacy.percent(len(completed_ids), total),
        "merged_percent": legacy.percent(len(closed_ids), total),
        "keep": actions["keep"],
        "revise": actions["revise"],
        "defer": actions["defer"],
        "reviewed_items_current_plan": actions["keep"] + actions["revise"] + actions["defer"],
        "ledger_reviewed_entries": ledger_reviewed_entries,
        "ledger_reviewed_percent": legacy.percent(ledger_reviewed_entries, scope_entries),
        "ledger_keep": ledger_actions["keep"],
        "ledger_revise": ledger_actions["revise"],
        "ledger_defer": ledger_actions["defer"],
        "resolved_entries": resolved_entries,
        "unresolved_entries": unresolved_entries,
        "resolved_percent": legacy.percent(resolved_entries, scope_entries),
        "gate_enabled": bool(gate.get("enabled", False)),
        "claims_allowed": bool(gate.get("claims_allowed", not gate.get("enabled", False))),
        "claims": legacy.claims(root / "work/translation_review/claims", now),
    }


def markdown(data):
    text = v2.markdown(data)
    r = data["translation_review"]
    row = (
        f"| Translation review | **{r['ledger_reviewed_percent']:.2f}% reviewed** / "
        f"**{r['resolved_percent']:.2f}% resolved** | {r['ledger_reviewed_entries']:,} ledger items | "
        f"{r['completed']} current-gen batch | {r['total']} current-gen total | {r['pending_merge']} |\n"
    )
    text = text.replace(
        "| UI review | **{:.2f}%**".format(data["ui_review"]["percent"]),
        row + "| UI review | **{:.2f}%**".format(data["ui_review"]["percent"]),
        1,
    )
    ui_bar = f"`{legacy.bar(data['ui_review']['percent'])}` UI Review worker **{data['ui_review']['percent']:.2f}%**"
    review_bar = (
        f"`{legacy.bar(r['ledger_reviewed_percent'])}` Translation Review ledger **{r['ledger_reviewed_percent']:.2f}% reviewed at least once** "
        f"— resolved **{r['resolved_entries']:,}/{r['scope_total_entries']:,} entry "
        f"({r['resolved_percent']:.2f}%)**; current generation **{r['completed']}/{r['total']} batch ({r['worker_percent']:.2f}%)**"
    )
    text = text.replace(ui_bar, review_bar + "  \n" + ui_bar, 1)

    gate_label = "REVIEW ACTIVE / TRANSLATION OPEN" if r["gate_enabled"] and r["claims_allowed"] else "LOCKED" if r["gate_enabled"] else "OPEN"
    detail = (
        f"- Translation Review: **{r['ledger_reviewed_entries']:,} / {r['scope_total_entries']:,} frozen-scope entry "
        f"reviewed at least once = {r['ledger_reviewed_percent']:.2f}%** (ledger keep/revise/defer = "
        f"**{r['ledger_keep']}/{r['ledger_revise']}/{r['ledger_defer']}**); "
        f"**{r['resolved_entries']:,} resolved = {r['resolved_percent']:.2f}%**; current-plan keep/revise/defer = "
        f"**{r['keep']}/{r['revise']}/{r['defer']}**; new-translation gate = **{gate_label}**.\n"
    )
    text = text.replace("- Active claims:", detail + "- Active claims:", 1)
    text = text.replace(
        f"UI **{data['ui_review']['claims']['active']}**; tổng **{data['workers']['active_total']}**.",
        f"Translation Review **{r['claims']['active']}**, UI **{data['ui_review']['claims']['active']}**; tổng **{data['workers']['active_total']}**.",
        1,
    )
    return text


def html(data):
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hachimi TL-VI Progress</title><style>body{{font:16px system-ui;margin:0;background:#101114;color:#f3f4f6}}main{{max-width:1100px;margin:auto;padding:28px 18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}}.card{{background:#191b20;border:1px solid #2c3038;border-radius:16px;padding:18px}}.big{{font-size:30px;font-weight:750}}.muted{{color:#9ca3af}}.bar{{height:10px;background:#30343c;border-radius:99px;overflow:hidden;margin-top:12px}}.fill{{height:100%;background:#f3f4f6}}table{{width:100%;border-collapse:collapse}}td{{padding:9px 0;border-bottom:1px solid #2c3038}}td:last-child{{text-align:right}}</style></head><body><main><h1>Hachimi TL-VI Progress</h1><p class="muted" id="meta"></p><div class="grid" id="cards"></div><div class="card" style="margin-top:14px"><table id="details"></table></div></main><script id="data" type="application/json">{blob}</script><script>const d=JSON.parse(document.getElementById('data').textContent),p=x=>Number(x||0).toFixed(2)+'%';document.getElementById('meta').textContent=`${{d.generated_at}} • ${{d.workers.active_total}} active claims • Translation review gate: ${{d.translation_review.gate_enabled?(d.translation_review.claims_allowed?'REVIEW ACTIVE / TRANSLATION OPEN':'LOCKED'):'OPEN'}}`;const a=[['Translation',d.translation.worker_percent,`${{d.translation.batches_worker_completed}} completed • ${{d.translation.batches_translated}} merged`],['Translation Review',d.translation_review.ledger_reviewed_percent,`${{d.translation_review.ledger_reviewed_entries}} reviewed at least once • ${{d.translation_review.resolved_percent.toFixed(2)}}% resolved`],['Speech',d.curation.speech.percent,`${{d.curation.speech.completed}} completed • ${{d.curation.speech.merged}} merged`],['Terminology',d.curation.terminology.percent,`${{d.curation.terminology.completed}} completed • ${{d.curation.terminology.merged}} merged`],['UI Review',d.ui_review.percent,`${{d.ui_review.completed}} completed • ${{d.ui_review.merged}} merged`]];document.getElementById('cards').innerHTML=a.map(x=>`<div class="card"><div class="muted">${{x[0]}}</div><div class="big">${{p(x[1])}}</div><div>${{x[2]}}</div><div class="bar"><div class="fill" style="width:${{x[1]}}%"></div></div></div>`).join('');const r=[['Translation canonical',p(d.translation.queue_percent)],['Translation review ledger',p(d.translation_review.ledger_reviewed_percent)],['Translation review resolved',p(d.translation_review.resolved_percent)],['Current review generation',p(d.translation_review.worker_percent)],['Translation review gate',d.translation_review.gate_enabled?(d.translation_review.claims_allowed?'REVIEW ACTIVE / TRANSLATION OPEN':'LOCKED'):'OPEN'],['Speech canonical',p(d.curation.speech.merged_percent)],['Terminology canonical',p(d.curation.terminology.merged_percent)],['UI canonical',p(d.ui_review.merged_percent)],['Main commit',d.main_commit||'unknown']];document.getElementById('details').innerHTML=r.map(x=>`<tr><td>${{x[0]}}</td><td>${{x[1]}}</td></tr>`).join('');</script></body></html>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    root = args.repo_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    t = v2.translation(root, now)
    c = legacy.curation(root, now)
    u = legacy.ui(root, now)
    r = translation_review(root, now, int(t["translated_entries"]))
    data = {
        "schema_version": 3,
        "generated_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "main_commit": legacy.head(root),
        "translation": t,
        "translation_review": r,
        "curation": c,
        "ui_review": u,
        "workers": {
            "active_total": t["claims"]["active"] + c["claims"]["active"] + r["claims"]["active"] + u["claims"]["active"]
        },
    }
    (out / "progress.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "README.md").write_text(markdown(data), encoding="utf-8")
    (out / "index.html").write_text(html(data), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(json.dumps({
        "translation_worker": t["worker_percent"],
        "translation_merged": t["queue_percent"],
        "translation_review_ledger": r["ledger_reviewed_percent"],
        "translation_review_current_generation": r["worker_percent"],
        "translation_review_resolved": r["resolved_percent"],
        "translation_review_gate": "review_active_translation_open" if r["gate_enabled"] and r["claims_allowed"] else "locked" if r["gate_enabled"] else "open",
        "speech_worker": c["speech"]["percent"],
        "terminology_worker": c["terminology"]["percent"],
        "ui_worker": u["percent"],
        "active_claims": data["workers"]["active_total"],
    }, indent=2))


if __name__ == "__main__":
    main()
