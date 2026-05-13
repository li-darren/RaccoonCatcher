import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.entities.bird import Bird


def test_bird_moves_right():
    b = Bird(zone_index=0)
    b.cam_x = 0.0
    b.cam_vx = 0.2
    b.facing_right = True
    b.update(0.5)
    assert b.cam_x == 0.1


def test_bird_moves_left():
    b = Bird(zone_index=1)
    b.cam_x = 1.0
    b.cam_vx = -0.2
    b.facing_right = False
    b.update(0.5)
    assert b.cam_x == 0.9


def test_bird_wing_phase_advances():
    b = Bird(zone_index=0)
    b.wing_phase = 0.0
    b.update(0.1)
    assert b.wing_phase > 0.0


def test_bird_wing_phase_wraps():
    b = Bird(zone_index=0)
    b.wing_phase = math.tau - 0.1
    b.cam_vx = 0.0
    b.update(0.1)
    assert b.wing_phase < math.tau


def test_bird_off_screen_right():
    b = Bird(zone_index=2)
    b.cam_x = 1.19
    b.cam_vx = 0.2
    assert b.update(0.1) is True  # 1.19 + 0.02 = 1.21 > 1.2


def test_bird_off_screen_left():
    b = Bird(zone_index=3)
    b.cam_x = -0.19
    b.cam_vx = -0.2
    assert b.update(0.1) is True  # -0.19 - 0.02 = -0.21 < -0.2


def test_bird_on_screen():
    b = Bird(zone_index=0)
    b.cam_x = 0.5
    b.cam_vx = 0.1
    assert b.update(0.1) is False


def test_bird_cam_y_frac_in_sky_range():
    for _ in range(50):
        b = Bird(zone_index=0)
        assert 0.06 <= b.cam_y_frac <= 0.30


def test_bird_zone_index_preserved():
    b = Bird(zone_index=2)
    b.update(0.1)
    assert b.zone_index == 2
