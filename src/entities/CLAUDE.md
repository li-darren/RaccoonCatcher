# src/entities

This directory contains all entity classes: `raccoon.py`, `viewfinder.py`, `bird.py`, `leaf.py`, and `trash_bag.py`.

## Distraction entities

Three purely cosmetic entity types create visual noise that may fool the player into thinking a raccoon is present. None of them interact with the viewfinder hit test.

**`Bird`** (`bird.py`) — flies across the sky band (`cam_y_frac ∈ [0.06, 0.30]`) in a straight horizontal line. Spawns off-screen at `cam_x = -0.12` (rightward) or `cam_x = 1.12` (leftward). `update(dt)` advances `cam_x` by `cam_vx * dt` and increments `wing_phase` (used by `draw_bird` for the flapping M-shape silhouette). Returns `True` when fully off the far edge (`cam_x < -0.2` or `> 1.2`), signalling the manager to remove it.

**`Leaf`** (`leaf.py`) — falls from near the top of the frame (`cam_y_frac` starts in `[-0.05, 0]`) to below the bottom (`> 1.1`). Horizontal position oscillates with a sine wave (`drift_amp`, `drift_freq`, `drift_phase`). `rotation` spins at `rot_speed` degrees/sec. Carries a `color` tuple drawn by `draw_leaf`. Returns `True` from `update(dt)` when off-screen below.

**`TrashBag`** (`trash_bag.py`) — static; no `update` method. Placed once per zone at a random `cam_x ∈ [0.15, 0.85]` and fixed `cam_y_frac = 0.65` (matching raccoon ground level). Does not move for the lifetime of the level.

## Raccoon entry behaviour

85% of the time a raccoon spawns just off the left or right edge of the camera feed (`cam_x` outside `[0, 1]`) and walks in slowly (0.015–0.04 units/sec), taking roughly 5–16 seconds to become visible. The remaining 15% spawn in the centre of the feed as before. While `_entering = True` the zone-hop timer does not tick, so a raccoon cannot teleport to another zone before the player has had a chance to see it. Once `cam_x` enters `[0, 1]` the raccoon switches to its normal wander speed and `_entering` is cleared.

`Raccoon.is_camera_visible` returns `True` when `cam_x ∈ [0, 1]`. The camera feed only draws and counts visible raccoons. The door button is always enabled — the player must decide for themselves when to enter a zone based on what they see on camera, with no explicit raccoon count shown.

## Zone-hop animation

Raccoons do not teleport between zones instantly. When a raccoon's `move_timer` expires, `_hopping = True` is set and the raccoon accelerates off its current camera edge. Once `cam_x` exceeds 1.2 or drops below -0.2 (fully off-screen), `zone_index` is updated to `_hop_target_zone` and `cam_x` is placed at the opposite edge so the raccoon walks on-screen from the far side of the new camera feed. The hop arrival also sets `_entering = True` so the move timer stays paused until the raccoon is fully on-screen in the new zone. Never change `zone_index` directly in `update()` — the commit always happens inside `update_wander()` once the raccoon is off-screen.
