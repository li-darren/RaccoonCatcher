"""Pure ADS viewport and lens-hit geometry — no pygame dependency."""
import math


def ads_viewport(mouse_x: float, mouse_y: float,
                 yard_left: int, yard_top: int, yard_w: int, yard_h: int,
                 screen_w: int, zoom: float,
                 lens_cx: float, lens_cy: float, lens_r: float) -> tuple:
    """Return (vp_x, vp_y, vp_w, vp_h) for the ADS viewport.

    Panning bounds are derived from lens geometry so the lens circle can
    reach every edge of the yard without showing content outside it.
    """
    vp_w = int(yard_w / zoom)
    vp_h = int(yard_h / zoom)
    yard_right = yard_left + yard_w
    yard_bottom = yard_top + yard_h
    vp_x_min = yard_left  - int((lens_cx - lens_r - yard_left) / zoom)
    vp_x_max = yard_right - int((lens_cx + lens_r - yard_left) / zoom)
    vp_y_min = yard_top   - int((lens_cy - lens_r - yard_top)  / zoom)
    vp_y_max = yard_bottom - int((lens_cy + lens_r - yard_top) / zoom)
    tx = max(0.0, min(mouse_x / max(screen_w - 1, 1), 1.0))
    ty = max(0.0, min((mouse_y - yard_top) / max(yard_h - 1, 1), 1.0))
    vp_x = vp_x_min + int(tx * (vp_x_max - vp_x_min))
    vp_y = vp_y_min + int(ty * (vp_y_max - vp_y_min))
    return vp_x, vp_y, vp_w, vp_h


def raccoon_in_lens(rx: float, ry: float, raccoon_radius: int,
                    vp_x: float, vp_y: float,
                    yard_left: int, yard_top: int,
                    zoom: float, lens_cx: float, lens_cy: float, lens_r: float) -> bool:
    """True when the raccoon circle is fully inside the ADS lens circle."""
    sx = yard_left + (rx - vp_x) * zoom
    sy = yard_top  + (ry - vp_y) * zoom
    dist = math.hypot(sx - lens_cx, sy - lens_cy)
    return dist + raccoon_radius * zoom <= lens_r
