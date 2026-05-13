# src/systems

This directory contains the game systems: `level_config.py` (level definitions), `raccoon_manager.py` (spawning/respawning), `zone_manager.py` (zone layout and positioning), and `distraction_manager.py` (visual distraction entities).

## DistractionManager

`distraction_manager.py` manages three lists — `birds`, `leaves`, `trash_bags` — plus per-zone spawn timers for birds and leaves.

- **`reset(num_zones)`** — clears birds and leaves, creates one fresh `TrashBag` per zone at a random position, and resets all spawn timers to a random value drawn from `BIRD_SPAWN_INTERVAL` / `LEAF_SPAWN_INTERVAL`. Call this alongside `raccoon_manager.populate()` in `Game.reset_level`.
- **`update(dt)`** — ticks spawn timers; when a timer fires it appends a new `Bird` or `Leaf` for that zone (if below `BIRD_MAX_PER_ZONE` / `LEAF_MAX_PER_ZONE`) and resets the timer. Also calls `update(dt)` on every bird/leaf and removes those that return `True` (off-screen). Trash bags are never updated.
- **`birds_in_zone(i)`**, **`leaves_in_zone(i)`**, **`trash_bags_in_zone(i)`** — filter the respective list by `zone_index`. Use these in rendering, mirroring `RaccoonManager.raccoons_in_zone`.

`game.distraction_manager` is updated in both `CameraState.update` and `YardState.update` so entities keep moving regardless of which view the player is in.

## Adding a new level

Edit `src/systems/level_config.py` — append a `LevelConfig` to the `LEVELS` list. The game automatically treats the last entry as the final level and shows a win screen after it.

## Adding a new zone

1. Increment `NUM_ZONES` in `settings.py` and add the name to `ZONE_NAMES`.
2. Add a zone color tuple to `ZoneManager._build_zones` in `src/systems/zone_manager.py`.
3. Add a drawing branch in `src/ui/renderer.draw_yard_background` for the new `zone_index`.
4. Adjust the camera grid layout if moving away from 2×2 (positions are computed in `ZoneManager._build_zones`).
