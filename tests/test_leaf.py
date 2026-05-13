import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.entities.leaf import Leaf


def test_leaf_falls():
    lf = Leaf(zone_index=0)
    lf.cam_y_frac = 0.0
    lf.cam_vy = 0.1
    lf.drift_amp = 0.0
    lf.update(1.0)
    assert abs(lf.cam_y_frac - 0.1) < 1e-9


def test_leaf_rotation_changes():
    lf = Leaf(zone_index=0)
    lf.rotation = 0.0
    lf.rot_speed = 90.0
    lf.cam_vy = 0.0
    lf.drift_amp = 0.0
    lf.update(1.0)
    assert abs(lf.rotation - 90.0) < 1e-9


def test_leaf_rotation_wraps():
    lf = Leaf(zone_index=0)
    lf.rotation = 350.0
    lf.rot_speed = 90.0
    lf.cam_vy = 0.0
    lf.drift_amp = 0.0
    lf.update(1.0)
    assert lf.rotation < 360.0


def test_leaf_off_screen_below():
    lf = Leaf(zone_index=1)
    lf.cam_y_frac = 1.09
    lf.cam_vy = 0.2
    lf.drift_amp = 0.0
    assert lf.update(0.1) is True  # 1.09 + 0.02 = 1.11 > 1.1


def test_leaf_on_screen():
    lf = Leaf(zone_index=0)
    lf.cam_y_frac = 0.5
    lf.cam_vy = 0.05
    assert lf.update(0.1) is False


def test_leaf_initial_position_near_top():
    for _ in range(50):
        lf = Leaf(zone_index=0)
        assert -0.05 <= lf.cam_y_frac <= 0.0


def test_leaf_zone_index_preserved():
    lf = Leaf(zone_index=3)
    lf.update(0.1)
    assert lf.zone_index == 3


def test_leaf_color_is_tuple():
    lf = Leaf(zone_index=0)
    assert isinstance(lf.color, tuple)
    assert len(lf.color) == 3
