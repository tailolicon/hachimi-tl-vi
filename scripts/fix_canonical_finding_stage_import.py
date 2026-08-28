from pathlib import Path

path = Path("scripts/build_translation_review_plan.py")
text = path.read_text(encoding="utf-8")
marker = "from typing import Any\n"
addition = (
    "from typing import Any\n\n"
    "try:\n"
    "    from scripts.translation_review_common import canonical_finding_matches, load_canonical_findings\n"
    "except ModuleNotFoundError:\n"
    "    from translation_review_common import canonical_finding_matches, load_canonical_findings  # type: ignore[no-redef]\n"
)
if "from scripts.translation_review_common import canonical_finding_matches, load_canonical_findings" not in text:
    if marker not in text:
        raise SystemExit("builder import marker missing")
    text = text.replace(marker, addition, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
