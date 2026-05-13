import random
import pygame
from src.states.base_state import BaseState
from src.entities.viewfinder import Viewfinder
from src.ui.hud import HUD
from src.ui.renderer import draw_yard_background, draw_raccoon
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, YARD_PHOTO_TIME_SEC, SHUTTER_FLASH_MS, TRANSITION_DURATION_MS

_FLED_DISPLAY_SEC = 2.0


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
        self._erratic_timers: list = []   # seconds until next direction/speed change per raccoon
        self._yard_vy: list = []          # vertical drift per raccoon (px/sec)
        self._vy_timers: list = []        # seconds until next y-direction change per raccoon

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

    def handle_event(self, event):
        if self.photo_taken or self.raccoon_fled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._take_photo()

    def _take_photo(self):
        self.photo_taken = True
        self.shutter_active = True
        self.shutter_elapsed = 0.0

        caught = [r for r in self.raccoons if self.viewfinder.hit_test(r.yard_pos)]
        self.result_score = sum(r.points for r in caught)
        self.game.score += self.result_score
        for r in caught:
            self.game.raccoon_manager.remove(r)
        self._pending_result = dict(score=self.result_score, fled=False,
                                    timeout=False, zone_index=self.zone_index)

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
            # Erratic x direction/speed changes
            self._erratic_timers[i] -= dt
            if self._erratic_timers[i] <= 0:
                if random.random() < 0.75:
                    r.yard_vx = random.choice([-1, 1]) * random.uniform(60, 160)
                    r.facing_right = r.yard_vx >= 0
                self._erratic_timers[i] = random.uniform(0.2, 0.7)

            # Erratic y drift
            self._vy_timers[i] -= dt
            if self._vy_timers[i] <= 0:
                self._yard_vy[i] = random.choice([-1, 1]) * random.uniform(15, 50)
                self._vy_timers[i] = random.uniform(0.3, 0.9)

            r.yard_pos[0] += r.yard_vx * dt
            r.yard_pos[1] = max(foreground_top,
                                min(r.yard_pos[1] + self._yard_vy[i] * dt, foreground_bot))

        self.viewfinder.update([r.yard_pos for r in self.raccoons] or None)

        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game.change_state("result", score=0, fled=False,
                                   timeout=True, zone_index=self.zone_index)

    def draw(self, screen):
        zone = self.game.zone_manager.get_zone(self.zone_index)
        draw_yard_background(screen, self.zone_index, zone.yard_rect)

        if not self.photo_taken:
            for r in self.raccoons:
                draw_raccoon(screen, r.yard_pos, r.radius, r.size, r.facing_right)

        if self.raccoon_fled:
            self._draw_fled_message(screen)
        elif not self.photo_taken:
            self.viewfinder.draw(screen)

        self.hud.draw_yard_hud(screen, max(self.time_remaining, 0.0), zone.name)

        if self.shutter_active:
            alpha = int(200 * max(1.0 - self.shutter_elapsed / SHUTTER_FLASH_MS, 0.0))
            self._shutter_surf.fill((255, 255, 255, alpha))
            screen.blit(self._shutter_surf, (0, 0))

    def _draw_fled_message(self, screen):
        font = pygame.font.SysFont("Arial", 52, bold=True)
        surf = font.render("The raccoon ran away!", True, (255, 200, 0))
        cx, cy = screen.get_width() // 2, screen.get_height() // 2
        screen.blit(surf, surf.get_rect(center=(cx, cy - 20)))

        font2 = pygame.font.SysFont("Arial", 28)
        sub = font2.render("You spent too long at the cameras...", True, (200, 200, 200))
        screen.blit(sub, sub.get_rect(center=(cx, cy + 45)))
