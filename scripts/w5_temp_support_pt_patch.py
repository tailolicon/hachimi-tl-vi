from pathlib import Path

p = Path('scripts/harden_training_support_canon.py')
s = p.read_text(encoding='utf-8')

support_needle = '''    _upsert(
        terms,
        {
            "id": "resource.support_points.common0160",'''
support_insert = '''    legacy_support_points = _find(terms, "system.support_points")
    if legacy_support_points is not None:
        legacy_support_points["ja"] = []
        legacy_support_points["zh_cn"] = []
        legacy_support_points["locked"] = False
        legacy_support_points["note"] = (
            "Superseded legacy Support Points umbrella. The player-facing compact resource label is scoped "
            "by resource.support_points.common0160; keep this record only as registry history."
        )

''' + support_needle
if 'legacy_support_points = _find(terms, "system.support_points")' not in s:
    if s.count(support_needle) != 1:
        raise SystemExit(f'expected one Support Pt insertion point, found {s.count(support_needle)}')
    s = s.replace(support_needle, support_insert)

energy_needle = '''    _upsert(
        terms,
        {
            "id": "state.energy.singlemode",'''
energy_insert = '''    legacy_energy = _find(terms, "resource.energy")
    if legacy_energy is not None:
        legacy_energy["ja"] = []
        legacy_energy["zh_cn"] = []
        legacy_energy["locked"] = False
        legacy_energy["note"] = (
            "Superseded legacy Energy umbrella. Bare 体力 is not globally locked; the Career Energy gauge "
            "is enforced only by state.energy.singlemode in verified SingleMode slots."
        )

''' + energy_needle
if 'legacy_energy = _find(terms, "resource.energy")' not in s:
    if s.count(energy_needle) != 1:
        raise SystemExit(f'expected one Energy insertion point, found {s.count(energy_needle)}')
    s = s.replace(energy_needle, energy_insert)

p.write_text(s, encoding='utf-8')
