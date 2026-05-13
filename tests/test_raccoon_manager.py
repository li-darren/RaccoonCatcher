import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.entities.raccoon import Raccoon
from src.systems.raccoon_manager import RaccoonManager
from src.systems.level_config import LEVELS
from settings import NUM_ZONES


class MockGame:
    raccoons_paused = False
    level_config = LEVELS[0]


def _manager():
    return RaccoonManager(MockGame())


# ---------------------------------------------------------------------------
# populate
# ---------------------------------------------------------------------------

def test_populate_creates_correct_count():
    m = _manager()
    m.populate(LEVELS[0])
    assert len(m.raccoons) == LEVELS[0].raccoon_count


def test_populate_clears_previous_raccoons():
    m = _manager()
    m.populate(LEVELS[0])
    m.populate(LEVELS[0])
    assert len(m.raccoons) == LEVELS[0].raccoon_count


def test_populate_assigns_valid_zones():
    m = _manager()
    m.populate(LEVELS[0])
    for r in m.raccoons:
        assert 0 <= r.zone_index < NUM_ZONES


def test_populate_assigns_valid_sizes():
    m = _manager()
    valid = {"small", "medium", "large", "xl"}
    m.populate(LEVELS[0])
    for r in m.raccoons:
        assert r.size in valid


def test_populate_applies_level_scales():
    m = _manager()
    m.populate(LEVELS[2])  # highest wariness/speed scale
    for r in m.raccoons:
        from settings import RACCOON_SIZES
        base_wariness = RACCOON_SIZES[r.size]["wariness"]
        expected = min(base_wariness * LEVELS[2].wariness_scale, 0.97)
        assert abs(r.wariness - expected) < 1e-9


# ---------------------------------------------------------------------------
# raccoons_in_zone / get_raccoon_in_zone
# ---------------------------------------------------------------------------

def test_raccoons_in_zone_filters_correctly():
    m = _manager()
    m.raccoons = [Raccoon("small", 0), Raccoon("medium", 1), Raccoon("large", 0)]
    result = m.raccoons_in_zone(0)
    assert len(result) == 2
    assert all(r.zone_index == 0 for r in result)


def test_raccoons_in_zone_empty_zone():
    m = _manager()
    m.raccoons = [Raccoon("small", 1)]
    assert m.raccoons_in_zone(0) == []


def test_get_raccoon_in_zone_returns_first():
    m = _manager()
    r0 = Raccoon("small", 2)
    r1 = Raccoon("medium", 2)
    m.raccoons = [r0, r1]
    assert m.get_raccoon_in_zone(2) is r0


def test_get_raccoon_in_zone_returns_none_for_empty_zone():
    m = _manager()
    m.raccoons = [Raccoon("small", 1)]
    assert m.get_raccoon_in_zone(0) is None


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------

def test_remove_deletes_raccoon():
    m = _manager()
    r = Raccoon("small", 0)
    m.raccoons = [r]
    m.remove(r)
    assert r not in m.raccoons


def test_remove_ignores_absent_raccoon():
    m = _manager()
    r = Raccoon("small", 0)
    m.raccoons = []
    m.remove(r)  # should not raise


def test_remove_only_removes_target():
    m = _manager()
    r0 = Raccoon("small", 0)
    r1 = Raccoon("medium", 1)
    m.raccoons = [r0, r1]
    m.remove(r0)
    assert r1 in m.raccoons
    assert r0 not in m.raccoons


# ---------------------------------------------------------------------------
# update — pausing
# ---------------------------------------------------------------------------

def test_update_paused_does_not_move_raccoon():
    game = MockGame()
    game.raccoons_paused = True
    m = RaccoonManager(game)
    r = Raccoon("small", 0)
    r._entering = False
    r._hopping = False
    r.cam_x = 0.5
    r.cam_vx = 0.2
    m.raccoons = [r]
    m.update(1.0)
    assert r.cam_x == 0.5


def test_update_unpaused_moves_raccoon():
    game = MockGame()
    game.raccoons_paused = False
    m = RaccoonManager(game)
    r = Raccoon("small", 0)
    r._entering = False
    r._hopping = False
    r._dir_timer = 999.0
    r.cam_x = 0.5
    r.cam_vx = 0.2
    m.raccoons = [r]
    m.update(1.0)
    assert r.cam_x != 0.5


# ---------------------------------------------------------------------------
# respawn_if_needed
# ---------------------------------------------------------------------------

def test_respawn_fills_to_raccoon_count():
    m = _manager()
    m.raccoons = []
    m.respawn_if_needed()
    assert len(m.raccoons) == LEVELS[0].raccoon_count


def test_respawn_no_op_when_already_full():
    m = _manager()
    m.populate(LEVELS[0])
    original = list(m.raccoons)
    m.respawn_if_needed()
    assert m.raccoons == original


def test_respawn_excludes_specified_zone():
    m = _manager()
    m.raccoons = []
    # Respawn many times to confirm the excluded zone is never used
    for _ in range(30):
        m.raccoons.clear()
        m.respawn_if_needed(exclude_zone=2)
        for r in m.raccoons:
            assert r.zone_index != 2


def test_respawn_spawned_raccoon_in_valid_zone():
    m = _manager()
    m.raccoons = []
    m.respawn_if_needed()
    for r in m.raccoons:
        assert 0 <= r.zone_index < NUM_ZONES
