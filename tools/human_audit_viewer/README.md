# Human Audit Viewer

Static, read-only viewer for manual quality auditing of the current retrospective translation-review corpus.

It reads the repository's current:

- `work/translation_review/active_plan.json`
- the active plan file
- review batch JSON files referenced by that plan

No build step and no backend are required.

## Run locally

From the repository root:

```bash
python -m http.server 8088
```

Then open:

```text
http://localhost:8088/tools/human_audit_viewer/
```

When served from `localhost`, the viewer automatically uses `../../` as the repository data root, so it reads the checkout you are currently inspecting.

Do **not** open `index.html` directly with `file://`; browsers usually block the JSON fetches. Use any static HTTP server.

## Read current `main` directly from GitHub

Open **Nguồn dữ liệu** in the viewer and choose **GitHub Raw main**.

Default raw root:

```text
https://raw.githubusercontent.com/tailolicon/hachimi-tl-vi/main/
```

This is useful when the local checkout is stale.

## What the viewer shows

Each entry includes:

- source text;
- current Vietnamese baseline;
- UID / source path / JSON locator;
- risk score and risk flags;
- locked terms;
- player-facing/community terminology;
- source-bridge rules/risks;
- canonical Skill context when embedded;
- raw review item JSON.

The viewer classifies entries into practical audit groups such as UI/System, Song title, Song credit, Mission/Race objective, Character, Skill, Condition, Spark/Inheritance, and others. Classification is for navigation only; repository review metadata remains authoritative.

## Manual annotations

Annotations are stored in browser `localStorage`, namespaced by `plan_id`.

Supported verdicts:

- OK
- Có lỗi
- Cần kiểm tra
- Chưa audit

Issue tags include meaning, terminology, proper name, naturalness, numeric/structure, source-bridge, and other.

Optional fields:

- audit note;
- proposed Vietnamese correction.

Annotations do **not** mutate repository translations or review results.

## Export / import

The viewer can export:

- JSON — complete annotation state with plan/context metadata;
- CSV — spreadsheet-friendly audit rows;
- Markdown — only `Có lỗi` / `Cần kiểm tra` entries, convenient to hand to a curation/review worker.

Importing JSON merges annotations into the browser's current local audit state. A warning appears if the imported `plan_id` differs from the active plan.

## Whole-corpus filtering

Initial navigation loads one 20-entry review batch at a time.

Press **Tải toàn bộ corpus** to fetch all active batches into browser memory. Once loaded, search/category/risk/verdict filters work across the entire current retrospective corpus.

For a large plan this makes many HTTP requests, so batch-by-batch review is the lightweight default.

## Keyboard

- `[` — previous batch
- `]` — next batch
- `/` — focus search

## Plan changes

Annotations are separated by `plan_id`. If canonical policy changes and a new retrospective plan is generated, loading the latest plan starts a separate annotation namespace rather than silently mixing old and new audit state.

Export important audit work before clearing browser storage.
