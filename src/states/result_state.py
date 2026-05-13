import pygame
from src.states.base_state import BaseState
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COL_WHITE, RESULT_DISPLAY_SEC

_POLAROID_PAD_SIDE = 14   # white border on each side + top
_POLAROID_PAD_BOTTOM = 56  # white strip at the bottom of the polaroid


class ResultState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.score = 0
        self.timeout = False
        self.zone_index = 0
        self.display_timer = 0.0
        self.photo = None
        self.font_big = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 34)
        self.font_small = pygame.font.SysFont("Arial", 22)
        self.font_caption = pygame.font.SysFont("Courier", 15)
        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def on_enter(self, data):
        self.score = data.get("score", 0)
        self.timeout = data.get("timeout", False)
        self.zone_index = data.get("zone_index", 0)
        self.photo = data.get("photo", None)
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
        self._overlay.fill((0, 0, 0, 160))
        screen.blit(self._overlay, (0, 0))

        cx = SCREEN_WIDTH // 2

        # --- Polaroid photo (only when a photo was captured) ---
        if self.photo is not None:
            pw = self.photo.get_width() + _POLAROID_PAD_SIDE * 2
            ph = self.photo.get_height() + _POLAROID_PAD_SIDE + _POLAROID_PAD_BOTTOM
            pol_x = cx - pw // 2
            pol_y = 28

            # Drop shadow
            shadow = pygame.Surface((pw + 8, ph + 8), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 90))
            screen.blit(shadow, (pol_x + 4, pol_y + 4))

            # Polaroid white background
            pygame.draw.rect(screen, (238, 236, 224), (pol_x, pol_y, pw, ph))

            # Photo image inside polaroid
            screen.blit(self.photo, (pol_x + _POLAROID_PAD_SIDE, pol_y + _POLAROID_PAD_SIDE))

            # Caption in the polaroid strip
            caption = "HIT!" if self.score > 0 else "MISSED"
            cap_col = (60, 160, 60) if self.score > 0 else (180, 60, 60)
            cap_surf = self.font_caption.render(caption, True, cap_col)
            cap_y = pol_y + _POLAROID_PAD_SIDE + self.photo.get_height() + 14
            screen.blit(cap_surf, cap_surf.get_rect(center=(cx, cap_y)))

            result_cy = pol_y + ph + 52
        else:
            result_cy = SCREEN_HEIGHT // 2

        # --- Result text ---
        if self.timeout:
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
        screen.blit(surf, surf.get_rect(center=(cx, result_cy)))

        sub_surf = self.font_med.render(sub_text, True, COL_WHITE)
        screen.blit(sub_surf, sub_surf.get_rect(center=(cx, result_cy + 68)))

        hint = self.font_small.render("Click or press SPACE to continue", True, (140, 140, 140))
        screen.blit(hint, hint.get_rect(center=(cx, result_cy + 120)))
