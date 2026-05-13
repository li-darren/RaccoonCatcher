# src/states

This directory contains all game states: `menu_state.py`, `camera_state.py`, `transition_state.py`, `yard_state.py`, `result_state.py`, `level_complete_state.py`, `game_over_state.py`, and `base_state.py`.

## Yard raccoon movement

Raccoons in the yard do **not** bounce at the screen edges — they walk off either side freely (same behaviour as the camera zone-hop). Movement is deliberately erratic: `YardState` maintains parallel lists `_erratic_timers`, `_yard_vy`, and `_vy_timers` (one entry per raccoon). Every 0.2–0.7 s there is a 75% chance of a sharp x-direction/speed change (60–160 px/s); y-drift also flips every 0.3–0.9 s, keeping raccoons bouncing within the foreground grass band (`yard_rect.height * 0.62` → `yard_rect.bottom - 40`). These lists are rebuilt in `on_enter` alongside `self.raccoons`.

All raccoons in the target zone always appear in the yard — there is no flee mechanic. `on_enter` calls `set_yard_position_from_camera` on every raccoon returned by `raccoons_in_zone`.

## Distraction rendering

`CameraState.update` calls `game.distraction_manager.update(dt)` each frame, and passes `distraction_manager=self.game.distraction_manager` to each `CameraFeed.draw` call so feeds can render zone-filtered distractions.

`YardState.update` also calls `game.distraction_manager.update(dt)` so birds and leaves continue moving while the player is in the yard. `YardState.draw` renders birds and trash bags to `self._yard_surf` before raccoons, and leaves after raccoons (so leaves fall in front of everything). Distractions are hidden alongside raccoons when `self.photo_taken` is True (the shutter-flash-to-result transition is brief enough that this is not noticeable).

Distraction entities use normalised `cam_x` / `cam_y_frac` coordinates. Convert to yard pixels with `yr.left + int(entity.cam_x * yr.width)` / `yr.top + int(entity.cam_y_frac * yr.height)`.

## ADS (zoom) viewport

`YardState._ads_viewport()` maps the full mouse range linearly to the full panning range so there are no dead zones at screen edges. The panning bounds are derived from the lens geometry (`_LENS_CX ± _LENS_R` mapped into yard-space) so the lens circle can reach every edge of the yard without showing content outside it. The viewport may therefore extend slightly beyond `_yard_surf`; `_get_vp_surf()` handles this safely by blitting only the in-bounds region and filling the rest with `COL_BG` (those pixels are always hidden by the dark vignette overlay outside the lens circle).
