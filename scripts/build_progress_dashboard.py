#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, os, subprocess
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


def head(root):
    if os.getenv("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return None


def translation(root, now):
    p = load(root / "work/translation_progress.json")
    total, queued, done = (int(p.get(k) or 0) for k in ("source_total_entries", "queued_entries", "translated_entries"))
    batches = int(p.get("queue_total_batches") or 0)
    return {
        "source_total_entries": total,
        "queued_entries": queued,
        "deferred_entries": int(p.get("deferred_entries") or 0),
        "translated_entries": done,
        "remaining_queue_entries": max(queued - done, 0),
        "raw_percent": percent(done, total),
        "queue_percent": percent(done, queued),
        "batches_total": batches,
        "batches_translated": len(p.get("translated_batches") or []),
        "batches_reviewed": len(p.get("reviewed_batches") or []),
        "batches_qa": len(p.get("qa_passed_batches") or []),
        "claims": claims(root / "work/claims", now),
    }


def curation(root, now):
    active = load(root / "work/curation/active_plan.json")
    plan_id, plan_path = active.get("plan_id"), active.get("plan_path")
    plan = load(root / plan_path) if plan_path else {}
    speech, terms = plan.get("speech_batches") or [], plan.get("terminology_batches") or []
    speech_sizes = {b["batch_id"]: len(b.get("items") or []) for b in speech if isinstance(b, dict) and b.get("batch_id")}
    sm, tm, profiles, actions = set(), set(), 0, Counter()
    merged = root / "work/curation/merged"
    for path in merged.glob("*.json") if merged.exists() else []:
        marker = load(path)
        if plan_id and marker.get("plan_id") != plan_id:
            continue
        bid = marker.get("batch_id", "")
        if bid.startswith("speech-"):
            sm.add(bid)
            profiles += speech_sizes.get(bid, 0)
        elif bid.startswith("term-"):
            tm.add(bid)
            result_path = marker.get("result_path")
            result = load(root / result_path) if result_path else {}
            for d in result.get("decisions") or []:
                if isinstance(d, dict) and d.get("action"):
                    actions[d["action"]] += 1
    return {
        "plan_id": plan_id,
        "speech": {"total": len(speech), "merged": len(sm), "percent": percent(len(sm), len(speech)), "profiles": profiles},
        "terminology": {"total": len(terms), "merged": len(tm), "percent": percent(len(tm), len(terms)), "decisions": sum(actions.values()), "lock": actions["lock"], "defer": actions["defer"], "ignore": actions["ignore"]},
        "claims": claims(root / "work/curation/claims", now),
    }


def ui(root, now):
    active = load(root / "work/ui_review/active_plan.json")
    plan_id, total = active.get("plan_id"), int(active.get("batch_count") or 0)
    merged_ids, actions = set(), Counter()
    merged = root / "work/ui_review/merged"
    for path in merged.glob("*.json") if merged.exists() else []:
        marker = load(path)
        if plan_id and marker.get("plan_id") != plan_id:
            continue
        if marker.get("batch_id"):
            merged_ids.add(marker["batch_id"])
        for k, v in (marker.get("counts") or {}).items():
            if isinstance(v, int):
                actions[k] += v
    return {
        "plan_id": plan_id,
        "candidates": int(active.get("candidate_count") or 0),
        "total": total,
        "merged": len(merged_ids),
        "percent": percent(len(merged_ids), total),
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

> Tự động cập nhật từ `main` lúc **{d['generated_at']}**. Worker không phải cập nhật dashboard này.

| Pipeline | Tiến độ | Đã xong | Tổng | Claim đang chạy |
|---|---:|---:|---:|---:|
| Translation priority queue | **{t['queue_percent']:.2f}%** | {t['translated_entries']:,} entry | {t['queued_entries']:,} entry | {t['claims']['active']} |
| Speech curation | **{c['speech']['percent']:.2f}%** | {c['speech']['merged']} batch | {c['speech']['total']} batch | {c['claims']['active']}* |
| Terminology curation | **{c['terminology']['percent']:.2f}%** | {c['terminology']['merged']} batch | {c['terminology']['total']} batch | {c['claims']['active']}* |
| UI review | **{u['percent']:.2f}%** | {u['merged']} batch | {u['total']} batch | {u['claims']['active']} |

`{bar(t['queue_percent'])}` Translation queue **{t['queue_percent']:.2f}%**  
`{bar(c['speech']['percent'])}` Speech **{c['speech']['percent']:.2f}%**  
`{bar(c['terminology']['percent'])}` Terminology **{c['terminology']['percent']:.2f}%**  
`{bar(u['percent'])}` UI Review **{u['percent']:.2f}%**

## Chi tiết

- Translation: **{t['translated_entries']:,} / {t['queued_entries']:,}** entry trong queue; còn **{t['remaining_queue_entries']:,}**. Raw coverage **{t['raw_percent']:.2f}%** trên {t['source_total_entries']:,} entry nguồn.
- Translation batches: **{t['batches_translated']} translated / {t['batches_reviewed']} reviewed / {t['batches_qa']} QA-passed / {t['batches_total']} total**.
- Speech: **{c['speech']['profiles']} profile** thuộc các batch đã merge.
- Terminology: **{c['terminology']['decisions']} decision** đã merge — lock/defer/ignore = **{c['terminology']['lock']}/{c['terminology']['defer']}/{c['terminology']['ignore']}**.
- UI Review: **{u['reviewed_items']} decision** đã merge — keep/revise/defer = **{u['keep']}/{u['revise']}/{u['defer']}**.
- Active claims tổng cộng: **{d['workers']['active_total']}**.
- Main snapshot: `{d['main_commit'] or 'unknown'}`.

Machine-readable: [`progress.json`](./progress.json) · Dashboard HTML: [`index.html`](./index.html)

\\* Speech và terminology dùng chung claim pool curation, nên số active claim được hiển thị giống nhau ở hai dòng.
'''


def html(d):
    blob = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hachimi TL-VI Progress</title><style>body{{font:16px system-ui;margin:0;background:#101114;color:#f3f4f6}}main{{max-width:1000px;margin:auto;padding:28px 18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}.card{{background:#191b20;border:1px solid #2c3038;border-radius:16px;padding:18px}}.big{{font-size:30px;font-weight:750}}.muted{{color:#9ca3af}}.bar{{height:10px;background:#30343c;border-radius:99px;overflow:hidden;margin-top:12px}}.fill{{height:100%;background:#f3f4f6}}table{{width:100%;border-collapse:collapse}}td{{padding:9px 0;border-bottom:1px solid #2c3038}}td:last-child{{text-align:right}}</style></head><body><main><h1>Hachimi TL-VI Progress</h1><p class="muted" id="meta"></p><div class="grid" id="cards"></div><div class="card" style="margin-top:14px"><table id="details"></table></div></main><script id="data" type="application/json">{blob}</script><script>const d=JSON.parse(document.getElementById('data').textContent),n=x=>Number(x||0).toLocaleString('vi-VN'),p=x=>Number(x||0).toFixed(2)+'%';document.getElementById('meta').textContent=`Tự động từ main • ${{d.generated_at}} • ${{d.workers.active_total}} active claims`;const a=[['Translation',d.translation.queue_percent,`${{n(d.translation.translated_entries)}} / ${{n(d.translation.queued_entries)}} entry`],['Speech',d.curation.speech.percent,`${{d.curation.speech.merged}} / ${{d.curation.speech.total}} batch`],['Terminology',d.curation.terminology.percent,`${{d.curation.terminology.merged}} / ${{d.curation.terminology.total}} batch`],['UI Review',d.ui_review.percent,`${{d.ui_review.merged}} / ${{d.ui_review.total}} batch`]];document.getElementById('cards').innerHTML=a.map(x=>`<div class="card"><div class="muted">${{x[0]}}</div><div class="big">${{p(x[1])}}</div><div>${{x[2]}}</div><div class="bar"><div class="fill" style="width:${{x[1]}}%"></div></div></div>`).join('');const r=[['Raw source coverage',p(d.translation.raw_percent)],['Translation queue remaining',n(d.translation.remaining_queue_entries)],['Speech profiles',n(d.curation.speech.profiles)],['Term lock / defer / ignore',`${{n(d.curation.terminology.lock)}} / ${{n(d.curation.terminology.defer)}} / ${{n(d.curation.terminology.ignore)}}`],['UI keep / revise / defer',`${{n(d.ui_review.keep)}} / ${{n(d.ui_review.revise)}} / ${{n(d.ui_review.defer)}}`],['Main commit',d.main_commit||'unknown']];document.getElementById('details').innerHTML=r.map(x=>`<tr><td>${{x[0]}}</td><td>${{x[1]}}</td></tr>`).join('');</script></body></html>'''


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
        "schema_version": 1,
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
    print(json.dumps({"translation": t["queue_percent"], "speech": c["speech"]["percent"], "terminology": c["terminology"]["percent"], "ui_review": u["percent"], "active_claims": data["workers"]["active_total"]}, indent=2))


if __name__ == "__main__":
    main()
