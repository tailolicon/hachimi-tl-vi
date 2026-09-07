# Canonical findings maintenance checkpoint — Ranzen Kappo Skill identity

Finding: `cf-84bac56a7f559d24` (`灿然阔步`)
Canonical target: JP `爛然闊歩`

## Live finding and identity diagnosis

The current retrospective review plan carries this as an active `proper_name` blocker on `text_data_dict.json` Skill title path `147/10570203`; current Vietnamese is the zh-CN-derived calque `Sải bước rạng ngời`.

Repository history had intentionally deferred the title because no verified JP alias was available at that time. Fresh identity verification now establishes the exact JP display title `爛然闊歩` for New Year Mr. C.B.; multiple current Japanese Uma Musume references agree on both the title and its distinctive long-spurt effect. No official Global title was verified, so this follows the repository's established JP-only Skill policy: preserve the exact Japanese player-facing title instead of inventing an English title or retaining a Chinese-derived Vietnamese calque.

## Scope decision

The live finding is source-path scoped (`text_data_dict.json`) with no JSON-path prefix. A category-147-only rule would therefore fail canonical-finding coverage semantics. The hardening rule is intentionally source-path scoped with `match_mode=exact`, which resolves the title itself while not consuming category-172 prose that merely contains `灿然阔步` inside a larger sentence.

## Durable implementation

- `5f682fca4ccace2143189babf45f2b9421fcaef0` adds `scripts/harden_ranzen_kappo_finding.py`.
- `43f54838d438877aea8216b6f00c3d728b66098d` adds `tests/test_ranzen_kappo_finding_hardening.py`.
- The regression covers hardener idempotence, canonical resolution, exact-only containment safety, and source-path isolation.

## Acceptance status

Production workflows triggered from the test commit:

- Validate `34121649485` — running at checkpoint time.
- Sync translation context `34121649530` — pending/running at checkpoint time.
- Sync translation review plan `34121649456` — pending/running at checkpoint time.

Do **not** increment maintenance `completed_count` beyond 195 yet. Completion requires green production validation, an applying Context Sync if generated canonical state changes, a subsequent unchanged Context Sync proving exact semantic no-op `Context is already current.`, and a green review-plan gate on synchronized context.