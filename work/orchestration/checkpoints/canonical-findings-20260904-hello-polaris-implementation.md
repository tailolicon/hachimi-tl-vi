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

## Production acceptance

Accepted on live `main`.

- Validate run `33826454594`: completed / success.
- Sync translation context run `33826454608`: completed / success.
- Sync translation review plan run `33826454592`: completed / success.
- Live production review plan `tr-p3-67f8551f7780-6b63119b0563-b5c0bcb3bd-2544610eef`, batch `b0176`, item `text_data_dict.json` `16/1175` embeds community rule `song.hello_polaris` with preferred `Hello Polaris`; the accepted target is present and the forbidden zh-CN title is absent.
- The same live batch contains no `cf-7af7f3692f9a938f` reference, confirming the canonical finding no longer blocks the item.

This finding may advance the maintenance completed count.
