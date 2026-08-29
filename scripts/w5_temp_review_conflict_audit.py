from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
registry = json.loads((root / 'glossary/term_registry.json').read_text(encoding='utf-8'))
reviews = json.loads((root / 'glossary/terminology_reviews.json').read_text(encoding='utf-8'))
terms = {str(term.get('id')): term for term in registry.get('terms', []) if isinstance(term, dict) and term.get('id')}
conflicts = []
for decision in reviews.get('decisions', []):
    if not isinstance(decision, dict) or str(decision.get('action', '')).lower() != 'lock':
        continue
    term_id = str(decision.get('term_id') or '').strip()
    if not term_id or term_id not in terms:
        continue
    term = terms[term_id]
    review_target = str(decision.get('target_vi') or '').strip()
    canonical_target = str(term.get('target_vi') or '').strip()
    reasons = []
    if review_target != canonical_target:
        reasons.append('target_mismatch')
    if not term.get('locked'):
        reasons.append('term_unlocked')
    if reasons:
        conflicts.append({
            'decision_id': decision.get('decision_id'),
            'term_id': term_id,
            'review_target': review_target,
            'canonical_target': canonical_target,
            'category': term.get('category'),
            'reasons': reasons,
            'ja': term.get('ja'),
            'zh_cn': term.get('zh_cn'),
            'note': term.get('note'),
        })
print(json.dumps(conflicts, ensure_ascii=False, indent=2))
print(f'conflict_count={len(conflicts)}')
