# Canonical findings maintenance checkpoint — Fenomeno 対象捕捉！正義遂行！ hardening

Finding: `cf-547f1a03893d2440` (`捕捉目标！正义执行！`)
Canonical target: `対象捕捉！正義遂行！`

## Superseding evidence

The earlier recheck-deferred checkpoint lacked a verified Japanese identity. Fresh verification now identifies this source alias as Fenomeno's JP-only unique Skill `対象捕捉！正義遂行！`. Repository evidence links the zh-CN title/inheritance entries to Fenomeno IDs `11270101`-`11270103`; current external JP references independently identify Fenomeno's unique Skill by the exact Japanese display title. Since Fenomeno is not released on Global, preserve the exact JP player-facing title rather than the historical zh-CN-derived Vietnamese calque `Bắt giữ mục tiêu! Thực thi chính nghĩa!`.

The finding uses `match_mode=contains` because the alias appears both as a standalone category-147 Skill title and inside category-172 inheritance prose. The canonical rule remains source-scoped to `text_data_dict.json`, preventing propagation to unrelated source files.

## Durable implementation

- `4b3488eacb6fc3bc4610ba03d57250adc3d9c423` adds `scripts/harden_fenomeno_target_capture_finding.py`.
- `05b50d76b6311dd0f8149cee12b6140b1112a58f` adds `tests/test_fenomeno_target_capture_finding_hardening.py` covering idempotence, canonical resolution, inheritance-prose coverage, and a negative `localize_dict.json` source-path guard.

## Acceptance evidence

- Validate run `34114898468`: `completed/success`.
- Production Context Sync run `34114898429`: `completed/success`; every hardening/context/test/commit-if-changed step succeeded.
- That production Sync generated canonical-context commit `b44cd1acb0948d586ea03d59853bbe1fe224f3c6`.
- Live `main` now records `cf-547f1a03893d2440` with canonical resolution target `対象捕捉！正義遂行！`, reviewed lock `audit.finding.skill-fenomeno-target-capture-justice`, and suggested target `対象捕捉！正義遂行！`. Under `active_findings` semantics it is therefore non-active.
- Review-plan Sync run `34114898387` was cancelled by workflow concurrency after newer `main` pushes; descendant-main review-plan run `34115081507` contains the Fenomeno commits and is queued.
- Descendant Context Sync `34115081532` is also queued. Because later maintenance changes exist on `main`, completion still requires a successful unchanged/no-op Context Sync after those generated changes settle.

Keep maintenance `completed_count=192` until a descendant review-plan Sync succeeds and the required second unchanged Context Sync semantic no-op is proven.
