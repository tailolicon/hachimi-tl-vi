# Training/Support finalization W5 checkpoint — 15:55Z

- W5 continues the primary `canonical-training-support` finalization lane from the 15:49Z checkpoint.
- Race casing split-brain remains diagnosed as `Radio NIKKEI Sho` (hardener) vs reviewed `Radio Nikkei Sho`; staged repair normalizes the hardener to the reviewed target.
- Scope-aware alias validation successfully passed the intentional `京城锦标` Race collision in execution run `33261469339`, proving disjoint exact JSON-path scopes can coexist without disabling conflict safety.
- That run then exposed the next real Training/Support split-brain: JA `サポートPt` is locked by legacy `system.support_points` to `Điểm Hỗ trợ`, while canonical Training/Support hardening scopes `resource.support_points.common0160` to `Support Pt`.
- Durable staged repair now updates `scripts/harden_training_support_canon.py` to retire the legacy `system.support_points` umbrella by clearing aliases and setting `locked=false`, preserving it as history while keeping `resource.support_points.common0160` as the scoped player-facing rule.
- A second bounded validation run is being triggered from main to apply Race + Support Pt repair, materialize hardeners, run terminology-review check, targeted Race/Training tests, full pytest, `tlvi validate`, and `tlvi index` before persistence.
- No `localized_data/**` examples were edited.
