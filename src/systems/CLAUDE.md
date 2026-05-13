# src/systems

This directory contains the game systems: `level_config.py` (level definitions), `raccoon_manager.py` (spawning/respawning), and `zone_manager.py` (zone layout and positioning).

## Adding a new level

Edit `src/systems/level_config.py` — append a `LevelConfig` to the `LEVELS` list. The game automatically treats the last entry as the final level and shows a win screen after it.

## Adding a new zone

1. Increment `NUM_ZONES` in `settings.py` and add the name to `ZONE_NAMES`.
2. Add a zone color tuple to `ZoneManager._build_zones` in `src/systems/zone_manager.py`.
3. Add a drawing branch in `src/ui/renderer.draw_yard_background` for the new `zone_index`.
4. Adjust the camera grid layout if moving away from 2×2 (positions are computed in `ZoneManager._build_zones`).
