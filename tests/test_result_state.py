import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
if not pygame.get_init():
    pygame.init()

from src.states.result_state import ResultState
from settings import RESULT_DISPLAY_SEC
from tests.helpers import FakeGame


def _make_state(**on_enter_data):
    game = FakeGame(timer=30.0, score=0, score_target=100)
    state = ResultState(game)
    state.on_enter(on_enter_data)
    return state, game


class TestResultStateOnEnter:
    def test_score_stored(self):
        state, _ = _make_state(score=75, timeout=False, zone_index=1)
        assert state.score == 75

    def test_timeout_stored(self):
        state, _ = _make_state(score=0, timeout=True, zone_index=0)
        assert state.timeout is True

    def test_zone_index_stored(self):
        state, _ = _make_state(score=0, timeout=False, zone_index=3)
        assert state.zone_index == 3

    def test_photo_stored(self):
        dummy_surf = pygame.Surface((10, 10))
        state, _ = _make_state(score=50, timeout=False, zone_index=0, photo=dummy_surf)
        assert state.photo is dummy_surf

    def test_photo_defaults_to_none(self):
        state, _ = _make_state(score=0, timeout=False, zone_index=0)
        assert state.photo is None

    def test_display_timer_reset(self):
        state, _ = _make_state(score=0, timeout=False, zone_index=0)
        state.display_timer = 99.0
        state.on_enter({"score": 0, "timeout": False, "zone_index": 0})
        assert state.display_timer == 0.0


class TestResultStateAdvance:
    def test_timeout_advances_to_game_over(self):
        game = FakeGame(timer=0.0, score=0, score_target=100)
        state = ResultState(game)
        state.on_enter({"score": 0, "timeout": False, "zone_index": 1})
        state._advance()
        assert game.last_state_change[0] == "game_over"

    def test_score_reached_advances_to_level_complete(self):
        game = FakeGame(timer=60.0, score=100, score_target=100)
        state = ResultState(game)
        state.on_enter({"score": 100, "timeout": False, "zone_index": 1})
        state._advance()
        assert game.last_state_change[0] == "level_complete"

    def test_normal_advances_to_camera(self):
        game = FakeGame(timer=60.0, score=30, score_target=100)
        state = ResultState(game)
        state.on_enter({"score": 30, "timeout": False, "zone_index": 2})
        state._advance()
        assert game.last_state_change[0] == "camera"
        assert game.last_state_change[1].get("exclude_zone") == 2

    def test_camera_exclude_zone_matches_zone_index(self):
        game = FakeGame(timer=60.0, score=0, score_target=100)
        state = ResultState(game)
        state.on_enter({"score": 0, "timeout": False, "zone_index": 3})
        state._advance()
        assert game.last_state_change[1]["exclude_zone"] == 3


class TestResultStateAutoAdvance:
    def test_auto_advances_after_display_time(self):
        state, game = _make_state(score=0, timeout=False, zone_index=0)
        state.update(RESULT_DISPLAY_SEC + 0.1)
        assert game.last_state_change is not None

    def test_does_not_advance_before_display_time(self):
        state, game = _make_state(score=0, timeout=False, zone_index=0)
        state.update(RESULT_DISPLAY_SEC - 0.5)
        assert game.last_state_change is None


class TestResultStateHandleEvent:
    def test_mouse_click_advances(self):
        state, game = _make_state(score=0, timeout=False, zone_index=0)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
        state.handle_event(event)
        assert game.last_state_change is not None

    def test_space_advances(self):
        state, game = _make_state(score=0, timeout=False, zone_index=0)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        state.handle_event(event)
        assert game.last_state_change is not None
