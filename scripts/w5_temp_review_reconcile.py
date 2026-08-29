from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'glossary/terminology_reviews.json'
payload = json.loads(path.read_text(encoding='utf-8'))

def append_note(decision: dict, suffix: str) -> None:
    note = str(decision.get('note') or '').strip()
    if suffix not in note:
        decision['note'] = (note + ' ' + suffix).strip()

expected = {
    'parallel.ctx-67f8551f77807292-v1.term-0097.15': 'target',
    'parallel.ctx-67f8551f77807292-v1.term-0109.01': 'superseded',
}
found = {key: 0 for key in expected}
for decision in payload.get('decisions', []):
    if not isinstance(decision, dict):
        continue
    decision_id = decision.get('decision_id')
    if decision_id not in expected:
        continue
    found[decision_id] += 1
    if decision_id.endswith('term-0097.15'):
        if decision.get('term_id') != 'race.tokyo_yushun':
            raise SystemExit(f'unexpected term_id: {decision.get("term_id")!r}')
        old = str(decision.get('target_vi') or '')
        if old not in {'Tokyo Yushun (Japanese Derby)', 'Japanese Derby'}:
            raise SystemExit(f'unexpected stale target: {old!r}')
        decision['target_vi'] = 'Japanese Derby'
        append_note(decision, 'Superseded by completed canonical Race hardening: use the verified player-facing target Japanese Derby.')
    else:
        if str(decision.get('source_zh_cn') or '') != '日本德比':
            raise SystemExit(f'unexpected Japanese Derby source: {decision.get("source_zh_cn")!r}')
        if str(decision.get('target_vi') or '') != 'Japanese Derby':
            raise SystemExit(f'unexpected Japanese Derby target: {decision.get("target_vi")!r}')
        decision['action'] = 'ignore'
        append_note(decision, 'Superseded by canonical race.tokyo_yushun; do not recreate a duplicate reviewed race-name lock.')

for decision_id, count in found.items():
    if count != 1:
        raise SystemExit(f'expected exactly one decision {decision_id}, found {count}')
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
