import pygame
from settings import VIEWFINDER_SIZE, HIT_ZONE_SIZE, COL_VIEWFINDER, COL_VIEWFINDER_HIT


class Viewfinder:
    def __init__(self):
        self.pos = (640, 360)
        self.outer_size = VIEWFINDER_SIZE
        self.hit_size = HIT_ZONE_SIZE
        self.is_hit = False

    def update(self, raccoon_positions=None):
        self.pos = pygame.mouse.get_pos()
        self.is_hit = bool(
            raccoon_positions and any(self.hit_test(p) for p in raccoon_positions)
        )

    def hit_test(self, raccoon_pos) -> bool:
        rx, ry = raccoon_pos
        cx, cy = self.pos
        half = self.hit_size // 2
        return abs(rx - cx) <= half and abs(ry - cy) <= half

    def draw(self, screen):
        cx, cy = self.pos
        color = COL_VIEWFINDER_HIT if self.is_hit else COL_VIEWFINDER
        half_o = self.outer_size // 2
        half_h = self.hit_size // 2
        tick = 14

        # L-shaped corner ticks (outer frame)
        corners = [
            (cx - half_o, cy - half_o, 1, 1),
            (cx + half_o, cy - half_o, -1, 1),
            (cx - half_o, cy + half_o, 1, -1),
            (cx + half_o, cy + half_o, -1, -1),
        ]
        for ox, oy, dx, dy in corners:
            pygame.draw.line(screen, color, (ox, oy), (ox + dx * tick, oy), 2)
            pygame.draw.line(screen, color, (ox, oy), (ox, oy + dy * tick), 2)

        # Inner hit-zone rectangle
        inner_rect = pygame.Rect(cx - half_h, cy - half_h, self.hit_size, self.hit_size)
        pygame.draw.rect(screen, color, inner_rect, 1)

        # Crosshair
        llen = 10
        pygame.draw.line(screen, color, (cx - llen, cy), (cx + llen, cy), 1)
        pygame.draw.line(screen, color, (cx, cy - llen), (cx, cy + llen), 1)
        pygame.draw.circle(screen, color, (cx, cy), 2)
