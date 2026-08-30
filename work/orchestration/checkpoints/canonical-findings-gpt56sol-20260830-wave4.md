# Canonical findings maintenance checkpoint — wave 4

Confirmed live baseline inherited from the maintenance claim: **30 resolved findings**. Pending hardeners must still be confirmed by green production Sync + live generated ledger before they increment that count.

Additional exact/category-16 proper-title hardener + regression-test pairs now durable:

- `願いのカタチ` → `Negai no Katachi`
- `笑顔の宝物 -Beyond The Future!-` → `Egao no Takaramono -Beyond The Future!-`
- `わたしの印は大本命◎` → `Watashi no Shirushi wa Daihonmei ◎`
- `涙ひかって明日になれ！` → `Namida Hikatte Ashita ni Nare!`

These use stable Latin/Romanized identities where no authoritative English localization is established, preserving punctuation/title markers and avoiding zh-CN/Vietnamese semantic calques.

They are automatically discovered by production Sync through the permanent `scripts/harden_*_finding.py` loop and are covered by full `pytest -q`.
