# src/states

This directory contains all game states: `menu_state.py`, `camera_state.py`, `transition_state.py`, `yard_state.py`, `result_state.py`, `level_complete_state.py`, `game_over_state.py`, and `base_state.py`.

## Yard raccoon movement

Raccoons in the yard do **not** bounce at the screen edges — they walk off either side freely (same behaviour as the camera zone-hop). Movement is deliberately erratic: `YardState` maintains parallel lists `_erratic_timers`, `_yard_vy`, and `_vy_timers` (one entry per raccoon). Every 0.2–0.7 s there is a 75% chance of a sharp x-direction/speed change (60–160 px/s); y-drift also flips every 0.3–0.9 s, keeping raccoons bouncing within the foreground grass band (`yard_rect.height * 0.62` → `yard_rect.bottom - 40`). These lists are rebuilt in `on_enter` alongside `self.raccoons`.

## ADS (zoom) viewport

`YardState._ads_viewport()` maps the full mouse range linearly to the full panning range so there are no dead zones at screen edges. The panning bounds are derived from the lens geometry (`_LENS_CX ± _LENS_R` mapped into yard-space) so the lens circle can reach every edge of the yard without showing content outside it. The viewport may therefore extend slightly beyond `_yard_surf`; `_get_vp_surf()` handles this safely by blitting only the in-bounds region and filling the rest with `COL_BG` (those pixels are always hidden by the dark vignette overlay outside the lens circle).
