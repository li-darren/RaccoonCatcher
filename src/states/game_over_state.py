import pygame
from src.states.base_state import BaseState
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COL_WHITE


class GameOverState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.font_big = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 34)
        self.font_small = pygame.font.SysFont("Arial", 22)
        self.menu_btn = None

    def on_enter(self, data):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_btn and self.menu_btn.collidepoint(event.pos):
                self.game.change_state("menu")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.change_state("menu")

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((28, 8, 8))
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        title_surf = self.font_big.render("TIME'S UP!", True, (255, 80, 80))
        screen.blit(title_surf, title_surf.get_rect(center=(cx, cy - 130)))

        needed = max(self.game.level_config.score_target - self.game.score, 0)
        sub = f"You needed {needed} more points.  Final score: {self.game.score}"
        sub_surf = self.font_med.render(sub, True, COL_WHITE)
        screen.blit(sub_surf, sub_surf.get_rect(center=(cx, cy - 60)))

        tip = self.font_med.render("The raccoons escaped into the night...", True, (180, 140, 140))
        screen.blit(tip, tip.get_rect(center=(cx, cy)))

        btn_w, btn_h = 280, 58
        self.menu_btn = pygame.Rect(cx - btn_w // 2, cy + 70, btn_w, btn_h)
        pygame.draw.rect(screen, (140, 25, 25), self.menu_btn, border_radius=10)
        pygame.draw.rect(screen, (255, 100, 100), self.menu_btn, 3, border_radius=10)
        btn_surf = self.font_med.render("TRY AGAIN", True, COL_WHITE)
        screen.blit(btn_surf, btn_surf.get_rect(center=self.menu_btn.center))

        hint = self.font_small.render("Press SPACE or click to return to menu", True, (110, 110, 110))
        screen.blit(hint, hint.get_rect(center=(cx, cy + 170)))
