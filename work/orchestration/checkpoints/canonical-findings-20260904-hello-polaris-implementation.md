# Canonical finding implementation — Hello Polaris

Finding: `cf-7af7f3692f9a938f`

- live zh-CN title: `Hello 北极星`
- JP title: `ハロー・ポラリス`
- live item: `text_data_dict.json` category `16`, entry `1175`
- canonical target: `Hello Polaris`

## Evidence basis

The live zh-CN title maps to the Uma Musume song `ハロー・ポラリス`. Apple Music US and Shazam publish the Lantis release under the English title `Hello Polaris`; Apple Music also identifies the `WINNING LIVE 33` release under that title. Preserve that official English-facing proper-name identity rather than treating `北极星` as free prose.

## Implementation

- regression: `tests/test_hello_polaris_finding_hardening.py`
- hardener: `scripts/harden_hello_polaris_finding.py`
- community rule: `song.hello_polaris`
- terminology decision: `audit.finding.song-hello-polaris`
- source scope: exact match in `text_data_dict.json`

Implementation commits on live `main`:

- regression commit `6e36507faf3eb50c3deb1f224df60b99584b0054`
- hardener commit `1a9444378eae78589b4089cb0012d2787ff03684`

## Acceptance status

Pending production acceptance. Do not advance the maintenance completed count until required Validate, Sync translation context, and Sync translation review plan workflows succeed and the then-live generated review item `text_data_dict.json` `16/1175` embeds `song.hello_polaris` / `Hello Polaris` with `canonical_findings: []`.
