import pygame
from src.states.base_state import BaseState
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COL_WHITE, COL_GOLD


class MenuState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_sub = pygame.font.SysFont("Arial", 36)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.start_rect = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._start_game()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_rect and self.start_rect.collidepoint(event.pos):
                self._start_game()

    def _start_game(self):
        self.game.reset_level(1)
        self.game.change_state("camera")

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((10, 30, 10))

        # Title
        title_surf = self.font_title.render("RACCOON CATCHER", True, COL_GOLD)
        screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        sub_surf = self.font_sub.render("Catch those sneaky yard bandits!", True, (180, 220, 180))
        screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 210)))

        # Big raccoon decoration
        self._draw_raccoon(screen, SCREEN_WIDTH // 2, 330, 60)

        # Start button
        btn_w, btn_h = 300, 58
        self.start_rect = pygame.Rect(SCREEN_WIDTH // 2 - btn_w // 2, 430, btn_w, btn_h)
        pygame.draw.rect(screen, (0, 140, 0), self.start_rect, border_radius=10)
        pygame.draw.rect(screen, COL_GOLD, self.start_rect, 3, border_radius=10)
        btn_surf = self.font_sub.render("START GAME", True, COL_WHITE)
        screen.blit(btn_surf, btn_surf.get_rect(center=self.start_rect.center))

        hint = self.font_small.render("Press SPACE or click START", True, (130, 130, 130))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 510)))

        # How to play
        lines = [
            ("HOW TO PLAY", COL_GOLD, True),
            ("Watch the security cameras to spot raccoons in your yard.", (160, 200, 160), False),
            ("Click GO HERE! on a camera feed to rush out and photograph them.", (160, 200, 160), False),
            ("Bigger raccoons = more points.  Don't dawdle — they run!", (160, 200, 160), False),
            ("Reach the score target before time runs out to clear each level.", (160, 200, 160), False),
        ]
        y = 550
        for text, color, bold in lines:
            f = pygame.font.SysFont("Arial", 20, bold=bold)
            s = f.render(text, True, color)
            screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, y)))
            y += 30

    def _draw_raccoon(self, screen, cx, cy, r):
        pygame.draw.circle(screen, (90, 90, 90), (cx, cy), r)
        pygame.draw.ellipse(screen, (35, 35, 35), (cx - int(r * 0.75), cy - int(r * 0.3), int(r * 1.5), int(r * 0.55)))
        er = max(r // 4, 4)
        eo = r // 3
        for ex in [cx - eo, cx + eo]:
            pygame.draw.circle(screen, (255, 255, 200), (ex, cy - 4), er)
            pygame.draw.circle(screen, (0, 0, 0), (ex, cy - 4), max(er - 2, 1))
        ear_r = max(r // 3, 6)
        for ex in [cx - int(r * 0.65), cx + int(r * 0.65)]:
            pygame.draw.circle(screen, (75, 75, 75), (ex, cy - r + 4), ear_r)
            pygame.draw.circle(screen, (160, 100, 100), (ex, cy - r + 5), max(ear_r - 4, 2))
        pygame.draw.circle(screen, (20, 20, 20), (cx, cy + r // 6), max(r // 7, 3))
