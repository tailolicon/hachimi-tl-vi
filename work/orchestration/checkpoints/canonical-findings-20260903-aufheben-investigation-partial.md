# Canonical finding checkpoint — 霹雳中的奥伏赫变 / 霹靂のアウフヘーベン

Worker: `gpt56sol-auto11-20260903T1158Z`

Candidate finding: `cf-1e27154bb898948c`.

## Verified repository evidence

- The active retrospective-review plan contains 12 occurrences of zh-CN `霹雳中的奥伏赫变` bridged to JP `霹靂のアウフヘーベン`; inherited Vietnamese output is inconsistent (`Lôi Đình Phá Bích`, `Long Trời Lở Đất - Aufheben`, and historical `Aufheben giữa lôi đình`).
- Existing review routing correctly defers those rows while `cf-1e27154bb898948c` is active instead of accepting a one-off local rewrite.
- Historical curation at locator `47:100841` already identified `アウフヘーベン` as a specialized loanword/philosophical term and deferred transliteration-vs-semantic rendering pending project-wide policy.
- `glossary/skill_name_style.json` is now live project-wide policy for Skill titles: translate the semantic core, keep titles concise/game-native, preserve official punctuation/symbols, render idiomatic/figurative titles by intended meaning rather than literal order, and reuse a locked Vietnamese form for repeated Skill identities.
- That general policy is sufficient to reject arbitrary inheritance and community-name promotion, but it still does not uniquely choose a Vietnamese canonical title for this specialized proper Skill identity.
- `scripts/canonical_findings.py` only treats an open/deferred finding as resolved once it has a canonical resolution derived from approved terminology/source-bridge evidence (or an explicit ignore review resolution). This finding currently has neither.
- The repository hardening precedent (`scripts/harden_staho_tv_finding.py`) uses an idempotent terminology lock only when the underlying identity/display evidence is strong enough; inventing a lock merely to clear the audit gate would violate that precedent.

## External corroboration retained from the prior checkpoint

- Public Uma Musume references identify Tanino Gimlet's JP unique Skill as `霹靂のアウフヘーベン` / zh-CN `霹雳中的奥伏赫变`.
- `Wall Crack Aufheben` appears as a community English label, not verified official English-release evidence, and must not be promoted as official canonical evidence.

## Decision

Keep `cf-1e27154bb898948c` open. The repository now has a general Skill-title style convention, but still lacks title-specific authoritative/project-approved evidence that uniquely selects the Vietnamese canonical wording for the specialized `アウフヘーベン` identity.

Do not lock `Lôi Đình Phá Bích`, `Long Trời Lở Đất - Aufheben`, `Aufheben giữa lôi đình`, or `Wall Crack Aufheben` from the evidence currently available. Do not patch `localized_data/**` examples. The 12 affected retrospective entries should continue to defer until title-specific canonical evidence or an explicit convention for this loanword class is added.
