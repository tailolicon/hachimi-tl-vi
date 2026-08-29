from pathlib import Path

p = Path('scripts/harden_training_support_canon.py')
s = p.read_text(encoding='utf-8')
needle = '''    _upsert(
        terms,
        {
            "id": "resource.support_points.common0160",'''
insert = '''    legacy_support_points = _find(terms, "system.support_points")
    if legacy_support_points is not None:
        legacy_support_points["ja"] = []
        legacy_support_points["zh_cn"] = []
        legacy_support_points["locked"] = False
        legacy_support_points["note"] = (
            "Superseded legacy Support Points umbrella. The player-facing compact resource label is scoped "
            "by resource.support_points.common0160; keep this record only as registry history."
        )

''' + needle
if 'legacy_support_points = _find(terms, "system.support_points")' not in s:
    if s.count(needle) != 1:
        raise SystemExit(f'expected one Support Pt insertion point, found {s.count(needle)}')
    s = s.replace(needle, insert)
    p.write_text(s, encoding='utf-8')
