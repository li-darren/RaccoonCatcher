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
