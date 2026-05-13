import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
if not pygame.get_init():
    pygame.init()

from src.states.transition_state import TransitionState
from settings import TRANSITION_DURATION_MS
from tests.helpers import FakeGame


def _make_state(target_zone=1):
    game = FakeGame()
    state = TransitionState(game)
    state.on_enter({"target_zone": target_zone})
    return state, game


class TestTransitionStateOnEnter:
    def test_pauses_raccoons(self):
        _, game = _make_state()
        assert game.raccoons_paused is True

    def test_stores_target_zone(self):
        state, _ = _make_state(target_zone=2)
        assert state.target_zone == 2

    def test_resets_elapsed(self):
        state, _ = _make_state()
        assert state.elapsed_ms == 0.0

    def test_starts_in_fade_out_phase(self):
        state, _ = _make_state()
        assert state.phase == "fade_out"


class TestTransitionStateOnExit:
    def test_unpauses_raccoons(self):
        state, game = _make_state()
        assert game.raccoons_paused is True
        state.on_exit()
        assert game.raccoons_paused is False


class TestTransitionStateUpdate:
    def test_fade_out_flips_to_fade_in_at_half(self):
        state, _ = _make_state()
        half = TRANSITION_DURATION_MS / 2
        state.update(half / 1000.0)
        assert state.phase == "fade_in"

    def test_elapsed_resets_on_phase_flip(self):
        state, _ = _make_state()
        half = TRANSITION_DURATION_MS / 2
        state.update(half / 1000.0)
        assert state.elapsed_ms < half  # reset to near 0

    def test_fade_in_triggers_yard_state_change(self):
        state, game = _make_state(target_zone=3)
        half = TRANSITION_DURATION_MS / 2
        # Complete fade_out
        state.update(half / 1000.0)
        # Complete fade_in
        state.update(half / 1000.0)
        assert game.last_state_change is not None
        assert game.last_state_change[0] == "yard"
        assert game.last_state_change[1].get("target_zone") == 3

    def test_state_change_carries_target_zone(self):
        state, game = _make_state(target_zone=2)
        half = TRANSITION_DURATION_MS / 2 / 1000.0
        # Two updates: one to complete fade_out, one to complete fade_in
        state.update(half + 0.01)
        state.update(half + 0.01)
        assert any(s[0] == "yard" for s in game._state_changes)
