import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
if not pygame.get_init():
    pygame.init()

from unittest.mock import patch
from src.states.yard_state import YardState
from tests.helpers import FakeGame, FakeRaccoon, FakeRaccoonManager
from settings import YARD_PHOTO_TIME_SEC


def _make_state(raccoons=None, timer=None):
    game = FakeGame()
    if raccoons is not None:
        game.raccoon_manager = FakeRaccoonManager(raccoons)
    state = YardState(game)
    with patch("pygame.mouse.set_visible"):
        state.on_enter({"target_zone": 0})
    if timer is not None:
        state.time_remaining = timer
    return state, game


class TestYardStateOnEnter:
    def test_raccoons_populated_from_zone(self):
        r = FakeRaccoon(zone_index=0)
        state, _ = _make_state(raccoons=[r])
        assert r in state.raccoons

    def test_raccoons_from_other_zone_excluded(self):
        r = FakeRaccoon(zone_index=1)
        state, _ = _make_state(raccoons=[r])
        assert r not in state.raccoons

    def test_timer_reset_to_full(self):
        state, _ = _make_state()
        assert state.time_remaining == YARD_PHOTO_TIME_SEC

    def test_photo_not_taken(self):
        state, _ = _make_state()
        assert state.photo_taken is False

    def test_erratic_timers_match_raccoon_count(self):
        raccoons = [FakeRaccoon(zone_index=0), FakeRaccoon(zone_index=0)]
        state, _ = _make_state(raccoons=raccoons)
        assert len(state._erratic_timers) == 2

    def test_yard_vy_matches_raccoon_count(self):
        raccoons = [FakeRaccoon(zone_index=0)]
        state, _ = _make_state(raccoons=raccoons)
        assert len(state._yard_vy) == 1

    def test_set_yard_position_called_for_each_raccoon(self):
        calls = []
        r = FakeRaccoon(zone_index=0)
        r.set_yard_position_from_camera = lambda rect, dur: calls.append(True)
        state, _ = _make_state(raccoons=[r])
        assert len(calls) == 1

    def test_aiming_reset_to_false(self):
        state, _ = _make_state()
        state._aiming = True
        with patch("pygame.mouse.set_visible"):
            state.on_enter({"target_zone": 0})
        assert state._aiming is False


class TestYardStateOnExit:
    def test_aiming_reset(self):
        state, _ = _make_state()
        state._aiming = True
        with patch("pygame.mouse.set_visible"):
            state.on_exit()
        assert state._aiming is False


class TestYardStateTimeout:
    def test_timeout_triggers_result_state(self):
        state, game = _make_state(timer=0.01)
        state.update(0.02)
        assert game.last_state_change is not None
        assert game.last_state_change[0] == "result"

    def test_timeout_result_has_timeout_true(self):
        state, game = _make_state(timer=0.01)
        state.update(0.02)
        _, kwargs = game.last_state_change
        assert kwargs.get("timeout") is True

    def test_timeout_result_has_score_zero(self):
        state, game = _make_state(timer=0.01)
        state.update(0.02)
        _, kwargs = game.last_state_change
        assert kwargs.get("score") == 0

    def test_no_timeout_before_time_runs_out(self):
        state, game = _make_state(timer=5.0)
        state.update(0.016)
        assert game.last_state_change is None

    def test_time_remaining_clamps_to_zero(self):
        state, game = _make_state(timer=0.01)
        state.update(0.05)
        assert state.time_remaining == 0


class TestYardStateHandleEvent:
    def test_right_click_sets_aiming(self):
        state, _ = _make_state()
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(640, 360))
        state.handle_event(event)
        assert state._aiming is True

    def test_right_release_clears_aiming(self):
        state, _ = _make_state()
        state._aiming = True
        event = pygame.event.Event(pygame.MOUSEBUTTONUP, button=3, pos=(640, 360))
        state.handle_event(event)
        assert state._aiming is False

    def test_left_click_without_aiming_does_not_take_photo(self):
        state, _ = _make_state()
        state._aiming = False
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(640, 360))
        state.handle_event(event)
        assert state.photo_taken is False

    def test_events_ignored_after_photo_taken(self):
        state, _ = _make_state()
        state.photo_taken = True
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(640, 360))
        state.handle_event(event)
        assert state._aiming is False
