# src/entities

This directory contains the core entity classes: `raccoon.py` (the `Raccoon` entity) and `viewfinder.py` (the `Viewfinder` entity).

## Raccoon entry behaviour

85% of the time a raccoon spawns just off the left or right edge of the camera feed (`cam_x` outside `[0, 1]`) and walks in slowly (0.015–0.04 units/sec), taking roughly 5–16 seconds to become visible. The remaining 15% spawn in the centre of the feed as before. While `_entering = True` the zone-hop timer does not tick, so a raccoon cannot teleport to another zone before the player has had a chance to see it. Once `cam_x` enters `[0, 1]` the raccoon switches to its normal wander speed and `_entering` is cleared.

`Raccoon.is_camera_visible` returns `True` when `cam_x ∈ [0, 1]`. The camera feed only draws and counts visible raccoons. The door button is always enabled — the player must decide for themselves when to enter a zone based on what they see on camera, with no explicit raccoon count shown.

## Zone-hop animation

Raccoons do not teleport between zones instantly. When a raccoon's `move_timer` expires, `_hopping = True` is set and the raccoon accelerates off its current camera edge. Once `cam_x` exceeds 1.2 or drops below -0.2 (fully off-screen), `zone_index` is updated to `_hop_target_zone` and `cam_x` is placed at the opposite edge so the raccoon walks on-screen from the far side of the new camera feed. The hop arrival also sets `_entering = True` so the move timer stays paused until the raccoon is fully on-screen in the new zone. Never change `zone_index` directly in `update()` — the commit always happens inside `update_wander()` once the raccoon is off-screen.
