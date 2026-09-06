# Hachimi TL-VI Progress

> Cập nhật tự động từ `main`: **2026-09-06T23:12:51Z**. `Completed` = worker đã xong; `Merged` = đã nhập canonical.

| Pipeline | Worker progress | Completed | Merged | Tổng | Pending merge |
|---|---:|---:|---:|---:|---:|
| Translation | **25.80%** | 330 batch | 276 batch | 1645 | 54 |
| Speech curation | **100.00%** | 24 batch | 24 batch | 24 | 0 |
| Terminology curation | **94.72%** | 233 batch | 233 batch | 246 | 0 |
| Translation review | **100.00% reviewed** / **86.60% resolved** | 19,520 ledger items | 20 current-gen batch | 131 current-gen total | 6 |
| UI review | **0.00%** | 0 batch | 0 batch | 323 | 0 |

`█████░░░░░░░░░░░░░░░` Translation worker **25.80%**  
`████████████████████` Speech worker **100.00%**  
`███████████████████░` Terminology worker **94.72%**  
`████████████████████` Translation Review ledger **100.00% reviewed at least once** — resolved **16,905/19,520 entry (86.60%)**; current generation **20/131 batch (15.27%)**  
`░░░░░░░░░░░░░░░░░░░░` UI Review worker **0.00%**

> ⚠️ Progress reconciliation: translation_progress.translated_entries=19520 differs from artifact-derived canonical_entries=28820

## Canonical / phát hành

- Translation canonical: **28,820 / 131,560 entry = 21.91%**; raw source coverage **2.49%**.
- Speech merged: **24 / 24 = 100.00%**, tương ứng **119 profile** đã nhập.
- Terminology merged: **233 / 246 = 94.72%**; 4648 decision canonical — lock/defer/ignore = **1742/2723/183**.
- UI Review merged: **0 / 323 = 0.00%**; keep/revise/defer = **0/0/0**.
- Translation Review: **19,520 / 19,520 frozen-scope entry reviewed at least once = 100.00%** (ledger keep/revise/defer = **14782/2345/2393**); **16,905 resolved = 86.60%**; current-plan keep/revise/defer = **0/0/280**; new-translation gate = **REVIEW ACTIVE / TRANSLATION OPEN**.
- Active claims: translation **0**, curation **0**, Translation Review **6**, UI **0**; tổng **6**.
- Main snapshot: `b5915c64d385ef02fccaaf8995a2eeac38a88123`.

Machine-readable: [`progress.json`](./progress.json) · HTML: [`index.html`](./index.html)
