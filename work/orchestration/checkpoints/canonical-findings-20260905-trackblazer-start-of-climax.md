# Canonical finding research — Trackblazer: Start of the Climax

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260905T185100Z`

Finding: `cf-a95679214256d891`

## Live finding

- zh-CN source: `巅峰赛开幕`
- active review evidence: `text_data_dict.json`, category/key `119/4`
- full source item: `Make a new track!!\n～巅峰赛开幕～`
- historical Vietnamese: `Make a new track!!\n～Climax khai mạc～`
- finding match mode: `contains`
- source path: `text_data_dict.json`
- concept: `Make a new track!! scenario subtitle`
- kind: `system_label`

## Identity and Global localization evidence

The source is the zh-CN bridge for JP `クライマックス開幕`, the subtitle of the third Career scenario originally released on JP as `Make a new track!! ～クライマックス開幕～`.

Current Global references identify the released English scenario as **Trackblazer: Start of the Climax**. GameTora's current Global scenario guide states that Trackblazer is the Global name for Make a New Track and records the Global release on 2026-03-12. Umamusume Wiki's current scenario page gives the full English title `Trackblazer: Start of the Climax` and maps it to JP `Make a new track!! ～クライマックス開幕～`.

Evidence checked 2026-09-05:

- https://gametora.com/umamusume/trackblazer
- https://umamusu.wiki/Game%3ATrackblazer

Therefore the player-facing bridge for the subtitle `巅峰赛开幕` is `Start of the Climax`; retaining the mixed calque `Climax khai mạc` is no longer justified.

## Durable hardening

- `7d9b9ac8da280fbd4d06e45b04b625d5fa1715ef` adds `scripts/harden_trackblazer_start_of_climax_finding.py`.
- The hardener adds community rule `scenario.trackblazer.start_of_the_climax`, source alias `巅峰赛开幕`, preferred/accepted target `Start of the Climax`, restricted to `text_data_dict.json` and preserving the finding's `contains` semantics.
- It also adds explicit terminology-review lock `audit.finding.trackblazer-start-of-the-climax` with JP identity `クライマックス開幕`.
- `575fde90934aa1b42c0e1cc597efbc0afac905c9` adds regression coverage for idempotence, canonical/review resolution, active-finding clearance, and path containment.

## Verification state

At this checkpoint the hardener and regression are on live `main`. Validate, Context Sync, and Review Plan Sync were still running, so **do not increment maintenance completed_count yet**. Completion requires green CI plus production materialization of both the canonical rule and finding resolution on `main`.
