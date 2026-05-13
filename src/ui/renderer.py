import math
import pygame


def draw_raccoon(surface, pos, radius: int, size_label: str = "medium",
                 facing_right: bool = True, camera_mode: bool = False):
    cx, cy = int(pos[0]), int(pos[1])

    # Striped tail (drawn behind body)
    tail_colors = [(90, 90, 90), (30, 30, 30)]
    seg_r = max(radius // 3, 2)
    tail_dir = -1 if facing_right else 1
    for i in range(5):
        tx = cx + tail_dir * (radius + 3 + i * (seg_r + 1))
        ty = cy + radius // 3 - i * 2
        pygame.draw.circle(surface, tail_colors[i % 2], (tx, ty), max(seg_r - i, 1))

    # Body
    pygame.draw.circle(surface, (90, 90, 90), (cx, cy), radius)

    # Mask stripe across eyes
    mask_w = int(radius * 1.6)
    mask_h = int(radius * 0.65)
    pygame.draw.ellipse(surface, (35, 35, 35),
                        (cx - mask_w // 2, cy - mask_h // 2, mask_w, mask_h))

    # Eyes — in camera mode the tapetum reflects the IR light as bright eye-shine
    er = max(radius // 4, 1)
    eo = radius // 3
    if camera_mode:
        for ex in [cx - eo, cx + eo]:
            pygame.draw.circle(surface, (180, 255, 180), (ex, cy - 2), er + 2)  # green glow halo
            pygame.draw.circle(surface, (220, 255, 220), (ex, cy - 2), er)      # bright reflection
    else:
        for ex in [cx - eo, cx + eo]:
            pygame.draw.circle(surface, (255, 255, 200), (ex, cy - 2), er)
            pygame.draw.circle(surface, (0, 0, 0), (ex, cy - 2), max(er - 2, 1))

    # Ears
    ear_r = max(radius // 3, 2)
    ear_ox = int(radius * 0.65)
    for ex in [cx - ear_ox, cx + ear_ox]:
        pygame.draw.circle(surface, (75, 75, 75), (ex, cy - radius + 3), ear_r)
        pygame.draw.circle(surface, (160, 100, 100), (ex, cy - radius + 4), max(ear_r - 4, 2))

    # Nose
    nr = max(radius // 6, 1)
    pygame.draw.ellipse(surface, (20, 20, 20),
                        (cx - nr, cy + nr - 1, nr * 2, nr + 2))


def draw_bird(surface, pos, radius: int, facing_right: bool = True,
              wing_phase: float = 0.0, camera_mode: bool = False):
    cx, cy = int(pos[0]), int(pos[1])
    col = (160, 200, 160) if camera_mode else (45, 42, 38)
    r = max(radius, 2)
    flap = int(math.sin(wing_phase) * r * 1.4)
    pygame.draw.circle(surface, col, (cx, cy), max(r // 2, 1))
    pygame.draw.line(surface, col, (cx, cy), (cx - r * 3, cy - flap), max(r // 3, 1))
    pygame.draw.line(surface, col, (cx, cy), (cx + r * 3, cy - flap), max(r // 3, 1))


def draw_leaf(surface, pos, radius: int, rotation: float = 0.0,
              color=(60, 120, 30), camera_mode: bool = False):
    cx, cy = int(pos[0]), int(pos[1])
    col = (80, 160, 80) if camera_mode else color
    r = max(radius, 1)
    if r <= 2:
        pygame.draw.circle(surface, col, (cx, cy), r)
        return
    angle = math.radians(rotation)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    points = []
    for t_deg in range(0, 360, 40):
        t = math.radians(t_deg)
        lx = r * 2.2 * math.cos(t)
        ly = r * math.sin(t)
        points.append((cx + int(lx * cos_a - ly * sin_a),
                        cy + int(lx * sin_a + ly * cos_a)))
    pygame.draw.polygon(surface, col, points)


def draw_trash_bag(surface, pos, radius: int, camera_mode: bool = False):
    cx, cy = int(pos[0]), int(pos[1])
    body_col = (40, 45, 40) if camera_mode else (25, 28, 22)
    knot_col = (60, 65, 58) if camera_mode else (42, 46, 38)
    r = max(radius, 5)
    pygame.draw.circle(surface, body_col, (cx, cy), r)
    pygame.draw.circle(surface, body_col, (cx + r // 3, cy - r // 4), r * 3 // 4)
    pygame.draw.circle(surface, knot_col, (cx + r // 4, cy - r), max(r // 5, 2))


def draw_yard_background(surface, zone_index: int, yard_rect: pygame.Rect):
    sky_h = yard_rect.height // 3
    sky_rect = pygame.Rect(yard_rect.left, yard_rect.top, yard_rect.width, sky_h)
    grass_rect = pygame.Rect(yard_rect.left, yard_rect.top + sky_h,
                             yard_rect.width, yard_rect.height - sky_h)

    pygame.draw.rect(surface, (5, 8, 28), sky_rect)
    pygame.draw.rect(surface, (10, 38, 10), grass_rect)
    pygame.draw.line(surface, (5, 22, 5),
                     (yard_rect.left, yard_rect.top + sky_h),
                     (yard_rect.right, yard_rect.top + sky_h), 4)

    # Night sky — moon with soft halo, then stars
    mx, my = yard_rect.right - 110, yard_rect.top + 45
    pygame.draw.circle(surface, (60, 60, 40), (mx, my), 38)   # dim glow ring
    pygame.draw.circle(surface, (200, 200, 140), (mx, my), 28)  # moon body
    for sx, sy in [(180, 25), (310, 12), (380, 48), (510, 30), (650, 18),
                   (780, 40), (880, 22), (1000, 38), (1100, 14)]:
        if yard_rect.left <= sx <= yard_rect.right:
            pygame.draw.circle(surface, (220, 220, 255), (sx, yard_rect.top + sy), 2)

    # Zone-specific props
    if zone_index == 0:
        _draw_fence(surface, yard_rect, grass_rect)
    elif zone_index == 1:
        _draw_shed(surface, yard_rect, grass_rect)
    elif zone_index == 2:
        _draw_gate(surface, yard_rect, grass_rect)
    else:
        _draw_garden(surface, yard_rect, grass_rect)


def _draw_fence(surface, yard_rect, grass_rect):
    fy = grass_rect.top + 18
    fc = (139, 90, 43)
    pygame.draw.line(surface, fc, (yard_rect.left + 40, fy + 28), (yard_rect.right - 40, fy + 28), 7)
    pygame.draw.line(surface, fc, (yard_rect.left + 40, fy + 68), (yard_rect.right - 40, fy + 68), 7)
    for x in range(yard_rect.left + 50, yard_rect.right - 30, 50):
        pygame.draw.rect(surface, fc, (x, fy, 13, 90))
        pygame.draw.polygon(surface, fc, [(x, fy), (x + 6, fy - 13), (x + 13, fy)])


def _draw_shed(surface, yard_rect, grass_rect):
    sx = yard_rect.right - 270
    sy = grass_rect.top - 25
    pygame.draw.rect(surface, (115, 75, 35), (sx, sy + 38, 200, 125))
    pygame.draw.polygon(surface, (75, 35, 15),
                        [(sx - 22, sy + 38), (sx + 100, sy - 22), (sx + 222, sy + 38)])
    pygame.draw.rect(surface, (55, 28, 8), (sx + 72, sy + 78, 52, 85))
    pygame.draw.circle(surface, (200, 170, 0), (sx + 113, sy + 118), 5)
    pygame.draw.rect(surface, (140, 200, 220), (sx + 138, sy + 55, 36, 36))
    pygame.draw.line(surface, (80, 80, 80), (sx + 138, sy + 73), (sx + 174, sy + 73), 2)
    pygame.draw.line(surface, (80, 80, 80), (sx + 156, sy + 55), (sx + 156, sy + 91), 2)


def _draw_gate(surface, yard_rect, grass_rect):
    gx = yard_rect.width // 2 - 75
    gy = grass_rect.top - 18
    pc = (100, 65, 25)
    gc = (148, 98, 45)
    pygame.draw.rect(surface, pc, (gx, gy, 20, 130))
    pygame.draw.rect(surface, pc, (gx + 130, gy, 20, 130))
    for i in range(5):
        pygame.draw.rect(surface, gc, (gx + 20 + i * 24, gy + 8, 13, 104))
    pygame.draw.rect(surface, gc, (gx + 20, gy + 18, 110, 11))
    pygame.draw.rect(surface, gc, (gx + 20, gy + 68, 110, 11))
    for x in range(yard_rect.left + 15, gx, 42):
        pygame.draw.rect(surface, (118, 78, 28), (x, gy + 8, 11, 92))
    for x in range(gx + 150, yard_rect.right - 15, 42):
        pygame.draw.rect(surface, (118, 78, 28), (x, gy + 8, 11, 92))
    pygame.draw.line(surface, (118, 78, 28),
                     (yard_rect.left + 15, gy + 28), (gx, gy + 28), 6)
    pygame.draw.line(surface, (118, 78, 28),
                     (gx + 150, gy + 28), (yard_rect.right - 15, gy + 28), 6)


def _draw_garden(surface, yard_rect, grass_rect):
    flower_colors = [(220, 90, 90), (255, 210, 0), (200, 90, 210), (90, 200, 255)]
    spots = [(160, 55), (380, 35), (680, 65), (960, 45)]
    for i, (bx, by) in enumerate(spots):
        gy = grass_rect.top + by
        pygame.draw.ellipse(surface, (18, 88, 18), (bx - 42, gy - 8, 84, 28))
        for fx, fy in [(bx - 22, gy - 14), (bx, gy - 20), (bx + 22, gy - 14)]:
            pygame.draw.circle(surface, flower_colors[i % len(flower_colors)], (fx, fy), 11)
            pygame.draw.circle(surface, (255, 230, 0), (fx, fy), 4)
            pygame.draw.line(surface, (18, 118, 18), (fx, fy + 9), (fx, gy + 6), 2)
    # Small potting bench
    bx2 = yard_rect.right - 210
    by2 = grass_rect.top - 8
    pygame.draw.rect(surface, (95, 65, 25), (bx2, by2, 165, 88))
    pygame.draw.polygon(surface, (65, 38, 10),
                        [(bx2 - 22, by2), (bx2 + 82, by2 - 48), (bx2 + 187, by2)])
