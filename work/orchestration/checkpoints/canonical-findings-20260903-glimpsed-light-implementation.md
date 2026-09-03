# Canonical finding implementation: 垣間見た光

Finding: `cf-263f7b206a317078`

- zh-CN bridge: `一线曙光`
- Verified JP Skill 203522: `垣間見た光`
- Canonical Vietnamese target: `Thoáng Thấy Ánh Sáng`
- Historical target rejected: `Tia bình minh`

## Evidence and reasoning

Pinned curation evidence in `work/curation/results/term-0008/sol-5d124e33-bf06-4eb5-b777-d79c479652fb.json` identifies Skill 203522 as JP `垣間見た光` and explicitly flags the zh-CN bridge as changing the image into a ray of dawn. Repository skill-name policy requires preserving JP meaning/motif when zh-CN materially diverges. `垣間見た` is a glimpse/brief sight and `光` is light, so `Thoáng Thấy Ánh Sáng` keeps the original motif without importing the bridge's dawn imagery.

## Implementation

- Hardener: `scripts/harden_glimpsed_light_finding.py` at commit `61825ee006690883e547584d97ccb92ab4d538ae`.
- Regression tests: `tests/test_glimpsed_light_finding_hardening.py` at commit `ef4df1ddb85daf2fe60aaf57cb8d1f3fda3b5bb6`.
- Community rule: `skill.glimpsed_light`, exact source `一线曙光`, category 147 only.
- Terminology decision: `audit.finding.skill-glimpsed-light`, JP evidence `垣間見た光`.
- Finding `cf-263f7b206a317078` receives the reviewed target so canonical refresh can resolve it positively.

## Remaining acceptance

Require successful Validate, production Sync translation context, refreshed review plan, and live context showing the finding absent with `skill.glimpsed_light` embedded.
