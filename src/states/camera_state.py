import pygame
from src.states.base_state import BaseState
from src.ui.camera_feed import CameraFeed
from src.ui.hud import HUD
from settings import COL_BG


class CameraState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.feeds: list = []
        self.hud = HUD()
        self._hover_zone = -1

    def on_enter(self, data):
        self.feeds = [CameraFeed(z) for z in self.game.zone_manager.zones]
        self.game.raccoons_paused = False
        exclude = data.get("exclude_zone", -1)
        self.game.raccoon_manager.respawn_if_needed(exclude_zone=exclude)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, feed in enumerate(self.feeds):
                if feed.get_door_button_rect().collidepoint(event.pos):
                    # Only allow going to a zone where a raccoon is visible
                    if any(r.is_camera_visible for r in self.game.raccoon_manager.raccoons_in_zone(i)):
                        self.game.target_zone = i
                        self.game.change_state("transition", target_zone=i)
                        return

    def update(self, dt):
        self.game.timer_remaining -= dt
        self.game.camera_room_elapsed += dt
        self.game.raccoon_manager.update(dt)

        for feed in self.feeds:
            feed.update(dt)

        mouse_pos = pygame.mouse.get_pos()
        self._hover_zone = -1
        for i, feed in enumerate(self.feeds):
            if feed.get_door_button_rect().collidepoint(mouse_pos):
                self._hover_zone = i

        if self.game.timer_remaining <= 0:
            self.game.timer_remaining = 0
            self.game.change_state("game_over")
        elif self.game.score >= self.game.level_config.score_target:
            self.game.change_state("level_complete")

    def draw(self, screen):
        screen.fill(COL_BG)
        for i, feed in enumerate(self.feeds):
            raccoons = self.game.raccoon_manager.raccoons_in_zone(i)
            feed.draw(screen, raccoons, door_hover=(self._hover_zone == i))

        self.hud.draw_camera_hud(
            screen,
            self.game.score,
            self.game.timer_remaining,
            self.game.level,
            self.game.level_config.score_target,
        )
