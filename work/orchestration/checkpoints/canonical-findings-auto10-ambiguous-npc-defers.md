# Canonical findings maintenance checkpoint — ambiguous NPC identity defers

Claim: `canonical-findings-maintenance-gpt56sol-auto10-20260831T1822Z`

Live review evidence re-opened several NPC display-name identities whose zh-CN kanji do not uniquely determine a Japanese given-name reading. Targeted repository and public-reference checks did not establish authoritative JP furigana/readings for these identities.

Permanent explicit-defer decisions were added for:

- `空(NPC)` — Sora is plausible but not uniquely established;
- `光(NPC)` — Hikari/Hikaru and other readings are possible;
- `明人(NPC)` — repository evidence already contains competing Akihito/Akito renderings;
- `进(NPC)` / JP `進` — Susumu is plausible but not uniquely established;
- `彻(NPC)` / JP `徹` — Toru is plausible but not uniquely established;
- `望(NPC)` — Nozomi/Nozomu and other readings are possible;
- `正人(NPC)` — Masato/Masahito and other readings are possible;
- `佳子(NPC)` — Yoshiko/Kako and other readings are possible.

These defers intentionally remain blocking. They prevent future stateless workers from repeatedly researching the same weak evidence and then canonizing a guessed Romanization. A later maintainer should replace an individual defer only when authoritative JP/Global identity evidence becomes available.

Hardener commit: `6099b74d945d75acf67ad8496ce0f4fdd0d0e4c6`
Regression-test commit: `fba13088a6461cf4db4314c9791397f14bc8e0bc`
