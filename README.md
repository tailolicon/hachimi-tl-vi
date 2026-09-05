# Hachimi TL-VI Progress

> Cập nhật tự động từ `main`: **2026-09-05T23:05:46Z**. `Completed` = worker đã xong; `Merged` = đã nhập canonical.

| Pipeline | Worker progress | Completed | Merged | Tổng | Pending merge |
|---|---:|---:|---:|---:|---:|
| Translation | **22.92%** | 306 batch | 273 batch | 1645 | 33 |
| Speech curation | **100.00%** | 24 batch | 24 batch | 24 | 0 |
| Terminology curation | **95.49%** | 233 batch | 233 batch | 244 | 0 |
| Translation review | **100.00% reviewed** / **84.35% resolved** | 19,520 ledger items | 73 current-gen batch | 164 current-gen total | 1 |
| UI review | **0.00%** | 0 batch | 0 batch | 323 | 0 |

`█████░░░░░░░░░░░░░░░` Translation worker **22.92%**  
`████████████████████` Speech worker **100.00%**  
`███████████████████░` Terminology worker **95.49%**  
`████████████████████` Translation Review ledger **100.00% reviewed at least once** — resolved **16,466/19,520 entry (84.35%)**; current generation **73/164 batch (44.51%)**  
`░░░░░░░░░░░░░░░░░░░░` UI Review worker **0.00%**

> ⚠️ Progress reconciliation: translation_progress.translated_entries=19520 differs from artifact-derived canonical_entries=26560

## Canonical / phát hành

- Translation canonical: **26,560 / 131,560 entry = 20.19%**; raw source coverage **2.29%**.
- Speech merged: **24 / 24 = 100.00%**, tương ứng **119 profile** đã nhập.
- Terminology merged: **233 / 244 = 95.49%**; 4648 decision canonical — lock/defer/ignore = **1742/2723/183**.
- UI Review merged: **0 / 323 = 0.00%**; keep/revise/defer = **0/0/0**.
- Translation Review: **19,520 / 19,520 frozen-scope entry reviewed at least once = 100.00%** (ledger keep/revise/defer = **14896/2329/2295**); **16,466 resolved = 84.35%**; current-plan keep/revise/defer = **167/58/1214**; new-translation gate = **REVIEW ACTIVE / TRANSLATION OPEN**.
- Active claims: translation **0**, curation **0**, Translation Review **4**, UI **0**; tổng **4**.
- Main snapshot: `9344e97e4a8f7cb4caf1dfebf80d56fce1f21a69`.

Machine-readable: [`progress.json`](./progress.json) · HTML: [`index.html`](./index.html)
