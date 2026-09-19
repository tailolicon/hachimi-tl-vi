# Hachimi TL-VI Progress

> Cập nhật tự động từ `main`: **2026-09-19T17:30:21Z**. `Completed` = worker đã xong; `Merged` = đã nhập canonical.

| Pipeline | Worker progress | Completed | Merged | Tổng | Pending merge |
|---|---:|---:|---:|---:|---:|
| Translation | **33.49%** | 360 batch | 293 batch | 1645 | 67 |
| Speech curation | **100.00%** | 24 batch | 24 batch | 24 | 0 |
| Terminology curation | **100.00%** | 249 batch | 248 batch | 249 | 1 |
| Translation review | **100.00% reviewed** / **85.36% resolved** | 19,520 ledger items | 0 current-gen batch | 143 current-gen total | 0 |
| UI review | **0.00%** | 0 batch | 0 batch | 323 | 0 |

`███████░░░░░░░░░░░░░` Translation worker **33.49%**  
`████████████████████` Speech worker **100.00%**  
`████████████████████` Terminology worker **100.00%**  
`████████████████████` Translation Review ledger **100.00% reviewed at least once** — resolved **16,662/19,520 entry (85.36%)**; current generation **0/143 batch (0.00%)**  
`░░░░░░░░░░░░░░░░░░░░` UI Review worker **0.00%**

> ⚠️ Progress reconciliation: translation_progress.translated_entries=19520 differs from artifact-derived canonical_entries=38080

## Canonical / phát hành

- Translation canonical: **38,080 / 131,560 entry = 28.94%**; raw source coverage **3.29%**.
- Speech merged: **24 / 24 = 100.00%**, tương ứng **119 profile** đã nhập.
- Terminology merged: **248 / 249 = 99.60%**; 4809 decision canonical — lock/defer/ignore = **1813/2767/229**.
- UI Review merged: **0 / 323 = 0.00%**; keep/revise/defer = **0/0/0**.
- Translation Review: **19,520 / 19,520 frozen-scope entry reviewed at least once = 100.00%** (ledger keep/revise/defer = **14779/2415/2326**); **16,662 resolved = 85.36%**; current-plan keep/revise/defer = **0/0/0**; new-translation gate = **REVIEW ACTIVE / TRANSLATION OPEN**.
- Active claims: translation **0**, curation **0**, Translation Review **0**, UI **0**; tổng **0**.
- Main snapshot: `f920e0eaca04b9cc147cb32137b080d6f29698e2`.

Machine-readable: [`progress.json`](./progress.json) · HTML: [`index.html`](./index.html)
