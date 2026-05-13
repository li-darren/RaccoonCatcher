import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
if not pygame.get_init():
    pygame.init()

from unittest.mock import patch, MagicMock
from src.states.camera_state import CameraState
from tests.helpers import FakeGame


def _make_state(score=0, timer=180.0, score_target=100):
    game = FakeGame(score=score, timer=timer, score_target=score_target)
    state = CameraState(game)
    with patch("src.states.camera_state.CameraFeed"):
        state.on_enter({})
    return state, game


class TestCameraStateUpdate:
    def test_timer_decrements(self):
        state, game = _make_state(timer=10.0)
        state.update(0.5)
        assert game.timer_remaining == 9.5

    def test_timer_at_zero_triggers_game_over(self):
        state, game = _make_state(timer=0.1)
        state.update(0.2)
        assert game.last_state_change[0] == "game_over"

    def test_timer_clamps_to_zero(self):
        state, game = _make_state(timer=0.1)
        state.update(0.2)
        assert game.timer_remaining == 0

    def test_score_target_reached_triggers_level_complete(self):
        state, game = _make_state(score=100, score_target=100)
        state.update(0.016)
        assert game.last_state_change[0] == "level_complete"

    def test_score_exceeded_triggers_level_complete(self):
        state, game = _make_state(score=200, score_target=100)
        state.update(0.016)
        assert game.last_state_change[0] == "level_complete"

    def test_normal_update_no_state_change(self):
        state, game = _make_state(score=0, timer=60.0, score_target=100)
        state.update(0.016)
        assert game.last_state_change is None

    def test_raccoons_paused_set_false_on_enter(self):
        game = FakeGame()
        game.raccoons_paused = True
        state = CameraState(game)
        with patch("src.states.camera_state.CameraFeed"):
            state.on_enter({})
        assert game.raccoons_paused is False


class TestCameraStateOnEnter:
    def test_exclude_zone_passed_to_respawn(self):
        game = FakeGame()
        calls = []
        game.raccoon_manager.respawn_if_needed = lambda exclude_zone: calls.append(exclude_zone)
        state = CameraState(game)
        with patch("src.states.camera_state.CameraFeed"):
            state.on_enter({"exclude_zone": 2})
        assert calls == [2]

    def test_no_exclude_zone_defaults_to_minus_one(self):
        game = FakeGame()
        calls = []
        game.raccoon_manager.respawn_if_needed = lambda exclude_zone: calls.append(exclude_zone)
        state = CameraState(game)
        with patch("src.states.camera_state.CameraFeed"):
            state.on_enter({})
        assert calls == [-1]


class TestCameraStateHandleEvent:
    def test_left_click_on_door_button_triggers_transition(self):
        game = FakeGame()
        state = CameraState(game)

        mock_feed = MagicMock()
        import pygame as pg
        mock_feed.get_door_button_rect.return_value = pg.Rect(50, 50, 100, 30)
        state.feeds = [mock_feed]

        event = pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=(75, 65))
        state.handle_event(event)

        assert game.last_state_change is not None
        assert game.last_state_change[0] == "transition"

    def test_left_click_outside_door_does_nothing(self):
        game = FakeGame()
        state = CameraState(game)

        mock_feed = MagicMock()
        import pygame as pg
        mock_feed.get_door_button_rect.return_value = pg.Rect(50, 50, 100, 30)
        state.feeds = [mock_feed]

        event = pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=(200, 200))
        state.handle_event(event)

        assert game.last_state_change is None
