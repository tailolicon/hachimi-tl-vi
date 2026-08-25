# hachimi-tl-vi

Pipeline **JP → VI bằng AI** cho Hachimi Edge, thiết kế để làm nguồn dịch tiếng Việt độc lập cho UM:PD bản JP.

## Nguyên tắc dữ liệu

- Đầu vào AI của dự án là **text tiếng Nhật gốc** do người dùng tự trích xuất từ bản game của mình hoặc nguồn mà họ có quyền sử dụng.
- Không dùng bản dịch tiếng Anh của UmaTL làm corpus/đầu vào cho AI.
- Code/tooling trong repo dùng MIT. Dữ liệu phát sinh từ game không mặc nhiên thuộc MIT.

## Hỗ trợ

Pipeline hiện có các lớp chính của Hachimi:

- UI: `localize_dict.json`
- fallback UI: `hashed_dict.json` (compiler đã hỗ trợ; importer chuyên dụng sẽ được thêm khi có dump nguồn)
- `master.mdb`: `text_data`, `character_system_text`, `race_jikkyo_comment`, `race_jikkyo_message`
- asset JSON Hachimi: story, home dialogue, race story, lyrics và các field text phổ biến
- Translation Memory SQLite
- glossary + style rules
- dịch batch qua API OpenAI-compatible
- QA placeholder/tag/newline
- compile `localized_data/`
- tạo `index.json` với BLAKE3 cho updater của Hachimi
- GitHub Actions test/validate và tạo nhánh `release`

## Cài môi trường

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e "[dev]"
```

Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '[dev]'
```

## 1. Lấy dữ liệu JP

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

Trong Hachimi Edge bật **Translator mode**, dùng chức năng dump localize dict, sau đó:

```bash
tlvi import-localize "C:/path/to/localize_dump.json"
```

### Story / Home / Race story / Lyrics

Trích xuất asset thành Hachimi-compatible JSON bằng tool phù hợp rồi đặt vào một thư mục giữ nguyên internal path, ví dụ:

```text
jp_assets/
├─ story/data/04/1001/storytimeline_041001001.json
├─ home/data/00000/01/hometimeline_....json
└─ lyrics/m1001_lyrics.json
```

Sau đó:

```bash
tlvi import-assets jp_assets
```

## 2. Cấu hình model AI

Sao chép `.env.example` hoặc đặt biến môi trường:

```powershell
$env:TLVI_API_BASE="https://api.openai.com/v1"
$env:TLVI_API_KEY="..."
$env:TLVI_MODEL="gpt-5.6"
```

Có thể dùng endpoint OpenAI-compatible khác (OpenRouter, gateway nội bộ, vLLM/Ollama-compatible, v.v.).

## 3. Dịch

Dịch thử 100 chuỗi:

```bash
tlvi translate --limit 100 --batch-size 20
```

Dịch riêng story:

```bash
tlvi translate --kind story --limit 500
```

Xem tiến độ:

```bash
tlvi status
```

Translation Memory dùng fingerprint của text + context. Khi game update, chuỗi không đổi sẽ **không bị dịch lại**; chuỗi mới/thay đổi trở thành pending.

## 4. Compile và kiểm tra

```bash
tlvi compile
tlvi validate
tlvi index
```

Kết quả là `localized_data/` + `index.json` tương thích cơ chế translation repo của Hachimi Edge.

## 5. Cập nhật sau patch game

Quy trình định kỳ:

```bash
tlvi import-mdb PATH_TO_NEW_MASTER_MDB
tlvi import-localize PATH_TO_NEW_LOCALIZE_DUMP
tlvi import-assets PATH_TO_NEW_EXTRACTED_ASSETS
tlvi translate
tlvi compile
tlvi validate
tlvi index
```

Các entry cũ có cùng fingerprint được tái sử dụng tự động.

## Repo selector của Hachimi

Entry đề xuất nằm ở `docs/meta-entry.json`. Sau khi repo GitHub tồn tại và nhánh `release` được publish, URL index sẽ là:

```text
https://raw.githubusercontent.com/tailolicon/hachimi-tl-vi/release/index.json
```

## Trạng thái kỹ thuật

Đây là nền tảng chạy được cho corpus JP. Để có **100% game tiếng Việt**, cần trích xuất toàn bộ asset JP sau mỗi patch; kể từ update JP 2025-09-24, story asset/meta đã thay đổi nên phần extraction nên dựa vào tool hiện hành hỗ trợ format mới. Pipeline này cố ý tách extraction khỏi translation để có thể đổi extractor mà không mất Translation Memory.
