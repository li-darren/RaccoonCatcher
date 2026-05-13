import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
if not pygame.get_init():
    pygame.init()

from src.states.level_complete_state import LevelCompleteState
from src.systems.level_config import LEVELS
from tests.helpers import FakeGame


def _make_state(level, score=200, score_target=100):
    game = FakeGame(level=level, score=score, score_target=score_target)
    state = LevelCompleteState(game)
    state.on_enter({})
    return state, game


class TestLevelCompleteOnEnter:
    def test_not_final_level_is_not_win(self):
        state, _ = _make_state(level=1)
        assert state.is_win is False

    def test_at_final_level_is_win(self):
        final = len(LEVELS)
        state, _ = _make_state(level=final)
        assert state.is_win is True

    def test_beyond_final_level_is_win(self):
        state, _ = _make_state(level=len(LEVELS) + 1)
        assert state.is_win is True


class TestLevelCompleteAdvance:
    def test_non_final_advances_to_camera_next_level(self):
        state, game = _make_state(level=1)
        state._advance()
        assert game.last_state_change[0] == "camera"
        assert game.level == 2

    def test_final_advances_to_menu(self):
        state, game = _make_state(level=len(LEVELS))
        state._advance()
        assert game.last_state_change[0] == "menu"

    def test_non_final_increments_game_level(self):
        state, game = _make_state(level=1)
        state._advance()
        assert game.level == 2


class TestLevelCompleteHandleEvent:
    def test_space_advances(self):
        state, game = _make_state(level=1)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        state.handle_event(event)
        assert game.last_state_change is not None

    def test_click_on_button_advances(self):
        state, game = _make_state(level=1)
        # Draw to set next_btn
        screen = pygame.Surface((1280, 720))
        state.draw(screen)
        assert state.next_btn is not None
        cx, cy = state.next_btn.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(cx, cy))
        state.handle_event(event)
        assert game.last_state_change is not None

    def test_click_outside_button_does_nothing(self):
        state, game = _make_state(level=1)
        screen = pygame.Surface((1280, 720))
        state.draw(screen)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
        state.handle_event(event)
        assert game.last_state_change is None
