import pygame
from settings import COL_CCTV_BORDER


class CameraFeed:
    def __init__(self, zone):
        self.zone = zone
        self.rect: pygame.Rect = zone.camera_rect
        self.scan_y: float = 0.0
        self._green_overlay = None

    def _overlay(self) -> pygame.Surface:
        if self._green_overlay is None:
            surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            surf.fill((0, 55, 0, 55))
            self._green_overlay = surf
        return self._green_overlay

    def update(self, dt: float):
        self.scan_y = (self.scan_y + 75 * dt) % self.rect.height

    def draw(self, screen, raccoons_in_zone: list, door_hover: bool = False):
        r = self.rect

        # 1. Sky + grass background
        sky_h = r.height // 3
        pygame.draw.rect(screen, (20, 40, 65), pygame.Rect(r.left, r.top, r.width, sky_h))
        pygame.draw.rect(screen, (18, 65, 18),
                         pygame.Rect(r.left, r.top + sky_h, r.width, r.height - sky_h))
        pygame.draw.line(screen, (10, 45, 10),
                         (r.left, r.top + sky_h), (r.right, r.top + sky_h), 2)

        # 2. Simple zone prop hint
        self._draw_zone_hint(screen, r)

        # 3. Raccoon(s) — show at most one, scaled to fit tile
        if raccoons_in_zone:
            raccoon = raccoons_in_zone[0]
            from src.ui.renderer import draw_raccoon
            rx = r.left + r.width // 2
            ry = r.top + int(r.height * 0.65)
            scale = min(r.width / 1280, r.height / 660) * 2.8
            scaled_r = max(int(raccoon.radius * scale), 5)
            draw_raccoon(screen, (rx, ry), scaled_r, raccoon.size)

        # 4. Green CCTV tint overlay
        screen.blit(self._overlay(), r.topleft)

        # 5. Animated scan line
        scan_surf = pygame.Surface((r.width, 5), pygame.SRCALPHA)
        scan_surf.fill((140, 255, 140, 50))
        screen.blit(scan_surf, (r.left, r.top + int(self.scan_y)))

        # 6. Border
        border_color = (0, 255, 80) if door_hover else COL_CCTV_BORDER
        pygame.draw.rect(screen, border_color, r, 3)

        # 7. Zone label
        font = pygame.font.SysFont("Courier", 13, bold=True)
        label = font.render(f"CAM {self.zone.index + 1}  {self.zone.name.upper()}", True, (0, 220, 0))
        screen.blit(label, (r.left + 6, r.top + 5))

        # 8. Raccoon count badge + door button
        self._draw_door_button(screen, len(raccoons_in_zone), door_hover)

    def _draw_zone_hint(self, screen, r: pygame.Rect):
        # A tiny colored rectangle to distinguish zones
        zone_colors = [(80, 50, 20), (60, 60, 60), (100, 80, 30), (50, 30, 10)]
        c = zone_colors[self.zone.index % len(zone_colors)]
        hint_rect = pygame.Rect(r.right - 28, r.top + r.height // 3 - 10, 18, 45)
        pygame.draw.rect(screen, c, hint_rect)

    def _draw_door_button(self, screen, raccoon_count: int, hover: bool):
        r = self.rect
        btn_w, btn_h = 145, 28
        btn_x = r.right - btn_w - 6
        btn_y = r.bottom - btn_h - 6
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        has_raccoon = raccoon_count > 0
        if has_raccoon:
            bg = (0, 170, 0) if hover else (0, 110, 0)
            border = (0, 255, 100)
            text = "GO HERE!"
            text_color = (255, 255, 255)
        else:
            bg = (35, 35, 35)
            border = (70, 70, 70)
            text = "CLEAR"
            text_color = (90, 90, 90)

        pygame.draw.rect(screen, bg, btn_rect, border_radius=5)
        pygame.draw.rect(screen, border, btn_rect, 2, border_radius=5)
        font = pygame.font.SysFont("Arial", 13, bold=True)
        t_surf = font.render(text, True, text_color)
        screen.blit(t_surf, t_surf.get_rect(center=btn_rect.center))

        if has_raccoon:
            badge_font = pygame.font.SysFont("Arial", 11, bold=True)
            badge = badge_font.render(f"{raccoon_count} raccoon(s) spotted!", True, (255, 220, 0))
            screen.blit(badge, (btn_x, btn_y - 17))

    def get_door_button_rect(self) -> pygame.Rect:
        r = self.rect
        btn_w, btn_h = 145, 28
        return pygame.Rect(r.right - btn_w - 6, r.bottom - btn_h - 6, btn_w, btn_h)
