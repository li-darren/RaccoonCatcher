import pygame
from settings import SCREEN_WIDTH, HUD_BAR_H, COL_WHITE, COL_GOLD


class HUD:
    def __init__(self):
        self.font_large = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 16)

    def draw_camera_hud(self, screen, score: int, timer_sec: float, level: int, target: int):
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_BAR_H)
        pygame.draw.rect(screen, (8, 22, 8), bar_rect)
        pygame.draw.line(screen, (0, 170, 0), (0, HUD_BAR_H - 1), (SCREEN_WIDTH, HUD_BAR_H - 1), 2)

        lv_surf = self.font_large.render(f"LEVEL {level}", True, COL_GOLD)
        screen.blit(lv_surf, (18, (HUD_BAR_H - lv_surf.get_height()) // 2))

        score_surf = self.font_large.render(f"SCORE: {score} / {target}", True, COL_WHITE)
        screen.blit(score_surf, score_surf.get_rect(
            center=(SCREEN_WIDTH // 2, HUD_BAR_H // 2)))

        mins = int(timer_sec) // 60
        secs = int(timer_sec) % 60
        timer_color = (255, 70, 70) if timer_sec < 30 else COL_WHITE
        timer_surf = self.font_large.render(f"TIME: {mins:02d}:{secs:02d}", True, timer_color)
        screen.blit(timer_surf, (SCREEN_WIDTH - timer_surf.get_width() - 18,
                                  (HUD_BAR_H - timer_surf.get_height()) // 2))

    def draw_yard_hud(self, screen, timer_sec: float, zone_name: str):
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_BAR_H)
        pygame.draw.rect(screen, (8, 8, 28), bar_rect)
        pygame.draw.line(screen, (100, 100, 200), (0, HUD_BAR_H - 1), (SCREEN_WIDTH, HUD_BAR_H - 1), 2)

        z_surf = self.font_large.render(f"Photographing: {zone_name}", True, COL_GOLD)
        screen.blit(z_surf, (18, (HUD_BAR_H - z_surf.get_height()) // 2))

        # Photo timer bar
        bar_total = 280
        ratio = max(timer_sec / 6.0, 0.0)
        bar_filled = int(bar_total * ratio)
        bx = SCREEN_WIDTH // 2 + 20
        by = (HUD_BAR_H - 18) // 2
        pygame.draw.rect(screen, (35, 35, 35), (bx, by, bar_total, 18), border_radius=5)
        if bar_filled > 0:
            color = (70, 190, 70) if timer_sec > 3 else (200, 70, 70)
            pygame.draw.rect(screen, color, (bx, by, bar_filled, 18), border_radius=5)
        pygame.draw.rect(screen, (160, 160, 160), (bx, by, bar_total, 18), 2, border_radius=5)

        hint = self.font_small.render("Click to photograph!", True, (180, 180, 255))
        screen.blit(hint, (SCREEN_WIDTH - hint.get_width() - 18,
                           (HUD_BAR_H - hint.get_height()) // 2))
