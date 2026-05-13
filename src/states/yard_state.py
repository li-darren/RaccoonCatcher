import random
import pygame
from src.states.base_state import BaseState
from src.entities.viewfinder import Viewfinder
from src.ui.hud import HUD
from src.ui.renderer import draw_yard_background, draw_raccoon
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, YARD_PHOTO_TIME_SEC, SHUTTER_FLASH_MS

_FLED_DISPLAY_SEC = 2.0


class YardState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.zone_index = 0
        self.raccoon = None
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

        raccoon = self.game.raccoon_manager.get_raccoon_in_zone(self.zone_index)
        if raccoon:
            flee_p = raccoon.flee_probability(self.game.camera_room_elapsed)
            if random.random() < flee_p:
                self.raccoon = None
                self.raccoon_fled = True
            else:
                self.raccoon = raccoon
                zone = self.game.zone_manager.get_zone(self.zone_index)
                self.raccoon.set_yard_position(zone.yard_rect)
        else:
            self.raccoon = None
            self.raccoon_fled = False

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

        if self.raccoon and self.viewfinder.hit_test(self.raccoon.yard_pos):
            self.result_score = self.raccoon.points
            self.game.score += self.result_score
            self.game.raccoon_manager.remove(self.raccoon)
            self._pending_result = dict(score=self.result_score, fled=False,
                                        timeout=False, zone_index=self.zone_index)
        else:
            self.result_score = 0
            self._pending_result = dict(score=0, fled=False,
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
        raccoon_pos = self.raccoon.yard_pos if self.raccoon else None
        self.viewfinder.update(raccoon_pos)

        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game.change_state("result", score=0, fled=False,
                                   timeout=True, zone_index=self.zone_index)

    def draw(self, screen):
        zone = self.game.zone_manager.get_zone(self.zone_index)
        draw_yard_background(screen, self.zone_index, zone.yard_rect)

        if self.raccoon and not self.photo_taken:
            draw_raccoon(screen, self.raccoon.yard_pos, self.raccoon.radius, self.raccoon.size)

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
