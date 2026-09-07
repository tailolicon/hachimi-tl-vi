# Canonical finding checkpoint — 固有加成 Global terminology policy correction

Finding: `cf-5cc239af1c9d7710` (`固有加成`) and companion `cf-823a42e63df66f92`.

A fresh repository-policy recheck corrected one part of the earlier recommendation: player-facing canonical identities prefer verified official/Global-facing game terminology when available. Released English support-card references identify JP `固有ボーナス` as **Unique Effect**. Therefore the canonical target should be `Unique Effect`, not a newly localized `Hiệu ứng riêng`.

The earlier concurrent implementation was still not safe because it used `match_mode=exact` for a reusable alias that occurs inside `固有加成详情`. Its removal remains correct.

The surviving live-main hardener was corrected at commit `9c0ce775d5bd407e15929ff33ade8416e47fb401` to combine both requirements:

- target: `Unique Effect`;
- `match_mode: contains`;
- `source_paths: [localize_dict.json]`;
- `key_exact: [Character0050, Character0196]`;
- negative scope for category-150 named unique effects / unrelated paths.

Any Context Sync that checked out main before `9c0ce775...` may reflect the superseded Vietnamese target and must not be used as final acceptance. Final acceptance must come from a Sync that includes `9c0ce775...`, followed by an unchanged/no-op Sync.
