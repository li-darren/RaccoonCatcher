import pygame
from src.states.base_state import BaseState
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TRANSITION_DURATION_MS


class TransitionState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.elapsed_ms = 0.0
        self.target_zone = 0
        self.phase = "fade_out"
        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._overlay.fill((0, 0, 0))
        self._font = pygame.font.SysFont("Arial", 36, bold=True)

    def on_enter(self, data):
        self.target_zone = data.get("target_zone", 0)
        self.elapsed_ms = 0.0
        self.phase = "fade_out"
        self.game.raccoons_paused = True

    def on_exit(self):
        self.game.raccoons_paused = False

    def update(self, dt):
        self.elapsed_ms += dt * 1000
        half = TRANSITION_DURATION_MS / 2

        if self.phase == "fade_out" and self.elapsed_ms >= half:
            self.phase = "fade_in"
            self.elapsed_ms = 0.0

        if self.phase == "fade_in" and self.elapsed_ms >= half:
            self.game.change_state("yard", target_zone=self.target_zone)

    def draw(self, screen):
        half = TRANSITION_DURATION_MS / 2
        if self.phase == "fade_out":
            alpha = min(int(255 * self.elapsed_ms / half), 255)
        else:
            alpha = max(int(255 * (1.0 - self.elapsed_ms / half)), 0)

        self._overlay.set_alpha(alpha)
        screen.blit(self._overlay, (0, 0))

        if alpha > 150:
            zone_name = self.game.zone_manager.get_zone(self.target_zone).name
            surf = self._font.render(f"Heading to: {zone_name}...", True, (200, 200, 200))
            cx, cy = screen.get_width() // 2, screen.get_height() // 2
            screen.blit(surf, surf.get_rect(center=(cx, cy)))
