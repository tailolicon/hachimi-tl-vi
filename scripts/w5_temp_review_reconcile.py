from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'glossary/terminology_reviews.json'
payload = json.loads(path.read_text(encoding='utf-8'))
decision_id = 'parallel.ctx-67f8551f77807292-v1.term-0097.15'
found = 0
for decision in payload.get('decisions', []):
    if not isinstance(decision, dict) or decision.get('decision_id') != decision_id:
        continue
    found += 1
    if decision.get('term_id') != 'race.tokyo_yushun':
        raise SystemExit(f'unexpected term_id: {decision.get("term_id")!r}')
    old = str(decision.get('target_vi') or '')
    if old not in {'Tokyo Yushun (Japanese Derby)', 'Japanese Derby'}:
        raise SystemExit(f'unexpected stale target: {old!r}')
    decision['target_vi'] = 'Japanese Derby'
    note = str(decision.get('note') or '').strip()
    suffix = 'Superseded by completed canonical Race hardening: use the verified player-facing target Japanese Derby.'
    if suffix not in note:
        decision['note'] = (note + ' ' + suffix).strip()
if found != 1:
    raise SystemExit(f'expected exactly one decision {decision_id}, found {found}')
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
