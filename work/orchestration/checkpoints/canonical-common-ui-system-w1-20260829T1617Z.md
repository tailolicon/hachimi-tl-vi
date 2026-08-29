# Common UI/System canonical hardening — W1 checkpoint

Task: `canonical-common-ui-system`
Stage: `ready_for_finalize`
Branch: `canonical-common-ui-system-hardening`

## Domain-work result

Substantive high-frequency Common UI/System hardening is complete enough for serial integration. Permanent exact-key/item-scoped rules live in `scripts/harden_common_ui_labels.py` with regression coverage in `tests/test_common_ui_labels_hardening.py`. No `localized_data/**` files were edited.

Canonical targets hardened:

- `Common0001` `确定` -> `Xác nhận`
- `Common0002`, `Common0004` `取消` -> `Hủy`
- `Common0005` `选择中` -> `Đang chọn`
- `Common0007` `关闭` -> `Đóng`
- `Common0008` `更改` -> `Thay đổi` (compact `Đổi`)
- `Common0009` `确认` -> `Xác nhận`
- `Common0013` `使用` -> `Sử dụng` (compact `Dùng`)
- `Common0020` `全部` -> `Tất cả`
- `Common0022` `搜索` -> `Tìm kiếm` (compact `Tìm`)
- `Common0023` `决定` -> `Xác nhận`
- `Common0030` `默认` -> `Mặc định`
- `Common0082` `返回` -> `Quay lại`
- `Common0083` `下项` -> `Tiếp theo`
- `Common0084` `卸下` -> `Tháo`
- `Common0085` `无指定` -> `Không chỉ định`
- `Common0087` `排序` -> `Sắp xếp`
- `Common0096` `重置` -> `Đặt lại`
- `Common0097` `不能选择` -> `Không thể chọn`
- `Common0098` `筛选` -> `Lọc`
- `Common0100` `升序` -> `Tăng dần`
- `Common0101` `降序` -> `Giảm dần`
- `Common0136` `显示顺序` -> `Thứ tự hiển thị`
- `RoomMatch0117` bare `详情` -> `Chi tiết`
- `Circle0086` bare `取消` -> `Hủy`

All records are scoped to exact `localize_dict.json` keys. Regression negatives cover story prose, cancellation status/compound actions, and compound `详情` headings.

## Important conflict caught and permanently guarded

A transient branch revision incorrectly inferred `Common0092`/`Common0093` as generic On/Off labels. Direct current-corpus evidence proves these keys are Race phases:

- `Common0092` `中盘` -> `Giữa cuộc đua`
- `Common0093` `终盘` -> `Cuối cuộc đua`

The invalid `common_ui.on.common0092` and `common_ui.off.common0093` records were removed. The permanent hardener deletes those IDs if encountered, and regressions assert the Race-phase keys remain unmatched by Common-UI rules.

## Cross-domain exclusions

Intentionally left overlapping concepts to their owning domains instead of creating split-brain rules:

- Training Level, Max Energy, stat cap/limit -> Training/Support;
- Reward, required/owned resource quantities, shop/purchase, consumables/materials -> Missions/Resources;
- race-phase labels `Common0091`-`Common0093` -> Race;
- character/training-specific status labels -> Character/Training UI.

No broad aliases were added for generic prose such as `详情`, `取消`, `使用`, `搜索`, or `更改`. Rare/ambiguous generic-looking strings without strong exact evidence were intentionally not locked.

## Validation and cleanup evidence

Final TEMP validation run `33262561076` completed successfully on the final substantive branch content:

- focused Common UI regressions: success;
- full pytest: success;
- canonical materialization: success;
- second hardener run/no-op proof: success.

The temporary validation workflow was removed in branch commit `c174ae9c6b40fa02913f83640729695336511157`. A post-cleanup compare shows only permanent glossary/hardener/tests plus this checkpoint differ from live `main`; no TEMP workflow and no `localized_data/**` edits remain.

## Integration handoff

This domain is ready for the serial integration lane under `CANONICAL_PARALLEL.md`.

Finalizer should:

1. compare/reconstruct the permanent branch changes onto current live `main`, preserving concurrently integrated domains;
2. resolve any cross-domain canonical conflict explicitly rather than last-writer-wins;
3. run full validation on integrated `main`;
4. rebuild retrospective review context;
5. run production Sync and second unchanged no-op Sync;
6. spot-check Common0001/Common0002, Common0007, Common0087/Common0098, Common0092/Common0093 negative guard, and RoomMatch0117 compound-negative behavior;
7. only then mark `canonical-common-ui-system` complete.
