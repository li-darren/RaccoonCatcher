# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```bash
python3.11 main.py
```

Install the single dependency first if needed:

```bash
python3.11 -m pip install pygame==2.5.2
```

To test imports without a display (e.g. in CI or headless environments):

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3.11 -c "..."
```

## Architecture

The game is a Pygame state machine. `src/game.py` owns the main loop, the screen, the clock, and all shared mutable state (`score`, `level`, `timer_remaining`, `camera_room_elapsed`, `raccoons_paused`). It instantiates every state once at startup and switches between them via `Game.change_state(name, **kwargs)`, which calls `on_exit()` on the outgoing state and `on_enter(data_dict)` on the incoming one.

### State flow

```
menu → camera ↔ transition → yard → result → camera (loop)
                                           ↘ level_complete → camera (next level)
                                           ↘ game_over → menu
```

States communicate only through the `data` dict passed to `on_enter` and through attributes on `self.game`. States never import each other.

### Key invariants

- `game.raccoons_paused = True` during `TransitionState` — raccoons must not change zones while the player is walking to a door, otherwise the zone they chose could be empty on arrival.
- `game.camera_room_elapsed` accumulates while in `CameraState` and resets to 0 at the start of `YardState.on_enter`. It drives the raccoon flee-probability formula: the longer the player watches cameras, the more likely a raccoon bolts before they arrive.
- `RaccoonManager.respawn_if_needed(exclude_zone)` is called every time `CameraState` is entered. Pass `exclude_zone` so new raccoons don't spawn in the zone the player just came from.
- All timing uses delta-time (`dt` in seconds, clamped to 50 ms). Never use frame counts or `pygame.time.delay`.
- `YardState` tracks `self.raccoons` (a list), never a single raccoon. `on_enter` calls `raccoons_in_zone()` to get every raccoon in the target zone, applies flee probability to each independently, and calls `set_yard_position_from_camera` on each survivor. `_take_photo` catches all raccoons whose `yard_pos` falls inside the viewfinder hit zone at the moment of the click. `Viewfinder.update` accepts a list of positions and sets `is_hit = True` if any of them are inside the hit zone.

### Zone-hop animation

Raccoons do not teleport between zones instantly. When a raccoon's `move_timer` expires, `_hopping = True` is set and the raccoon accelerates off its current camera edge. Once `cam_x` exceeds 1.2 or drops below -0.2 (fully off-screen), `zone_index` is updated to `_hop_target_zone` and `cam_x` is placed at the opposite edge so the raccoon walks on-screen from the far side of the new camera feed. Never change `zone_index` directly in `update()` — the commit always happens inside `update_wander()` once the raccoon is off-screen.

### Camera ↔ yard visual consistency

- The camera feed background is a pre-rendered, scaled-down copy of the full yard background (`draw_yard_background` drawn onto a 1280×660 buffer, then `pygame.transform.scale`'d to the tile size). This is cached per zone in `CameraFeed._bg_cache`.
- The raccoon scale in the camera feed uses `min(r.width/1280, r.height/660)` — the same ratio used to scale the background — so raccoon size is proportionally identical in both views.
- Raccoons are drawn at `r.height * 0.65` in the camera, which maps exactly to `yard_rect.top + yard_rect.height * 0.65` (~489 px) in the yard. `set_yard_position_from_camera` uses this mapping so the raccoon appears at the same relative position after transition.
- `set_yard_position` (random placement) also restricts y to `yard_rect.top + yard_rect.height * 0.62` or lower, keeping raccoons in the foreground grass below all zone props (fences, shed, gate, garden tops all end above the 60% mark).

### Yard raccoon movement

Raccoons in the yard do **not** bounce at the screen edges — they walk off either side freely (same behaviour as the camera zone-hop). Movement is deliberately erratic: `YardState` maintains parallel lists `_erratic_timers`, `_yard_vy`, and `_vy_timers` (one entry per raccoon). Every 0.2–0.7 s there is a 75% chance of a sharp x-direction/speed change (60–160 px/s); y-drift also flips every 0.3–0.9 s, keeping raccoons bouncing within the foreground grass band (`yard_rect.height * 0.62` → `yard_rect.bottom - 40`). These lists are rebuilt in `on_enter` alongside `self.raccoons`.

### Night-time visual theme

The game is set at night. Key colour values:
- `COL_BG` (letterbox/fill): `(5, 8, 18)` — dark navy
- Sky in `draw_yard_background`: `(5, 8, 28)`
- Grass in `draw_yard_background`: `(10, 38, 10)`
- The moon is drawn with a dim halo ring behind it; nine stars are scattered across the sky strip.

`draw_raccoon` accepts a `camera_mode: bool = False` parameter. When `True` (used by `CameraFeed`), the eyes skip the dark pupil and instead render a bright green glow halo + white reflection to simulate tapetum eye-shine under IR/CCTV light. The yard view passes `camera_mode=False` (default) and keeps normal eyes.

### Adding a new level

Edit `src/systems/level_config.py` — append a `LevelConfig` to the `LEVELS` list. The game automatically treats the last entry as the final level and shows a win screen after it.

### Adding a new zone

1. Increment `NUM_ZONES` in `settings.py` and add the name to `ZONE_NAMES`.
2. Add a zone color tuple to `ZoneManager._build_zones` in `src/systems/zone_manager.py`.
3. Add a drawing branch in `src/ui/renderer.draw_yard_background` for the new `zone_index`.
4. Adjust the camera grid layout if moving away from 2×2 (positions are computed in `ZoneManager._build_zones`).

### Graphics

All graphics are drawn with `pygame.draw` primitives — there are no image assets. `src/ui/renderer.py` contains the two shared drawing functions (`draw_raccoon`, `draw_yard_background`) used by both the camera feeds and the yard view. Semi-transparent overlays (CCTV tint, shutter flash) use `pygame.SRCALPHA` surfaces created once and reused — never recreate them per frame.

### Settings

All tunable constants live in `settings.py` at the project root. Target Python version is **3.11**.
