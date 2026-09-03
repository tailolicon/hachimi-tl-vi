from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "common.style"
NARRATIVE_EXCLUSIONS = [
    "Hi～，我是丸善斯基哟！\\n你也是来看的吧？我那异次元般的跑法。\\n哼哼♪被迷的神魂颠倒的话……我可不管哦♪",
    "我是黄金城市。……事先说好，如果你只是把我当成\\n一个漂亮人偶来对待的话，我是不会原谅你的。\\n不要靠外表去判断我，而是靠跑法来判断。",
    "正义的英雄，微光飞驹参上！\\n无论是怎样的强敌，我的跑法都能够“砰”地将其打败，\\n夺回大家的笑容！很厉害吧！",
]


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "ui_community_terms.json"
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        existing = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*existing, *NARRATIVE_EXCLUSIONS]))
        term["basis"] = (
            "Common EN-version running-style category label. The zh-CN alias 跑法 is also ordinary narrative "
            "language meaning how someone runs; proven character-introduction sentences are excluded so the "
            "player-facing Style label is not forced into prose."
        )
        break
    else:
        raise ValueError(f"missing canonical community term {TERM_ID}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"running_style_narrative_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
