import pygame
from src.states.base_state import BaseState
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COL_WHITE, COL_GOLD


class LevelCompleteState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.font_big = pygame.font.SysFont("Arial", 68, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 34)
        self.font_small = pygame.font.SysFont("Arial", 22)
        self.is_win = False
        self.next_btn = None

    def on_enter(self, data):
        from src.systems.level_config import LEVELS
        self.is_win = self.game.level >= len(LEVELS)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.next_btn and self.next_btn.collidepoint(event.pos):
                self._advance()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._advance()

    def _advance(self):
        if self.is_win:
            self.game.change_state("menu")
        else:
            self.game.reset_level(self.game.level + 1)
            self.game.change_state("camera")

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((8, 35, 8))
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        if self.is_win:
            title = "YOU WIN!"
            title_color = (255, 230, 0)
            sub = "All raccoons photographed — the yard is safe!"
            btn_text = "MAIN MENU"
        else:
            title = f"LEVEL {self.game.level} COMPLETE!"
            title_color = COL_GOLD
            sub = f"Final score: {self.game.score} pts — Excellent work!"
            btn_text = f"NEXT: LEVEL {self.game.level + 1}"

        title_surf = self.font_big.render(title, True, title_color)
        screen.blit(title_surf, title_surf.get_rect(center=(cx, cy - 160)))

        sub_surf = self.font_med.render(sub, True, COL_WHITE)
        screen.blit(sub_surf, sub_surf.get_rect(center=(cx, cy - 90)))

        self._draw_celebration(screen, cx, cy - 10)

        btn_w, btn_h = 340, 58
        self.next_btn = pygame.Rect(cx - btn_w // 2, cy + 100, btn_w, btn_h)
        pygame.draw.rect(screen, (0, 140, 0), self.next_btn, border_radius=10)
        pygame.draw.rect(screen, COL_GOLD, self.next_btn, 3, border_radius=10)
        btn_surf = self.font_med.render(btn_text, True, COL_WHITE)
        screen.blit(btn_surf, btn_surf.get_rect(center=self.next_btn.center))

        hint = self.font_small.render("Press SPACE or click to continue", True, (130, 130, 130))
        screen.blit(hint, hint.get_rect(center=(cx, cy + 185)))

    def _draw_celebration(self, screen, cx, cy):
        r = 40
        pygame.draw.circle(screen, (90, 90, 90), (cx, cy), r)
        pygame.draw.ellipse(screen, (35, 35, 35), (cx - 30, cy - 14, 60, 22))
        er = 10
        for ex in [cx - 13, cx + 13]:
            pygame.draw.circle(screen, (255, 255, 200), (ex, cy - 4), er)
            pygame.draw.circle(screen, (0, 0, 0), (ex, cy - 4), 5)
        for ex in [cx - 26, cx + 26]:
            pygame.draw.circle(screen, (75, 75, 75), (ex, cy - r + 4), 13)
        # Stars
        for sx, sy in [(-70, -50), (70, -50), (-80, 10), (80, 10), (0, -65)]:
            pygame.draw.circle(screen, COL_GOLD, (cx + sx, cy + sy), 7)
