import pygame
from src.states.base_state import BaseState
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COL_WHITE, RESULT_DISPLAY_SEC


class ResultState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.score = 0
        self.fled = False
        self.timeout = False
        self.zone_index = 0
        self.display_timer = 0.0
        self.font_big = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 34)
        self.font_small = pygame.font.SysFont("Arial", 22)
        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def on_enter(self, data):
        self.score = data.get("score", 0)
        self.fled = data.get("fled", False)
        self.timeout = data.get("timeout", False)
        self.zone_index = data.get("zone_index", 0)
        self.display_timer = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
        ):
            self._advance()

    def _advance(self):
        if self.game.timer_remaining <= 0:
            self.game.change_state("game_over")
        elif self.game.score >= self.game.level_config.score_target:
            self.game.change_state("level_complete")
        else:
            self.game.change_state("camera", exclude_zone=self.zone_index)

    def update(self, dt):
        self.display_timer += dt
        if self.display_timer >= RESULT_DISPLAY_SEC:
            self._advance()

    def draw(self, screen):
        self._overlay.fill((0, 0, 0, 150))
        screen.blit(self._overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        if self.fled:
            main_text = "RACCOON FLED!"
            main_color = (255, 160, 0)
            sub_text = "You took too long at the cameras..."
        elif self.timeout:
            main_text = "TOO SLOW!"
            main_color = (255, 80, 80)
            sub_text = "The raccoon escaped while you were aiming!"
        elif self.score > 0:
            main_text = f"+{self.score} POINTS!"
            main_color = (80, 255, 80)
            sub_text = "Great shot!  Raccoon photographed!"
        else:
            main_text = "MISSED!"
            main_color = (255, 80, 80)
            sub_text = "The raccoon is still out there..."

        surf = self.font_big.render(main_text, True, main_color)
        screen.blit(surf, surf.get_rect(center=(cx, cy - 50)))

        sub_surf = self.font_med.render(sub_text, True, COL_WHITE)
        screen.blit(sub_surf, sub_surf.get_rect(center=(cx, cy + 30)))

        hint = self.font_small.render("Click or press SPACE to continue", True, (140, 140, 140))
        screen.blit(hint, hint.get_rect(center=(cx, cy + 90)))
