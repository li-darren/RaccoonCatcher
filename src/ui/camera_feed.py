import pygame
from settings import COL_CCTV_BORDER

_FULL_W = 1280
_FULL_H = 660  # SCREEN_HEIGHT - HUD_BAR_H


class CameraFeed:
    _bg_cache: dict = {}

    def __init__(self, zone):
        self.zone = zone
        self.rect: pygame.Rect = zone.camera_rect
        self.scan_y: float = 0.0
        self._cctv_overlay = None

    def _overlay(self) -> pygame.Surface:
        if self._cctv_overlay is None:
            surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            surf.fill((0, 50, 0, 120))
            self._cctv_overlay = surf
        return self._cctv_overlay

    def _get_bg(self, r: pygame.Rect) -> pygame.Surface:
        key = (self.zone.index, r.width, r.height)
        if key not in CameraFeed._bg_cache:
            from src.ui.renderer import draw_yard_background
            full = pygame.Surface((_FULL_W, _FULL_H))
            draw_yard_background(full, self.zone.index,
                                 pygame.Rect(0, 0, _FULL_W, _FULL_H))
            CameraFeed._bg_cache[key] = pygame.transform.scale(full, (r.width, r.height))
        return CameraFeed._bg_cache[key]

    def update(self, dt: float):
        self.scan_y = (self.scan_y + 75 * dt) % self.rect.height

    def draw(self, screen, raccoons_in_zone: list, door_hover: bool = False):
        r = self.rect

        # 1. Yard background scaled to camera tile size
        screen.blit(self._get_bg(r), r.topleft)

        # 3. Raccoon(s) — draw all raccoons in zone, scaled to fit tile
        if raccoons_in_zone:
            from src.ui.renderer import draw_raccoon
            scale = min(r.width / 1280, r.height / 660)
            ry = r.top + int(r.height * 0.65)
            screen.set_clip(r)
            for raccoon in raccoons_in_zone:
                rx = r.left + int(raccoon.cam_x * r.width)
                scaled_r = max(int(raccoon.radius * scale), 3)
                draw_raccoon(screen, (rx, ry), scaled_r, raccoon.size, raccoon.facing_right,
                             camera_mode=True)
            screen.set_clip(None)

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

    def _draw_door_button(self, screen, raccoon_count: int, hover: bool):
        r = self.rect
        btn_w, btn_h = 168, 28
        btn_x = r.right - btn_w - 6
        btn_y = r.bottom - btn_h - 6
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        has_raccoon = raccoon_count > 0
        if has_raccoon:
            bg = (0, 170, 0) if hover else (0, 110, 0)
            border = (0, 255, 100)
            text = "Open door to yard"
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
        btn_w, btn_h = 168, 28
        return pygame.Rect(r.right - btn_w - 6, r.bottom - btn_h - 6, btn_w, btn_h)
