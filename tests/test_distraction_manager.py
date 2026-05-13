import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.systems.distraction_manager import DistractionManager
from src.entities.bird import Bird
from src.entities.leaf import Leaf


def _make_dm(num_zones=4) -> DistractionManager:
    dm = DistractionManager()
    dm.reset(num_zones)
    return dm


def test_reset_places_one_trash_bag_per_zone():
    dm = _make_dm(4)
    assert len(dm.trash_bags) == 4
    for i in range(4):
        assert len(dm.trash_bags_in_zone(i)) == 1


def test_reset_clears_birds_and_leaves():
    dm = _make_dm(4)
    dm.birds.append(Bird(0))
    dm.leaves.append(Leaf(0))
    dm.reset(4)
    assert len(dm.birds) == 0
    assert len(dm.leaves) == 0


def test_reset_replaces_trash_bags():
    dm = _make_dm(4)
    old_bags = list(dm.trash_bags)
    dm.reset(4)
    assert dm.trash_bags is not old_bags


def test_zone_filtering_birds():
    dm = _make_dm(4)
    b0 = Bird(0)
    b1a = Bird(1)
    b1b = Bird(1)
    dm.birds.extend([b0, b1a, b1b])
    assert dm.birds_in_zone(0) == [b0]
    assert set(dm.birds_in_zone(1)) == {b1a, b1b}
    assert dm.birds_in_zone(2) == []


def test_zone_filtering_leaves():
    dm = _make_dm(4)
    lf2 = Leaf(2)
    dm.leaves.append(lf2)
    assert dm.leaves_in_zone(2) == [lf2]
    assert dm.leaves_in_zone(0) == []


def test_update_removes_offscreen_bird():
    dm = _make_dm(4)
    b = Bird(0)
    b.cam_x = 1.19
    b.cam_vx = 0.5
    dm.birds.append(b)
    dm.update(0.1)  # 1.19 + 0.05 = 1.24 > 1.2
    assert b not in dm.birds


def test_update_removes_fallen_leaf():
    dm = _make_dm(4)
    lf = Leaf(1)
    lf.cam_y_frac = 1.09
    lf.cam_vy = 0.5
    lf.drift_amp = 0.0
    dm.leaves.append(lf)
    dm.update(0.1)  # 1.09 + 0.05 = 1.14 > 1.1
    assert lf not in dm.leaves


def test_update_keeps_on_screen_bird():
    dm = _make_dm(4)
    b = Bird(0)
    b.cam_x = 0.5
    b.cam_vx = 0.01
    dm.birds.append(b)
    dm.update(0.1)
    assert b in dm.birds


def test_update_keeps_falling_leaf():
    dm = _make_dm(4)
    lf = Leaf(0)
    lf.cam_y_frac = 0.5
    lf.cam_vy = 0.05
    dm.leaves.append(lf)
    dm.update(0.1)
    assert lf in dm.leaves


def test_spawn_bird_when_timer_fires():
    dm = _make_dm(4)
    dm._bird_timers[0] = 0.001
    initial_count = len(dm.birds_in_zone(0))
    dm.update(0.01)
    assert len(dm.birds_in_zone(0)) > initial_count


def test_spawn_leaf_when_timer_fires():
    dm = _make_dm(4)
    dm._leaf_timers[0] = 0.001
    initial_count = len(dm.leaves_in_zone(0))
    dm.update(0.01)
    assert len(dm.leaves_in_zone(0)) > initial_count


def test_trash_bags_not_affected_by_update():
    dm = _make_dm(4)
    original_xs = [b.cam_x for b in dm.trash_bags]
    dm.update(10.0)
    assert [b.cam_x for b in dm.trash_bags] == original_xs
