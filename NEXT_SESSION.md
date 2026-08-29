# Next-session handoff

The repository now owns the complete handoff and lifecycle state.

Do not use chat history, copied prompts, or this file as an independent worker protocol.

For every fresh session, use exactly:

> Run `tailolicon/hachimi-tl-vi/WORKER_START.md` from `main`.

`WORKER_START.md` reads `work/orchestration/state.json` and routes the worker to the current blocking canonical-maintenance task, systemic canonical finding, retrospective review, UI review, translation wave, deferred-wave expansion, post-completion audit, or final release task.

The current progress/task summary is automatically rendered near the top of `README.md`.
