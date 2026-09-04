# Canonical finding research — Tracen Ondo

Finding: `cf-5c83fe60c17ea214`

- source title: `トレセン音頭`
- canonical target: `Tracen Ondo`
- finding class: proper-name / named song title

## Evidence basis

- Official Lantis WINNING LIVE 13 lists `トレセン音頭` as track 1 and identifies it as the Uma Musume 2.5th-anniversary song (release 2023-09-06).
- Established English-facing music catalogs identify the same Lantis release as `Tracen Ondo`; Shazam lists `Tracen Ondo` on WINNING LIVE 13 with label Lantis and the same 2023-09-06 release date.
- The established Uma Musume English community discography also maps Japanese `トレセン音頭` directly to English `Tracen Ondo`.

## Decision

Evidence is sufficient to preserve the named-song identity as `Tracen Ondo`. Do not semantically translate `音頭` into a Vietnamese descriptive phrase for this exact title.

If this finding remains live priority after the current maintenance item is accepted/skipped, implement an exact `text_data_dict.json` item-scoped song rule and terminology lock, with idempotent regression plus negative coverage for longer prose/other source files. Acceptance still requires the repository's normal Validate + production context/review sync gates and live generated-context verification.
