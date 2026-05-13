import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
if not pygame.get_init():
    pygame.init()

from src.states.game_over_state import GameOverState
from tests.helpers import FakeGame


def _make_state(score=0, score_target=100):
    game = FakeGame(score=score, score_target=score_target)
    state = GameOverState(game)
    state.on_enter({})
    return state, game


class TestGameOverHandleEvent:
    def test_space_returns_to_menu(self):
        state, game = _make_state()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        state.handle_event(event)
        assert game.last_state_change[0] == "menu"

    def test_click_on_button_returns_to_menu(self):
        state, game = _make_state()
        screen = pygame.Surface((1280, 720))
        state.draw(screen)
        assert state.menu_btn is not None
        cx, cy = state.menu_btn.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(cx, cy))
        state.handle_event(event)
        assert game.last_state_change[0] == "menu"

    def test_click_outside_button_does_nothing(self):
        state, game = _make_state()
        screen = pygame.Surface((1280, 720))
        state.draw(screen)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
        state.handle_event(event)
        assert game.last_state_change is None

    def test_right_click_does_nothing(self):
        state, game = _make_state()
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(640, 360))
        state.handle_event(event)
        assert game.last_state_change is None

    def test_other_key_does_nothing(self):
        state, game = _make_state()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        state.handle_event(event)
        assert game.last_state_change is None


class TestGameOverUpdate:
    def test_update_does_not_change_state(self):
        state, game = _make_state()
        state.update(1.0)
        assert game.last_state_change is None
