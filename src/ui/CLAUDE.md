# src/ui

This directory contains the UI layer: `renderer.py` (shared drawing functions), `camera_feed.py` (per-zone camera display), and `hud.py` (heads-up display).

## Graphics

All graphics are drawn with `pygame.draw` primitives — there are no image assets. `src/ui/renderer.py` contains all shared drawing functions used by both camera feeds and the yard view. Semi-transparent overlays (CCTV tint, shutter flash) use `pygame.SRCALPHA` surfaces created once and reused — never recreate them per frame.

The distraction drawing functions in `renderer.py` follow the same `camera_mode: bool` convention as `draw_raccoon`:

- **`draw_bird(surface, pos, radius, facing_right, wing_phase, camera_mode)`** — M-shape silhouette; wing tips move up/down with `sin(wing_phase)`. `camera_mode=True` renders lighter pixels that read as greenish once the CCTV overlay is applied.
- **`draw_leaf(surface, pos, radius, rotation, color, camera_mode)`** — rotated ellipse approximated as a polygon. Falls back to a dot for `radius ≤ 2`. `camera_mode=True` replaces the colour with a flat `(80, 160, 80)`.
- **`draw_trash_bag(surface, pos, radius, camera_mode)`** — two overlapping dark circles (body + lump) with a small knot circle on top. Intentionally similar in mass to a large raccoon to fool a quick glance.

## Night-time visual theme

The game is set at night. Key colour values:
- `COL_BG` (letterbox/fill): `(5, 8, 18)` — dark navy
- Sky in `draw_yard_background`: `(5, 8, 28)`
- Grass in `draw_yard_background`: `(10, 38, 10)`
- The moon is drawn with a dim halo ring behind it; nine stars are scattered across the sky strip.

`draw_raccoon` accepts a `camera_mode: bool = False` parameter. When `True` (used by `CameraFeed`), the eyes skip the dark pupil and instead render a bright green glow halo + white reflection to simulate tapetum eye-shine under IR/CCTV light. The yard view passes `camera_mode=False` (default) and keeps normal eyes.

## Camera ↔ yard visual consistency

- The camera feed background is a pre-rendered, scaled-down copy of the full yard background (`draw_yard_background` drawn onto a 1280×660 buffer, then `pygame.transform.scale`'d to the tile size). This is cached per zone in `CameraFeed._bg_cache`.
- The raccoon scale in the camera feed uses `min(r.width/1280, r.height/660)` — the same ratio used to scale the background — so raccoon size is proportionally identical in both views. Distraction entities use the same scale factor.
- Raccoons are drawn at `r.height * 0.65` in the camera, which maps exactly to `yard_rect.top + yard_rect.height * 0.65` (~489 px) in the yard. `set_yard_position_from_camera` uses this mapping so the raccoon appears at the same relative position after transition. `TrashBag.cam_y_frac` is also `0.65` so it sits at the same ground level.
- `set_yard_position` (random placement) also restricts y to `yard_rect.top + yard_rect.height * 0.62` or lower, keeping raccoons in the foreground grass below all zone props (fences, shed, gate, garden tops all end above the 60% mark).

## Draw order in camera feed and yard

Both views use the same depth order to keep entities visually consistent:

```
Background → Birds → Trash bags → Raccoons → Leaves → CCTV tint / overlay
```

In the camera feed this all happens inside `CameraFeed.draw`, which now accepts an optional `distraction_manager` parameter. All entity drawing (raccoons and distractions) is wrapped in `screen.set_clip(r)` / `screen.set_clip(None)` to prevent bleed into adjacent tiles. Distractions are drawn before the CCTV tint so they receive the green colour shift.

In the yard (`YardState.draw`), entities are drawn to `self._yard_surf` in the same order. Convert normalised coordinates to yard-space with `yr.left + int(entity.cam_x * yr.width)` / `yr.top + int(entity.cam_y_frac * yr.height)` where `yr = zone.yard_rect`.
