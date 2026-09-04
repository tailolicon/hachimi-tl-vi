# hachimi-tl-vi

Pipeline dịch tiếng Việt độc lập cho **Uma Musume Pretty Derby JP** trên Hachimi Edge.

<!-- AUTO_PROGRESS_START -->
## Live project control

**Spawn worker (the only prompt you need):** `Run tailolicon/hachimi-tl-vi/WORKER_START.md from main.`

| Metric | Live state |
| --- | --- |
| Current phase | **retrospective_translation_review** |
| Primary integration lane | **Retrospective translation Audit Round 1** — stage **mass_review** (`main`) |
| Canonical parallelism | **ON** — domain work parallel / integration serial; 0 active-or-claimable domain lanes, 0 ready for integration, 7 canonical domains complete; configured domain-worker cap 5 |
| Pinned source coverage | **21,380 / 1,158,825 (1.84%)** — 1,137,445 remaining |
| Current translation wave | **21,380 / 131,560 (16.25%)** — 110,180 queued remaining |
| Deferred pinned entries | **1,027,265** — these must be promoted in later deterministic waves, not ignored |
| Translation Audit Round 1 | **19,520 / 19,520 entries reviewed at least once (100.00%)** — ledger keep/revise/defer **14,644/2,442/2,434**; 15,350 / 19,520 currently resolved (78.64%); current generation **68 / 218 batches (31.19%)**, 1,250 merged decisions; 4,170 unresolved; gate **REVIEW ACTIVE / TRANSLATION OPEN** |
| Audit merge backlog | **5 completed batch** awaiting bounded reconciliation (normally ≤5 min) |
| UI review | **0 / 6,455 reviewed items (0.00%)** |
| Context curation | Speech **100.00%**, terminology **95.88%** |
| Active worker claims | **9** |

**Roadmap:** ▶ Retrospective translation Audit Round 1

Machine routing lives in `work/orchestration/state.json`; canonical parallel rules are in `CANONICAL_PARALLEL.md`; detailed lifecycle is in `AUTOPILOT.md`. This block is generated from canonical repository state. The `status` branch keeps the timestamped detailed progress snapshot.
<!-- AUTO_PROGRESS_END -->

Mục tiêu dài hạn là ưu tiên **JP → VI** trực tiếp. Để bootstrap với dữ liệu đủ mới trong 2026, dự án hiện dùng snapshot Hachimi zh-CN của **server JP** làm semantic bridge, được pin theo commit để mọi worker dịch cùng một corpus bất biến.

## Nguyên tắc dữ liệu

- Ưu tiên text tiếng Nhật gốc khi có snapshot đủ mới và có thể sử dụng phù hợp.
- Bootstrap hiện tại dùng `Hachimi-Hachimi/tl-zh-cn` đã pin; provenance/điều kiện nguồn được ghi trong `SOURCE_ATTRIBUTION.md`.
- Không dùng bản dịch tiếng Anh của UmaTL làm corpus/đầu vào cho AI.
- Với zh-CN, tên riêng không được dịch literal sang tiếng Việt; phải resolve qua character/term registry.
- Code/tooling trong repo dùng MIT. Dữ liệu game và material phái sinh không mặc nhiên thuộc MIT.

## Shared game context cho mọi worker

Mọi worker song song phải đọc cùng context trong repo thay vì tự nghiên cứu lại từ đầu:

- `GAME_CONTEXT.md` — world/game/translation bible
- `glossary/term_registry.json` — thuật ngữ JP ↔ zh-CN ↔ VI đã review/lock
- `glossary/observed_terms.json` — exact terminology memory học từ các entity đã merge; không tự coi là canonical
- `glossary/terminology_review_queue.json` — queue ưu tiên conflict/promotion/new entity
- `glossary/terminology_reviews.json` — ledger quyết định `lock` / `defer` / `ignore`
- `glossary/characters.json` — canonical character identity + JP/zh-CN alias
- `glossary/speech_bible.json` — speech profile đã curate để giữ register/nhịp/cá tính
- `glossary/speech_samples.json` — mẫu hội thoại + thống kê từ exact pinned snapshot, chỉ dùng làm evidence review
- `glossary/speech_review_queue.json` — queue các nhân vật chưa có speech profile
- `glossary/style_rules.json` — luật theo UI/skill/story/race/lyrics
- `glossary/generated_candidates.json` — candidate race/skill/support/scenario để review, **không phải canonical glossary**

Character registry, terminology candidates và speech evidence đều bám exact `source_commit` trong `work/translation_progress.json`. Prompt chỉ inject core terms + observed term + character/speech profile thật sự liên quan đến batch, nên các registry có thể lớn mà không làm mọi request phình context.

Xem chi tiết tại `CONTEXT_MAINTENANCE.md` và `PARALLEL_WORKERS.md`.

## Trạng thái context bootstrap 2026

Ở snapshot đang pin:

- 142 structured character identities; 141 có game ID đã resolve và 1 identity giữ stable slug vì chưa có ID đáng tin.
- 5.584 terminology candidate records, gom thành 5.179 source entity duy nhất.
- Speech sampler đã quét 18.299 asset JSON và 440.394 dialogue block.
- 330.719 dialogue block map được về 141 character identities; 0 ambiguous alias và 0 invalid JSON trong lần scan hiện tại.
- Speech Bible hiện có seed curated profiles; các nhân vật còn lại được ưu tiên trong `speech_review_queue.json` theo lượng dialogue evidence.

Các con số này là snapshot-derived và sẽ được workflow sinh lại khi pinned source thay đổi.

## Hỗ trợ

Pipeline hiện có các lớp chính của Hachimi:

- UI: `localize_dict.json`
- fallback UI: `hashed_dict.json`
- `master.mdb`: `text_data`, `character_system_text`, `race_jikkyo_comment`, `race_jikkyo_message`
- asset JSON Hachimi: story, home dialogue, race story, lyrics và các field text phổ biến
- Translation Memory SQLite
- shared game context + canonical/observed terminology
- canonical character registry + batch-filtered Character Speech Bible
- relevance-filtered AI prompt context
- dịch batch qua API OpenAI-compatible
- QA placeholder/tag/newline
- parallel worker claims + persisted results + merge workflow
- compile `localized_data/`
- tạo `index.json` với BLAKE3 cho updater của Hachimi
- GitHub Actions validate, source/context/speech sync và tạo nhánh `release`

## Cài môi trường

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Dữ liệu JP trực tiếp

### master.mdb

Windows DMM thường có file tại:

```text
%USERPROFILE%\AppData\LocalLow\Cygames\umamusume\master\master.mdb
```

Nhập vào Translation Memory:

```bash
tlvi import-mdb "C:/Users/you/AppData/LocalLow/Cygames/umamusume/master/master.mdb"
```

### UI/localize

Trong Hachimi Edge bật Translator mode, dump localize dict, sau đó:

```bash
tlvi import-localize "C:/path/to/localize_dump.json"
```

### Story / Home / Race story / Lyrics

Giữ Hachimi-compatible internal path, ví dụ:

```text
jp_assets/
├─ story/data/04/1001/storytimeline_041001001.json
├─ home/data/00000/01/hometimeline_....json
└─ lyrics/m1001_lyrics.json
```

Import:

```bash
tlvi import-assets jp_assets
```

## Cấu hình model AI

```powershell
$env:TLVI_API_BASE="https://api.openai.com/v1"
$env:TLVI_API_KEY="..."
$env:TLVI_MODEL="gpt-5.6"
```

Có thể dùng endpoint OpenAI-compatible khác.

## Dịch local pipeline

```bash
tlvi translate --limit 100 --batch-size 20
tlvi translate --kind story --limit 500
tlvi status
```

Translation Memory dùng fingerprint của text + context. Khi source update, chuỗi không đổi không phải dịch lại; chuỗi mới/thay đổi trở thành pending.

## Compile và kiểm tra

```bash
tlvi compile
tlvi validate
tlvi index
```

Kết quả là `localized_data/` + `index.json` tương thích translation repo của Hachimi Edge.

## Context maintenance

Sinh/sync identity và terminology review data:

```bash
python scripts/sync_context_registry.py
python scripts/extract_context_candidates.py
python scripts/build_observed_term_memory.py
python scripts/apply_terminology_reviews.py --check
python scripts/apply_terminology_reviews.py
python scripts/build_terminology_review_queue.py
```

`apply_terminology_reviews.py` chỉ promote các quyết định `action=lock` đã được ghi rõ trong `glossary/terminology_reviews.json`. Nếu alias đã bị khóa sang một target khác, script dừng với lỗi thay vì ghi đè. `defer` và `ignore` không sửa canonical registry.

Speech evidence/review:

```bash
python scripts/extract_speaker_samples.py --upstream-root PATH_TO_PINNED_SOURCE --source-commit PINNED_SHA
python scripts/build_speech_review_queue.py
```

`glossary/speech_samples.json` chỉ là evidence. Chỉ `glossary/speech_bible.json` mới được inject làm speech guidance, và source scene luôn có ưu tiên cao hơn profile tổng quát.

GitHub Actions chạy context/speech sync định kỳ nhưng luôn đọc exact pinned source; chúng không tự đổi corpus đang được các worker dịch và không sửa claim/result/canonical progress của worker.

## Repo selector của Hachimi

```text
https://raw.githubusercontent.com/tailolicon/hachimi-tl-vi/release/index.json
```

## Trạng thái kỹ thuật

Pipeline đang bootstrap từ corpus JP-server zh-CN 2026 và có thể migrate dần sang JP trực tiếp khi có snapshot mới tương đương. Extraction, evidence, translation, review và canonical locking được tách rời để game update/extractor mới không làm mất Translation Memory hoặc kết quả đã review.
