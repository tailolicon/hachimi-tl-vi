# Common UI/System canonical hardening — W1 checkpoint

Task: `canonical-common-ui-system`
Stage: `domain_work`
Branch: `canonical-common-ui-system-hardening`

## Durable scope completed so far

Added permanent exact-key/item-scoped hardening in `scripts/harden_common_ui_labels.py` with regression coverage in `tests/test_common_ui_labels_hardening.py` for high-frequency generic controls/status labels. No `localized_data/**` files were edited.

Current canonical targets covered:

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

All rules are scoped to exact `localize_dict.json` keys. Regression negatives cover story prose, cancellation status/compound actions, and compound `详情` headings.

## Important conflict caught and corrected

A transient branch revision incorrectly treated `Common0092`/`Common0093` as generic On/Off labels. Direct current-corpus evidence shows these are race phases:

- `Common0092` `中盘` -> `Giữa cuộc đua`
- `Common0093` `终盘` -> `Cuối cuộc đua`

The invalid `common_ui.on.common0092` and `common_ui.off.common0093` records were removed. The permanent hardener now deletes those IDs if encountered, and regression coverage asserts the race-phase keys remain unmatched by Common-UI rules.

## Cross-domain exclusions

Intentionally did not harden overlapping concepts owned by parallel domains:

- Training Level, Max Energy, stat cap/limit -> Training/Support;
- Reward, required/owned resource quantities, shop/purchase, consumables/materials -> Missions/Resources;
- race-phase labels `Common0091`-`Common0093` -> Race;
- character/training-specific status labels -> Character/Training UI.

No broad aliases were added for generic prose such as `详情`, `取消`, `使用`, `搜索`, or `更改`.

## Validation evidence so far

Earlier branch run `33262122728` passed focused regressions, full pytest, canonical materialization, and a second hardener no-op proof. Later green runs validated the removal of the invalid `Common0092`/`Common0093` toggle rules and subsequent expanded controls. Latest validation for the final expanded set is still running at this checkpoint and must be verified before handoff.

Temporary validation workflow `.github/workflows/temp-common-ui-validation.yml` remains branch-local and MUST be removed before integration/handoff.

## Remaining in this worker run

1. verify the latest focused/full-test/materialization/no-op run;
2. ensure final materialized branch head is captured;
3. remove the temporary workflow;
4. decide whether current substantive Common UI coverage is sufficient for `ready_for_integration` under `CANONICAL_PARALLEL.md` or leave explicit `domain_work` continuation evidence;
5. checkpoint/release the domain claim only at the normal session handoff boundary.
