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

`src/game.py` also holds `distraction_manager` (a `DistractionManager`), which is reset alongside `raccoon_manager` inside `Game.reset_level`. The distraction manager is updated every frame in both `CameraState` and `YardState`. There is no time penalty for watching cameras — raccoons always stay in their zone until the player enters the yard.

### State flow

```
menu → camera ↔ transition → yard → result → camera (loop)
                                           ↘ level_complete → camera (next level)
                                           ↘ game_over → menu
```

States communicate only through the `data` dict passed to `on_enter` and through attributes on `self.game`. States never import each other.

### Key invariants

- `game.raccoons_paused = True` during `TransitionState` — raccoons must not change zones while the player is walking to a door, otherwise the zone they chose could be empty on arrival.
- `RaccoonManager.respawn_if_needed(exclude_zone)` is called every time `CameraState` is entered. Pass `exclude_zone` so new raccoons don't spawn in the zone the player just came from.
- All timing uses delta-time (`dt` in seconds, clamped to 50 ms). Never use frame counts or `pygame.time.delay`.
- `YardState` tracks `self.raccoons` (a list), never a single raccoon. `on_enter` calls `raccoons_in_zone()` to get every raccoon in the target zone, applies flee probability to each independently, and calls `set_yard_position_from_camera` on each survivor. `_take_photo` catches all raccoons whose `yard_pos` falls inside the viewfinder hit zone at the moment of the click. `Viewfinder.update` accepts a list of positions and sets `is_hit = True` if any of them are inside the hit zone.
- All levels use `raccoon_count = 1`. With one raccoon across four zones, cameras are mostly empty — the player watches and waits for a raccoon to walk into frame.
- Distraction entities (birds, leaves, trash bags) are purely cosmetic — they do not trigger the viewfinder hit test and are never counted as catches. `DistractionManager` is updated in `CameraState.update` and `YardState.update`; do not update it in `TransitionState`.

### Settings

All tunable constants live in `settings.py` at the project root. Target Python version is **3.11**.

## Tests

Unit tests live in `tests/` and can be run without a display:

```bash
python3.11 -m pytest tests/ -v
```

Tests cover the three distraction entity types and `DistractionManager`. They do not import pygame — entity logic is pure Python.

## Subdirectory guides

Detailed documentation for each subsystem lives alongside the code it describes:

- `src/entities/CLAUDE.md` — raccoon entry behaviour, zone-hop animation
- `src/states/CLAUDE.md` — yard raccoon movement, ADS (zoom) viewport
- `src/systems/CLAUDE.md` — adding a new level, adding a new zone
- `src/ui/CLAUDE.md` — graphics primitives, night-time visual theme, camera ↔ yard visual consistency
