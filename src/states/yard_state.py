import random
import pygame
from src.states.base_state import BaseState
from src.entities.viewfinder import Viewfinder
from src.ui.hud import HUD
from src.ui.renderer import draw_yard_background, draw_raccoon
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HUD_BAR_H, COL_BG,
    YARD_PHOTO_TIME_SEC, SHUTTER_FLASH_MS, TRANSITION_DURATION_MS,
    ADS_ZOOM,
)

_FLED_DISPLAY_SEC = 2.0

# Lens geometry — circular vignette for ADS mode
_LENS_CX = SCREEN_WIDTH // 2
_LENS_CY = HUD_BAR_H + (SCREEN_HEIGHT - HUD_BAR_H) // 2
_LENS_R = min(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - HUD_BAR_H) // 2) - 25


class YardState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.zone_index = 0
        self.raccoons: list = []
        self.viewfinder = Viewfinder()
        self.hud = HUD()
        self.time_remaining = YARD_PHOTO_TIME_SEC
        self.raccoon_fled = False
        self.photo_taken = False
        self.result_score = 0
        self.shutter_elapsed = 0.0
        self.shutter_active = False
        self.fled_timer = 0.0
        self._shutter_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._pending_result = None
        self._yard_rect = None
        self._erratic_timers: list = []
        self._yard_vy: list = []
        self._vy_timers: list = []

        # ADS (camera-to-face) state
        self._aiming = False
        self._yard_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Pre-bake the circular vignette overlay used in ADS mode
        self._ads_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._ads_overlay.fill((0, 0, 0, 225))
        pygame.draw.circle(self._ads_overlay, (0, 0, 0, 0), (_LENS_CX, _LENS_CY), _LENS_R)

    def on_enter(self, data):
        self.zone_index = data.get("target_zone", 0)
        self.time_remaining = YARD_PHOTO_TIME_SEC
        self.raccoon_fled = False
        self.photo_taken = False
        self.result_score = 0
        self.shutter_active = False
        self.shutter_elapsed = 0.0
        self.fled_timer = 0.0
        self._pending_result = None
        self._aiming = False

        pygame.mouse.set_visible(False)

        zone = self.game.zone_manager.get_zone(self.zone_index)
        self._yard_rect = zone.yard_rect

        all_in_zone = self.game.raccoon_manager.raccoons_in_zone(self.zone_index)
        present = []
        for raccoon in all_in_zone:
            flee_p = raccoon.flee_probability(self.game.camera_room_elapsed)
            if random.random() >= flee_p:
                raccoon.set_yard_position_from_camera(
                    zone.yard_rect, TRANSITION_DURATION_MS / 1000.0)
                present.append(raccoon)

        self.raccoons = present
        self.raccoon_fled = bool(all_in_zone) and not present
        self._erratic_timers = [random.uniform(0.2, 0.8) for _ in present]
        self._yard_vy = [random.choice([-1, 1]) * random.uniform(15, 45) for _ in present]
        self._vy_timers = [random.uniform(0.3, 1.0) for _ in present]

        self.game.camera_room_elapsed = 0.0

    def on_exit(self):
        pygame.mouse.set_visible(True)
        self._aiming = False

    def handle_event(self, event):
        if self.photo_taken or self.raccoon_fled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self._aiming:
                self._take_photo()
            elif event.button == 3:
                self._aiming = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                self._aiming = False

    # ------------------------------------------------------------------
    # Photo capture helpers
    # ------------------------------------------------------------------

    def _ads_viewport(self) -> pygame.Rect:
        """Compute the ADS viewport rect using a linear mouse-to-yard mapping.

        Panning bounds are derived from the lens geometry so that at the
        extreme mouse positions the lens edge aligns exactly with the yard
        edge — the lens can reach every part of the yard but never shows
        content outside it.  The viewport may extend slightly beyond the
        _yard_surf surface; _get_vp_surf handles that safely.
        """
        mx, my = pygame.mouse.get_pos()
        yr = self._yard_rect
        vp_w = int(yr.width / ADS_ZOOM)
        vp_h = int(yr.height / ADS_ZOOM)
        # Lens edge in yard-space coords:
        #   lens_left_yard  = (_LENS_CX - _LENS_R) / ADS_ZOOM  = 134
        #   lens_right_yard = (_LENS_CX + _LENS_R) / ADS_ZOOM  = 378
        #   lens_top_yard   = (_LENS_CY - _LENS_R - yr.top) / ADS_ZOOM = 10
        #   lens_bot_yard   = (_LENS_CY + _LENS_R - yr.top) / ADS_ZOOM = 254
        vp_x_min = yr.left  - int((_LENS_CX - _LENS_R - yr.left) / ADS_ZOOM)
        vp_x_max = yr.right - int((_LENS_CX + _LENS_R - yr.left) / ADS_ZOOM)
        vp_y_min = yr.top   - int((_LENS_CY - _LENS_R - yr.top)  / ADS_ZOOM)
        vp_y_max = yr.bottom - int((_LENS_CY + _LENS_R - yr.top) / ADS_ZOOM)
        tx = max(0.0, min(mx / max(SCREEN_WIDTH - 1, 1), 1.0))
        ty = max(0.0, min((my - yr.top) / max(yr.height - 1, 1), 1.0))
        vp_x = vp_x_min + int(tx * (vp_x_max - vp_x_min))
        vp_y = vp_y_min + int(ty * (vp_y_max - vp_y_min))
        return pygame.Rect(vp_x, vp_y, vp_w, vp_h)

    def _get_vp_surf(self, vp_rect: pygame.Rect) -> pygame.Surface:
        """Extract the ADS viewport, filling any out-of-bounds area with COL_BG.

        Out-of-bounds pixels are always in the dark overlay region (outside the
        lens circle), so the player never sees them.
        """
        surf = pygame.Surface((vp_rect.w, vp_rect.h))
        surf.fill(COL_BG)
        src_rect = vp_rect.clip(self._yard_surf.get_rect())
        if src_rect.w > 0 and src_rect.h > 0:
            surf.blit(self._yard_surf, (src_rect.x - vp_rect.x, src_rect.y - vp_rect.y), src_rect)
        return surf

    def _capture_photo(self):
        """Return a Surface cropped to the ADS viewport around the cursor."""
        yr = self._yard_rect
        vp_rect = self._ads_viewport()
        vp_w, vp_h = vp_rect.w, vp_rect.h

        region = self._get_vp_surf(vp_rect)

        # Scale to photo display size (preserve original aspect ratio)
        photo_w, photo_h = 420, int(420 * vp_h / vp_w)
        photo = pygame.Surface((photo_w, photo_h))
        pygame.transform.scale(region, (photo_w, photo_h), photo)

        # Night-vision green tint
        tint = pygame.Surface((photo_w, photo_h), pygame.SRCALPHA)
        tint.fill((0, 30, 0, 45))
        photo.blit(tint, (0, 0))

        # Timestamp overlay (bottom-right corner)
        ts_font = pygame.font.SysFont("Courier", 12)
        ts_surf = ts_font.render(
            "03:47:12  CAM-{:02d}".format(self.zone_index + 1), True, (160, 255, 160))
        bg_w, bg_h = ts_surf.get_width() + 6, ts_surf.get_height() + 4
        ts_bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        ts_bg.fill((0, 0, 0, 160))
        photo.blit(ts_bg, (photo_w - bg_w - 3, photo_h - bg_h - 3))
        photo.blit(ts_surf, (photo_w - ts_surf.get_width() - 6, photo_h - ts_surf.get_height() - 5))

        return photo

    def _raccoon_in_lens(self, raccoon) -> bool:
        """True if the raccoon circle is fully inside the ADS lens circle."""
        yr = self._yard_rect
        vp_rect = self._ads_viewport()
        rx, ry = raccoon.yard_pos
        sx = yr.left + (rx - vp_rect.x) * ADS_ZOOM
        sy = yr.top + (ry - vp_rect.y) * ADS_ZOOM
        dist = ((sx - _LENS_CX) ** 2 + (sy - _LENS_CY) ** 2) ** 0.5
        return dist + raccoon.radius * ADS_ZOOM <= _LENS_R

    def _take_photo(self):
        photo = self._capture_photo()

        self.photo_taken = True
        self.shutter_active = True
        self.shutter_elapsed = 0.0

        caught = [r for r in self.raccoons if self._raccoon_in_lens(r)]
        self.result_score = sum(r.points for r in caught)
        self.game.score += self.result_score
        for r in caught:
            self.game.raccoon_manager.remove(r)
        self._pending_result = dict(
            score=self.result_score, fled=False,
            timeout=False, zone_index=self.zone_index,
            photo=photo,
        )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt):
        if self.raccoon_fled:
            self.fled_timer += dt
            if self.fled_timer >= _FLED_DISPLAY_SEC:
                self.game.change_state("result", score=0, fled=True,
                                       timeout=False, zone_index=self.zone_index)
            return

        if self.shutter_active:
            self.shutter_elapsed += dt * 1000
            if self.shutter_elapsed >= SHUTTER_FLASH_MS and self._pending_result is not None:
                self.shutter_active = False
                self.game.change_state("result", **self._pending_result)
            return

        if self.photo_taken:
            return

        self.time_remaining -= dt

        yr = self._yard_rect
        foreground_top = yr.top + int(yr.height * 0.62)
        foreground_bot = yr.bottom - 40

        for i, r in enumerate(self.raccoons):
            self._erratic_timers[i] -= dt
            if self._erratic_timers[i] <= 0:
                if random.random() < 0.75:
                    r.yard_vx = random.choice([-1, 1]) * random.uniform(60, 160)
                    r.facing_right = r.yard_vx >= 0
                self._erratic_timers[i] = random.uniform(0.2, 0.7)

            self._vy_timers[i] -= dt
            if self._vy_timers[i] <= 0:
                self._yard_vy[i] = random.choice([-1, 1]) * random.uniform(15, 50)
                self._vy_timers[i] = random.uniform(0.3, 0.9)

            r.yard_pos[0] += r.yard_vx * dt
            r.yard_pos[1] = max(foreground_top,
                                min(r.yard_pos[1] + self._yard_vy[i] * dt, foreground_bot))

        self.viewfinder.update([r.yard_pos for r in self.raccoons] or None)
        if self._aiming:
            # In ADS mode, reticle turns green only when a raccoon is fully inside the lens
            self.viewfinder.is_hit = bool(self.raccoons) and any(
                self._raccoon_in_lens(r) for r in self.raccoons
            )

        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game.change_state("result", score=0, fled=False,
                                   timeout=True, zone_index=self.zone_index)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, screen):
        zone = self.game.zone_manager.get_zone(self.zone_index)

        # Render the yard scene into _yard_surf so it can be zoomed / captured
        self._yard_surf.fill(COL_BG)
        draw_yard_background(self._yard_surf, self.zone_index, zone.yard_rect)
        if not self.photo_taken:
            for r in self.raccoons:
                draw_raccoon(self._yard_surf, r.yard_pos, r.radius, r.size, r.facing_right)

        if self._aiming and not self.photo_taken and not self.raccoon_fled:
            self._draw_ads(screen)
        else:
            screen.blit(self._yard_surf, (0, 0))
            if self.raccoon_fled:
                self._draw_fled_message(screen)
            elif not self.photo_taken:
                self.viewfinder.draw_cursor(screen)

        self.hud.draw_yard_hud(screen, max(self.time_remaining, 0.0), zone.name)

        if self.shutter_active:
            alpha = int(200 * max(1.0 - self.shutter_elapsed / SHUTTER_FLASH_MS, 0.0))
            self._shutter_surf.fill((255, 255, 255, alpha))
            screen.blit(self._shutter_surf, (0, 0))

    def _draw_ads(self, screen):
        """Render a zoomed, circular-lens view centred on the mouse position."""
        yr = self._yard_rect
        vp_rect = self._ads_viewport()

        zoomed = pygame.transform.scale(self._get_vp_surf(vp_rect), (yr.width, yr.height))
        screen.blit(zoomed, (yr.left, yr.top))

        # Circular vignette — dark outside lens, clear inside
        screen.blit(self._ads_overlay, (0, 0))

        # Lens chrome ring
        pygame.draw.circle(screen, (160, 160, 160), (_LENS_CX, _LENS_CY), _LENS_R, 3)
        pygame.draw.circle(screen, (220, 220, 220), (_LENS_CX, _LENS_CY), _LENS_R - 5, 1)

        # ADS zoom label
        font = pygame.font.SysFont("Courier", 14)
        label = font.render(f"{ADS_ZOOM:.1f}×", True, (180, 220, 180))
        screen.blit(label, (_LENS_CX + _LENS_R - label.get_width() - 12,
                             _LENS_CY - _LENS_R + 10))

        # Precision reticle at lens centre
        self.viewfinder.draw_aiming_reticle(screen, _LENS_CX, _LENS_CY)

    def _draw_fled_message(self, screen):
        font = pygame.font.SysFont("Arial", 52, bold=True)
        surf = font.render("The raccoon ran away!", True, (255, 200, 0))
        cx, cy = screen.get_width() // 2, screen.get_height() // 2
        screen.blit(surf, surf.get_rect(center=(cx, cy - 20)))

        font2 = pygame.font.SysFont("Arial", 28)
        sub = font2.render("You spent too long at the cameras...", True, (200, 200, 200))
        screen.blit(sub, sub.get_rect(center=(cx, cy + 45)))
