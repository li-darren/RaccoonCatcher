# src/ui

This directory contains the UI layer: `renderer.py` (shared drawing functions), `camera_feed.py` (per-zone camera display), and `hud.py` (heads-up display).

## Graphics

All graphics are drawn with `pygame.draw` primitives — there are no image assets. `src/ui/renderer.py` contains the two shared drawing functions (`draw_raccoon`, `draw_yard_background`) used by both the camera feeds and the yard view. Semi-transparent overlays (CCTV tint, shutter flash) use `pygame.SRCALPHA` surfaces created once and reused — never recreate them per frame.

## Night-time visual theme

The game is set at night. Key colour values:
- `COL_BG` (letterbox/fill): `(5, 8, 18)` — dark navy
- Sky in `draw_yard_background`: `(5, 8, 28)`
- Grass in `draw_yard_background`: `(10, 38, 10)`
- The moon is drawn with a dim halo ring behind it; nine stars are scattered across the sky strip.

`draw_raccoon` accepts a `camera_mode: bool = False` parameter. When `True` (used by `CameraFeed`), the eyes skip the dark pupil and instead render a bright green glow halo + white reflection to simulate tapetum eye-shine under IR/CCTV light. The yard view passes `camera_mode=False` (default) and keeps normal eyes.

## Camera ↔ yard visual consistency

- The camera feed background is a pre-rendered, scaled-down copy of the full yard background (`draw_yard_background` drawn onto a 1280×660 buffer, then `pygame.transform.scale`'d to the tile size). This is cached per zone in `CameraFeed._bg_cache`.
- The raccoon scale in the camera feed uses `min(r.width/1280, r.height/660)` — the same ratio used to scale the background — so raccoon size is proportionally identical in both views.
- Raccoons are drawn at `r.height * 0.65` in the camera, which maps exactly to `yard_rect.top + yard_rect.height * 0.65` (~489 px) in the yard. `set_yard_position_from_camera` uses this mapping so the raccoon appears at the same relative position after transition.
- `set_yard_position` (random placement) also restricts y to `yard_rect.top + yard_rect.height * 0.62` or lower, keeping raccoons in the foreground grass below all zone props (fences, shed, gate, garden tops all end above the 60% mark).
