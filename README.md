# Hachimi TL-VI Progress

> Cập nhật tự động từ `main`: **2026-09-15T21:35:51Z**. `Completed` = worker đã xong; `Merged` = đã nhập canonical.

| Pipeline | Worker progress | Completed | Merged | Tổng | Pending merge |
|---|---:|---:|---:|---:|---:|
| Translation | **33.49%** | 360 batch | 293 batch | 1645 | 67 |
| Speech curation | **100.00%** | 24 batch | 24 batch | 24 | 0 |
| Terminology curation | **100.00%** | 249 batch | 248 batch | 249 | 1 |
| Translation review | **100.00% reviewed** / **85.78% resolved** | 19,520 ledger items | 12 current-gen batch | 139 current-gen total | 1 |
| UI review | **0.00%** | 0 batch | 0 batch | 323 | 0 |

`███████░░░░░░░░░░░░░` Translation worker **33.49%**  
`████████████████████` Speech worker **100.00%**  
`████████████████████` Terminology worker **100.00%**  
`████████████████████` Translation Review ledger **100.00% reviewed at least once** — resolved **16,744/19,520 entry (85.78%)**; current generation **12/139 batch (8.63%)**  
`░░░░░░░░░░░░░░░░░░░░` UI Review worker **0.00%**

> ⚠️ Progress reconciliation: translation_progress.translated_entries=19520 differs from artifact-derived canonical_entries=38040

## Canonical / phát hành

- Translation canonical: **38,040 / 131,560 entry = 28.91%**; raw source coverage **3.28%**.
- Speech merged: **24 / 24 = 100.00%**, tương ứng **119 profile** đã nhập.
- Terminology merged: **248 / 249 = 99.60%**; 4809 decision canonical — lock/defer/ignore = **1813/2767/229**.
- UI Review merged: **0 / 323 = 0.00%**; keep/revise/defer = **0/0/0**.
- Translation Review: **19,520 / 19,520 frozen-scope entry reviewed at least once = 100.00%** (ledger keep/revise/defer = **14779/2415/2326**); **16,744 resolved = 85.78%**; current-plan keep/revise/defer = **3/1/216**; new-translation gate = **REVIEW ACTIVE / TRANSLATION OPEN**.
- Active claims: translation **0**, curation **0**, Translation Review **0**, UI **0**; tổng **0**.
- Main snapshot: `c8f8d70da2800ceeb9d1eebf6a8308695dd4dec6`.

Machine-readable: [`progress.json`](./progress.json) · HTML: [`index.html`](./index.html)
