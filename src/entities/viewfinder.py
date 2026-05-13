import pygame
from settings import HIT_ZONE_SIZE, COL_VIEWFINDER, COL_VIEWFINDER_HIT


class Viewfinder:
    def __init__(self):
        self.pos = (640, 360)
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

    def draw_cursor(self, screen):
        """Camera-body cursor drawn around the mouse position."""
        cx, cy = int(self.pos[0]), int(self.pos[1])
        col = COL_VIEWFINDER_HIT if self.is_hit else COL_VIEWFINDER

        # Camera body
        bw, bh = 58, 36
        pygame.draw.rect(screen, col, (cx - bw // 2, cy - bh // 2, bw, bh), 2)

        # Viewfinder bump (top-left of body)
        pygame.draw.rect(screen, col, (cx - bw // 2 + 6, cy - bh // 2 - 8, 14, 9), 2)

        # Shutter button (top-right of body)
        pygame.draw.circle(screen, col, (cx + bw // 2 - 10, cy - bh // 2 - 4), 4, 2)

        # Lens barrel — outer ring, inner ring, center dot
        pygame.draw.circle(screen, col, (cx, cy), 13, 2)
        pygame.draw.circle(screen, col, (cx, cy), 6, 1)
        pygame.draw.circle(screen, col, (cx, cy), 2)

        # Hit-zone corner brackets (target area indicator)
        half_h = self.hit_size // 2
        tick = 9
        for ox, oy, dx, dy in [
            (cx - half_h, cy - half_h,  1,  1),
            (cx + half_h, cy - half_h, -1,  1),
            (cx - half_h, cy + half_h,  1, -1),
            (cx + half_h, cy + half_h, -1, -1),
        ]:
            pygame.draw.line(screen, col, (ox, oy), (ox + dx * tick, oy), 1)
            pygame.draw.line(screen, col, (ox, oy), (ox, oy + dy * tick), 1)

    def draw_aiming_reticle(self, screen, lens_cx, lens_cy):
        """Precision crosshair drawn at the centre of the ADS lens circle."""
        col = COL_VIEWFINDER_HIT if self.is_hit else (210, 210, 210)
        gap, arm = 22, 55

        # Four-arm crosshair with a gap at the centre
        pygame.draw.line(screen, col, (lens_cx - gap - arm, lens_cy), (lens_cx - gap, lens_cy), 1)
        pygame.draw.line(screen, col, (lens_cx + gap, lens_cy), (lens_cx + gap + arm, lens_cy), 1)
        pygame.draw.line(screen, col, (lens_cx, lens_cy - gap - arm), (lens_cx, lens_cy - gap), 1)
        pygame.draw.line(screen, col, (lens_cx, lens_cy + gap), (lens_cx, lens_cy + gap + arm), 1)

        # Centre dot
        pygame.draw.circle(screen, col, (lens_cx, lens_cy), 3)

        # Corner brackets that visualise the hit zone
        b, off = 20, 28
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            bx, by = lens_cx + dx * off, lens_cy + dy * off
            pygame.draw.line(screen, col, (bx, by), (bx + dx * b, by), 2)
            pygame.draw.line(screen, col, (bx, by), (bx, by + dy * b), 2)
