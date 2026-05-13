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

## Tests

Run all tests (no display required):

```bash
python3.11 -m pytest tests/ -v
```

Run a single test file or specific test:

```bash
python3.11 -m pytest tests/test_raccoon.py -v
python3.11 -m pytest tests/test_raccoon.py::test_cam_y_initialized_in_ground_band -v
```

Tests avoid pygame by testing only pure-logic modules and using `tests/helpers.py` fakes (`FakeGame`, `FakeRaccoon`, `FakeZoneManager`, etc.) for state tests that need a game object.

## Architecture

The game is a Pygame state machine. `src/game.py` owns the main loop, the screen, the clock, and all shared mutable state (`score`, `level`, `timer_remaining`, `raccoons_paused`). It instantiates every state once at startup and switches between them via `Game.change_state(name, **kwargs)`, which calls `on_exit()` on the outgoing state and `on_enter(data_dict)` on the incoming one.

`src/game.py` also holds `distraction_manager` (a `DistractionManager`), which is reset alongside `raccoon_manager` inside `Game.reset_level`. The distraction manager is updated every frame in both `CameraState` and `YardState`. There is no time penalty for watching cameras — raccoons always stay in their zone until the player enters the yard.

### State flow

```
menu → camera ↔ transition → yard → result → camera (loop)
                                           ↘ level_complete → camera (next level)
                                           ↘ game_over → menu
```

States communicate only through the `data` dict passed to `on_enter` and through attributes on `self.game`. States never import each other.

### Pure-logic modules

Several files contain pygame-free logic extracted specifically for testability. Always extend these rather than embedding logic in state/UI code:

| File | Purpose |
|------|---------|
| `src/states/result_logic.py` | Next-state decision after a photo result |
| `src/states/transition_logic.py` | Fade-alpha computation for `TransitionState` |
| `src/states/yard_logic.py` | ADS viewport geometry and raccoon-in-lens hit test |
| `src/systems/zone_layout.py` | Camera grid and yard rect geometry |
| `src/ui/hud_format.py` | Timer string formatting, HUD colour thresholds |

### Key invariants

- `game.raccoons_paused = True` during `TransitionState` — raccoons must not change zones while the player is walking to a door, otherwise the zone they chose could be empty on arrival.
- `RaccoonManager.respawn_if_needed(exclude_zone)` is called every time `CameraState` is entered. Pass `exclude_zone` so new raccoons don't spawn in the zone the player just came from.
- All timing uses delta-time (`dt` in seconds, clamped to 50 ms). Never use frame counts or `pygame.time.delay`.
- `YardState` tracks `self.raccoons` (a list), never a single raccoon. `on_enter` calls `raccoons_in_zone()` to get every raccoon in the target zone, applies flee probability to each independently, and calls `set_yard_position_from_camera` on each survivor. `_take_photo` catches all raccoons whose `yard_pos` falls inside the viewfinder hit zone at the moment of the click. `Viewfinder.update` accepts a list of positions and sets `is_hit = True` if any of them are inside the hit zone.
- All levels use `raccoon_count = 1`. With one raccoon across four zones, cameras are mostly empty — the player watches and waits for a raccoon to walk into frame.
- Distraction entities (birds, leaves, trash bags) are purely cosmetic — they do not trigger the viewfinder hit test and are never counted as catches. `DistractionManager` is updated in `CameraState.update` and `YardState.update`; do not update it in `TransitionState`.

### Raccoon camera coordinates

`Raccoon` uses two normalised coordinate pairs:

- **`cam_x` / `cam_vx`** — horizontal position (0 = left edge, 1 = right edge). Raccoons bounce at 0.05/0.95 and hop zones by walking off-screen past −0.2/1.2.
- **`cam_y` / `cam_vy`** — vertical position (0 = top, 1 = bottom). Constrained to the ground band 0.58–0.75 with slow drift (0.006–0.014 units/s) and random direction reversals every 2–6 s. Frozen during zone-hop exits.

`set_yard_position_from_camera` maps both `cam_x` and `cam_y` into yard pixel space, clamping Y to the foreground grass band (≥ 62% of yard height).

### Settings

All tunable constants live in `settings.py` at the project root. Target Python version is **3.11**.

## Subdirectory guides

Detailed documentation for each subsystem lives alongside the code it describes:

- `src/entities/CLAUDE.md` — raccoon entry behaviour, zone-hop animation
- `src/states/CLAUDE.md` — yard raccoon movement, ADS (zoom) viewport
- `src/systems/CLAUDE.md` — adding a new level, adding a new zone
- `src/ui/CLAUDE.md` — graphics primitives, night-time visual theme, camera ↔ yard visual consistency
