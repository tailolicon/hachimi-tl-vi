# Source attribution and provenance

The Vietnamese translation pipeline is independent from UmaTL's English translation corpus and does not use UmaTL English text as generative-AI input.

## Current bootstrap source

For a recent, Hachimi-compatible JP-server corpus, source checkpoints are normalized from:

- Project: **Hachimi-Hachimi/tl-zh-cn**
- Language: Simplified Chinese (`zh-CN`)
- Upstream branch: `dev`
- Game region: Japanese server
- License stated by upstream: **CC BY-NC-SA 4.0** for the translation material described in its README, including translation work continued from Trainers' Legend G (TLG).
- Upstream project: https://github.com/Hachimi-Hachimi/tl-zh-cn

Every normalized source record stores the exact upstream commit SHA, source path, JSON path and source-text fingerprint. This allows later source upgrades to retranslate only changed material.

The upstream repository also contains or describes data originating from *Umamusume: Pretty Derby*. Copyright in the original game and its data remains with the respective rights holders. This repository claims no ownership of the original game data.

## Translation policy

The bootstrap flow is:

`recent zh-CN JP-server corpus -> Vietnamese draft -> language/style review -> terminology review -> structural QA -> Hachimi output`

When a sufficiently recent direct Japanese corpus becomes available, Japanese is preferred and the same stable locators/fingerprints are used to migrate entries incrementally.

Generated Vietnamese material derived from CC BY-NC-SA source material must retain the applicable attribution, non-commercial and share-alike obligations. This file is provenance documentation, not legal advice.
