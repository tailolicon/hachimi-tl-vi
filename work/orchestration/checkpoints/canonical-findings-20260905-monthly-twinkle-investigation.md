# Canonical findings maintenance checkpoint — Monthly Twinkle implementation

The recurring in-world publication `月刊Twinkle` is represented by two live proper-name findings:
- `cf-3f76c45986ceefe6`, scoped to `localize_dict.json` key `Champions187003`.
- `cf-fc0ace892355f4ce`, scoped to `localize_dict.json` key `Champions0507`.

Both findings' canonical source is the base alias `月刊Twinkle` with `match_mode=contains`; the surrounding `号外` / `增刊` text is edition wording and is not part of the canonical publication identity. Historical review results consistently deferred both entries pending this canonical decision.

Evidence and decision:
- Cygames' official JP portal identifies Otonashi Etsuko as a reporter for the magazine `月刊トゥインクル`, establishing this as a recurring proper publication title rather than generic prose.
- The pinned zh-CN UI preserves the title element `Twinkle` as `月刊Twinkle`.
- Established English-language Umamusume references render the publication as `Monthly Twinkle`.
- Canonical target selected: `Monthly Twinkle`, at the community/proper-name layer. This is a deliberate project canonical rendering, not a claim that an official Global localization was found.
- Matcher is item-scoped to `localize_dict.json` keys `Champions0507` and `Champions187003`; it locks only the base title and leaves edition suffix wording to the containing UI item.

Durable implementation on `main`:
- `scripts/harden_monthly_twinkle_finding.py` at commit `94ecd3f92f8d16e51642d772052b22ee177022b1`.
- `tests/test_monthly_twinkle_finding_hardening.py` at commit `9f6f5cad5c84c9856514a548afa43195a110c2b4`.
- Rule id: `publication.monthly_twinkle`; review decision id: `audit.finding.publication-monthly-twinkle`.
- Regression coverage asserts both findings resolve through the same key-scoped contains rule, remain idempotent, and do not match an unrelated key.

Production acceptance is still pending. Push-triggered `Validate`, `Sync translation context`, and `Sync translation review plan` runs for the implementation/test commits must succeed before incrementing the maintenance completion counter or claiming the findings closed. The context sync workflow automatically executes all `scripts/harden_*_finding.py` hardeners before applying review locks and persists generated glossary changes back to `main`.
