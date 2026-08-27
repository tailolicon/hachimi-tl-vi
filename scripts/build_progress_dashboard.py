#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def load(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {} if default is None else default


def percent(done, total):
    return round(done * 100 / total, 2) if total else 0.0


def dt(value):
    if not isinstance(value, str):
        return None
    try:
        value = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(value)
        return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except ValueError:
        return None


def claims(root, now):
    out = {"active": 0, "expired": 0, "unknown": 0}
    for path in Path(root).rglob("*.json") if Path(root).exists() else []:
        expires = dt(load(path).get("expires_at"))
        if expires is None:
            out["unknown"] += 1
        elif expires > now:
            out["active"] += 1
        else:
            out["expired"] += 1
    return out


def completion_ids(root, plan_id=None, allowed=None):
    root = Path(root)
    found = set()
    if not root.exists():
        return found
    allowed = set(allowed or [])
    for batch_dir in root.iterdir():
        if not batch_dir.is_dir():
            continue
        bid = batch_dir.name
        if allowed and bid not in allowed:
            continue
        for path in batch_dir.glob("*.json"):
            marker = load(path)
            if plan_id and marker.get("plan_id") != plan_id:
                continue
            marker_bid = marker.get("batch_id")
            if marker_bid and marker_bid != bid:
                continue
            found.add(bid)
            break
    return found


def head(root):
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return os.getenv("GITHUB_SHA")


def translation(root, now):
    p = load(root / "work/translation_progress.json")
    total, queued, done = (int(p.get(k) or 0) for k in ("source_total_entries", "queued_entries", "translated_entries"))
    batches = int(p.get("queue_total_batches") or 0)
    merged_batch_numbers = {int(x) for x in (p.get("translated_batches") or [])}
    completed_batch_numbers = set(merged_batch_numbers)
    completion_root = root / "work/completions"
    if completion_root.exists():
        for child in completion_root.iterdir():
            if not child.is_dir() or not any(child.glob("*.json")):
                continue
            m = re.fullmatch(r"batch-(\d+)", child.name)
            if m:
                completed_batch_numbers.add(int(m.group(1)))
    worker_completed_batches = len(completed_batch_numbers)
    estimated_worker_entries = min(queued, worker_completed_batches * int(p.get("batch_size") or 80))
    return {
        "source_total_entries": total,
        "queued_entries": queued,
        "deferred_entries": int(p.get("deferred_entries") or 0),
        "translated_entries": done,
        "remaining_queue_entries": max(queued - done, 0),
        "raw_percent": percent(done, total),
        "queue_percent": percent(done, queued),
        "batches_total": batches,
        "batches_translated": len(merged_batch_numbers),
        "batches_worker_completed": worker_completed_batches,
        "batches_pending_merge": max(worker_completed_batches - len(merged_batch_numbers), 0),
        "worker_percent": percent(worker_completed_batches, batches),
        "estimated_worker_entries": estimated_worker_entries,
        "batches_reviewed": len(p.get("reviewed_batches") or []),
        "batches_qa": len(p.get("qa_passed_batches") or []),
        "claims": claims(root / "work/claims", now),
    }


def curation(root, now):
    active = load(root / "work/curation/active_plan.json")
    plan_id, plan_path = active.get("plan_id"), active.get("plan_path")
    plan = load(root / plan_path) if plan_path else {}
    speech, terms = plan.get("speech_batches") or [], plan.get("terminology_batches") or []
    speech_ids = {b.get("batch_id") for b in speech if isinstance(b, dict) and b.get("batch_id")}
    term_ids = {b.get("batch_id") for b in terms if isinstance(b, dict) and b.get("batch_id")}
    speech_sizes = {b["batch_id"]: len(b.get("items") or []) for b in speech if isinstance(b, dict) and b.get("batch_id")}
    sm, tm, profiles, actions = set(), set(), 0, Counter()
    merged = root / "work/curation/merged"
    for path in merged.glob("*.json") if merged.exists() else []:
        marker = load(path)
        if plan_id and marker.get("plan_id") != plan_id:
            continue
        bid = marker.get("batch_id", "")
        if bid in speech_ids:
            sm.add(bid)
            profiles += speech_sizes.get(bid, 0)
        elif bid in term_ids:
            tm.add(bid)
            result_path = marker.get("result_path")
            result = load(root / result_path) if result_path else {}
            for d in result.get("decisions") or []:
                if isinstance(d, dict) and d.get("action"):
                    actions[d["action"]] += 1
    completed = completion_ids(root / "work/curation/completions", plan_id=plan_id, allowed=speech_ids | term_ids)
    sc = sm | (completed & speech_ids)
    tc = tm | (completed & term_ids)
    return {
        "plan_id": plan_id,
        "speech": {
            "total": len(speech), "completed": len(sc), "merged": len(sm),
            "pending_merge": len(sc - sm), "percent": percent(len(sc), len(speech)),
            "merged_percent": percent(len(sm), len(speech)), "profiles": profiles,
        },
        "terminology": {
            "total": len(terms), "completed": len(tc), "merged": len(tm),
            "pending_merge": len(tc - tm), "percent": percent(len(tc), len(terms)),
            "merged_percent": percent(len(tm), len(terms)),
            "decisions": sum(actions.values()), "lock": actions["lock"], "defer": actions["defer"], "ignore": actions["ignore"],
        },
        "claims": claims(root / "work/curation/claims", now),
    }


def ui(root, now):
    active = load(root / "work/ui_review/active_plan.json")
    plan_id, total = active.get("plan_id"), int(active.get("batch_count") or 0)
    plan_path = active.get("plan_path")
    plan = load(root / plan_path) if plan_path else {}
    plan_ids = {b.get("batch_id") for b in (plan.get("batches") or []) if isinstance(b, dict) and b.get("batch_id")}
    merged_ids, actions = set(), Counter()
    merged = root / "work/ui_review/merged"
    for path in merged.glob("*.json") if merged.exists() else []:
        marker = load(path)
        if plan_id and marker.get("plan_id") != plan_id:
            continue
        bid = marker.get("batch_id")
        if bid:
            merged_ids.add(bid)
        for k, v in (marker.get("counts") or {}).items():
            if isinstance(v, int):
                actions[k] += v
    completed = completion_ids(root / "work/ui_review/completions", plan_id=plan_id, allowed=plan_ids or None)
    completed_ids = merged_ids | completed
    return {
        "plan_id": plan_id,
        "candidates": int(active.get("candidate_count") or 0),
        "total": total,
        "completed": len(completed_ids),
        "merged": len(merged_ids),
        "pending_merge": len(completed_ids - merged_ids),
        "percent": percent(len(completed_ids), total),
        "merged_percent": percent(len(merged_ids), total),
        "keep": actions["keep"], "revise": actions["revise"], "defer": actions["defer"],
        "reviewed_items": actions["keep"] + actions["revise"] + actions["defer"],
        "claims": claims(root / "work/ui_review/claims", now),
    }


def bar(p, width=20):
    n = round(max(0, min(100, p)) * width / 100)
    return "█" * n + "░" * (width - n)


def markdown(d):
    t, c, u = d["translation"], d["curation"], d["ui_review"]
    return f'''# Hachimi TL-VI Progress

> Cập nhật tự động từ `main`: **{d['generated_at']}**. `Completed` = worker đã xong; `Merged` = đã nhập canonical.

| Pipeline | Worker progress | Completed | Merged | Tổng | Pending merge |
|---|---:|---:|---:|---:|---:|
| Translation | **{t['worker_percent']:.2f}%** | {t['batches_worker_completed']} batch | {t['batches_translated']} batch | {t['batches_total']} | {t['batches_pending_merge']} |
| Speech curation | **{c['speech']['percent']:.2f}%** | {c['speech']['completed']} batch | {c['speech']['merged']} batch | {c['speech']['total']} | {c['speech']['pending_merge']} |
| Terminology curation | **{c['terminology']['percent']:.2f}%** | {c['terminology']['completed']} batch | {c['terminology']['merged']} batch | {c['terminology']['total']} | {c['terminology']['pending_merge']} |
| UI review | **{u['percent']:.2f}%** | {u['completed']} batch | {u['merged']} batch | {u['total']} | {u['pending_merge']} |

`{bar(t['worker_percent'])}` Translation worker **{t['worker_percent']:.2f}%**  
`{bar(c['speech']['percent'])}` Speech worker **{c['speech']['percent']:.2f}%**  
`{bar(c['terminology']['percent'])}` Terminology worker **{c['terminology']['percent']:.2f}%**  
`{bar(u['percent'])}` UI Review worker **{u['percent']:.2f}%**

## Canonical / phát hành

- Translation canonical: **{t['translated_entries']:,} / {t['queued_entries']:,} entry = {t['queue_percent']:.2f}%**; raw source coverage **{t['raw_percent']:.2f}%**.
- Speech merged: **{c['speech']['merged']} / {c['speech']['total']} = {c['speech']['merged_percent']:.2f}%**, tương ứng **{c['speech']['profiles']} profile** đã nhập.
- Terminology merged: **{c['terminology']['merged']} / {c['terminology']['total']} = {c['terminology']['merged_percent']:.2f}%**; {c['terminology']['decisions']} decision canonical — lock/defer/ignore = **{c['terminology']['lock']}/{c['terminology']['defer']}/{c['terminology']['ignore']}**.
- UI Review merged: **{u['merged']} / {u['total']} = {u['merged_percent']:.2f}%**; keep/revise/defer = **{u['keep']}/{u['revise']}/{u['defer']}**.
- Active claims: translation **{t['claims']['active']}**, curation **{c['claims']['active']}**, UI **{u['claims']['active']}**; tổng **{d['workers']['active_total']}**.
- Main snapshot: `{d['main_commit'] or 'unknown'}`.

Machine-readable: [`progress.json`](./progress.json) · HTML: [`index.html`](./index.html)
'''


def html(d):
    blob = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hachimi TL-VI Progress</title><style>body{{font:16px system-ui;margin:0;background:#101114;color:#f3f4f6}}main{{max-width:1000px;margin:auto;padding:28px 18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}.card{{background:#191b20;border:1px solid #2c3038;border-radius:16px;padding:18px}}.big{{font-size:30px;font-weight:750}}.muted{{color:#9ca3af}}.bar{{height:10px;background:#30343c;border-radius:99px;overflow:hidden;margin-top:12px}}.fill{{height:100%;background:#f3f4f6}}table{{width:100%;border-collapse:collapse}}td{{padding:9px 0;border-bottom:1px solid #2c3038}}td:last-child{{text-align:right}}</style></head><body><main><h1>Hachimi TL-VI Progress</h1><p class="muted" id="meta"></p><div class="grid" id="cards"></div><div class="card" style="margin-top:14px"><table id="details"></table></div></main><script id="data" type="application/json">{blob}</script><script>const d=JSON.parse(document.getElementById('data').textContent),n=x=>Number(x||0).toLocaleString('vi-VN'),p=x=>Number(x||0).toFixed(2)+'%';document.getElementById('meta').textContent=`${{d.generated_at}} • ${{d.workers.active_total}} active claims • Completed = worker done, Merged = canonical`;const a=[['Translation',d.translation.worker_percent,`${{d.translation.batches_worker_completed}} completed • ${{d.translation.batches_translated}} merged`],['Speech',d.curation.speech.percent,`${{d.curation.speech.completed}} completed • ${{d.curation.speech.merged}} merged`],['Terminology',d.curation.terminology.percent,`${{d.curation.terminology.completed}} completed • ${{d.curation.terminology.merged}} merged`],['UI Review',d.ui_review.percent,`${{d.ui_review.completed}} completed • ${{d.ui_review.merged}} merged`]];document.getElementById('cards').innerHTML=a.map(x=>`<div class="card"><div class="muted">${{x[0]}}</div><div class="big">${{p(x[1])}}</div><div>${{x[2]}}</div><div class="bar"><div class="fill" style="width:${{x[1]}}%"></div></div></div>`).join('');const r=[['Translation canonical',p(d.translation.queue_percent)],['Speech canonical',p(d.curation.speech.merged_percent)],['Terminology canonical',p(d.curation.terminology.merged_percent)],['UI canonical',p(d.ui_review.merged_percent)],['Pending merge T/S/Term/UI',`${{d.translation.batches_pending_merge}} / ${{d.curation.speech.pending_merge}} / ${{d.curation.terminology.pending_merge}} / ${{d.ui_review.pending_merge}}`],['Main commit',d.main_commit||'unknown']];document.getElementById('details').innerHTML=r.map(x=>`<tr><td>${{x[0]}}</td><td>${{x[1]}}</td></tr>`).join('');</script></body></html>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    root = args.repo_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    t, c, u = translation(root, now), curation(root, now), ui(root, now)
    data = {
        "schema_version": 2,
        "generated_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "main_commit": head(root),
        "translation": t,
        "curation": c,
        "ui_review": u,
        "workers": {"active_total": t["claims"]["active"] + c["claims"]["active"] + u["claims"]["active"]},
    }
    (out / "progress.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "README.md").write_text(markdown(data), encoding="utf-8")
    (out / "index.html").write_text(html(data), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(json.dumps({"translation_worker": t["worker_percent"], "translation_merged": t["queue_percent"], "speech_worker": c["speech"]["percent"], "speech_merged": c["speech"]["merged_percent"], "terminology_worker": c["terminology"]["percent"], "terminology_merged": c["terminology"]["merged_percent"], "ui_worker": u["percent"], "ui_merged": u["merged_percent"], "active_claims": data["workers"]["active_total"]}, indent=2))


if __name__ == "__main__":
    main()
