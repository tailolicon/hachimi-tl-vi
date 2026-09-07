# Canonical finding conflict repair — Wonder Acute 湯守の和心

- Active finding: `cf-4c728f45693525f7` (`汤守和心`).
- Initial hardening incorrectly tried to preserve the Japanese title `湯守の和心` as the target.
- Production Sync `34089167239` rejected that lock during `Apply explicit reviewed terminology locks` because the same Japanese Skill identity was already durably accepted by prior finding `cf-141e1dbe5b4bc506` (`汤守的和心`) as project target `Tấm Lòng Người Giữ Suối Nóng`.
- Corrective convergence keeps one canonical term: `skill.wonder_acute.yumori_washin`, target `Tấm Lòng Người Giữ Suối Nóng`, source aliases `汤守的和心` and `汤守和心`, with item/source-path scope retained.
- Existing hardener convergence commit: `4bb353097667929096149b198465583fdd847105`.
- Alternate-finding hardener convergence commit: `c5e491ae8814cf4adf2a51a8ec2fc4d75b5220d7`.
- Regression commit: `b46a1efbae8df198fb581a2e01cda2e29d6de21e` verifies both aliases resolve through the shared canonical term and that unrelated source files do not inherit the lock.
- Corrected Validate run: `34089558622`.
- Corrected production Sync run: `34089558589`.
- Do not increment maintenance completion yet. Remaining acceptance: corrected Validate success, corrected production Sync success, live ledger/rule verification, then a second unchanged production Sync proving semantic no-op.
