"""Pure zone-layout geometry — no pygame dependency."""


def camera_grid_rects(pad: int, feed_w: int, feed_h: int,
                      hud_h: int) -> list:
    """Return (x, y, w, h) tuples for each camera tile in row-major order."""
    rects = []
    for row in range(2):
        for col in range(2):
            x = pad + col * (feed_w + pad)
            y = hud_h + pad + row * (feed_h + pad)
            rects.append((x, y, feed_w, feed_h))
    return rects


def yard_rect_bounds(screen_w: int, screen_h: int, hud_h: int) -> tuple:
    """Return (left, top, width, height) for the shared yard rect."""
    return (0, hud_h, screen_w, screen_h - hud_h)
