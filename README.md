# Hachimi TL-VI Progress

> Cập nhật tự động từ `main`: **2026-09-13T04:24:13Z**. `Completed` = worker đã xong; `Merged` = đã nhập canonical.

| Pipeline | Worker progress | Completed | Merged | Tổng | Pending merge |
|---|---:|---:|---:|---:|---:|
| Translation | **33.29%** | 359 batch | 293 batch | 1645 | 66 |
| Speech curation | **100.00%** | 24 batch | 24 batch | 24 | 0 |
| Terminology curation | **100.00%** | 249 batch | 244 batch | 249 | 5 |
| Translation review | **100.00% reviewed** / **85.89% resolved** | 19,520 ledger items | 0 current-gen batch | 138 current-gen total | 0 |
| UI review | **0.00%** | 0 batch | 0 batch | 323 | 0 |

`███████░░░░░░░░░░░░░` Translation worker **33.29%**  
`████████████████████` Speech worker **100.00%**  
`████████████████████` Terminology worker **100.00%**  
`████████████████████` Translation Review ledger **100.00% reviewed at least once** — resolved **16,766/19,520 entry (85.89%)**; current generation **0/138 batch (0.00%)**  
`░░░░░░░░░░░░░░░░░░░░` UI Review worker **0.00%**

> ⚠️ Progress reconciliation: translation_progress.translated_entries=19520 differs from artifact-derived canonical_entries=37860

## Canonical / phát hành

- Translation canonical: **37,860 / 131,560 entry = 28.78%**; raw source coverage **3.27%**.
- Speech merged: **24 / 24 = 100.00%**, tương ứng **119 profile** đã nhập.
- Terminology merged: **244 / 249 = 97.99%**; 4741 decision canonical — lock/defer/ignore = **1780/2753/208**.
- UI Review merged: **0 / 323 = 0.00%**; keep/revise/defer = **0/0/0**.
- Translation Review: **19,520 / 19,520 frozen-scope entry reviewed at least once = 100.00%** (ledger keep/revise/defer = **14776/2414/2330**); **16,766 resolved = 85.89%**; current-plan keep/revise/defer = **0/0/0**; new-translation gate = **REVIEW ACTIVE / TRANSLATION OPEN**.
- Active claims: translation **0**, curation **4**, Translation Review **0**, UI **0**; tổng **4**.
- Main snapshot: `b56688d1238adaf82c72babdbd3c579289b2e83e`.

Machine-readable: [`progress.json`](./progress.json) · HTML: [`index.html`](./index.html)
