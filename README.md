# hachimi-tl-vi

Pipeline dịch tiếng Việt độc lập cho **Uma Musume Pretty Derby JP** trên Hachimi Edge.

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
- `glossary/characters.json` — canonical character identity + alias + speech/relationship rules
- `glossary/style_rules.json` — luật theo UI/skill/story/race/lyrics
- `glossary/generated_candidates.json` — candidate race/skill/support/scenario để review, **không phải canonical glossary**

Character registry và terminology candidates được tự sync từ snapshot đang pin. Prompt chỉ inject core terms + entity thật sự xuất hiện trong batch, nên registry có thể lớn mà không làm mọi request phình context.

Xem chi tiết tại `CONTEXT_MAINTENANCE.md` và `PARALLEL_WORKERS.md`.

## Hỗ trợ

Pipeline hiện có các lớp chính của Hachimi:

- UI: `localize_dict.json`
- fallback UI: `hashed_dict.json`
- `master.mdb`: `text_data`, `character_system_text`, `race_jikkyo_comment`, `race_jikkyo_message`
- asset JSON Hachimi: story, home dialogue, race story, lyrics và các field text phổ biến
- Translation Memory SQLite
- shared game context + terminology/character registry
- relevance-filtered AI prompt context
- dịch batch qua API OpenAI-compatible
- QA placeholder/tag/newline
- parallel worker claims + persisted results + merge workflow
- compile `localized_data/`
- tạo `index.json` với BLAKE3 cho updater của Hachimi
- GitHub Actions validate, context sync và tạo nhánh `release`

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

```bash
python scripts/sync_context_registry.py
python scripts/extract_context_candidates.py
```

GitHub Actions cũng chạy context sync định kỳ, nhưng luôn đọc exact `source_commit` từ `work/translation_progress.json`; nó không tự đổi corpus đang được các worker dịch.

## Repo selector của Hachimi

```text
https://raw.githubusercontent.com/tailolicon/hachimi-tl-vi/release/index.json
```

## Trạng thái kỹ thuật

Pipeline đang bootstrap từ corpus JP-server zh-CN 2026 và có thể migrate dần sang JP trực tiếp khi có snapshot mới tương đương. Extraction và translation được tách rời để game update/extractor mới không làm mất Translation Memory hoặc kết quả đã review.
